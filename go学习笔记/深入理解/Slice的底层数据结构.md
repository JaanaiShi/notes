## Slice的底层数据结构

### slice的定义

```go
type slice struct {
    arrray unsafe.Pointer
    len int
    cap int
}
```

Slice的底层数据结构共分为三部分，如下

* array：指向所引用的数组指针（`unsafe.Pointer`可以表示任何可寻址的值的指针）
* len：长度，当前引用切片的元素个数
* cap：容量，当前引用切片的容量（底层数组的元素总数）

在实际使用中，cap一定是大于或等于len的，否则会导致panic

```go
func main() {
    nums := [3]int{}    
    nums[0] = 1

    dnums := nums[0:2]      // 这段代码确定了Slice的Pointer指向数组，且len和cap都为数组的基础属性。

    fmt.Printf("dnums: %v, len: %d, cap: %d", dnums, len(dnums), cap(dnums))
}
```

### slice的创建

Slice的创建有两种方式，如下

* `var []T`或`[]T{}`
* `func make ([]T, len, cap)[]T`

Q：因为slice需要指向一个Array。那么make是怎么做到的呢？

A：它会在调用make的时候，分配一个数组并返回引用该数组的slice

```go
func makeslice(et *_type, len, cap int) slice {
    maxElements := maxSliceCap(et.size)
    if len < 0 || uintptr(len) > maxElements {
        panic(errorString("makeslice: len out of range"))
    }

    if cap < len || uintptr(cap) > maxElements {
        panic(errorString("makeslice: cap out of range"))
    }

    p := mallocgc(et.size*uintptr(cap), et, true)
    return slice{p, len, cap}
}
```

* 根据传入的slice类型，获取其类型能够申请的最大容量大小
* 判断len是否合规，检查是否在0 < x <maxElements范围内
* 判断cap是否合规，检查是否在len < x < maxElements范围内
* 申请Slice所需的内存空间对象。若为大型对象（大于32KB）则直接从堆中分配
* 返回申请成功的Slice内存地址和相关属性（默认返回申请到的内存起始地址）

### Slice的扩容

当使用Slice时，若存储的元素不断增长（例如通过append）。当条件满足扩容的策略时，将会触发自动扩容。

#### zerobase

```go
func growslice(et *_type, old slice, cap int) slice {
    ...
    if et.size == 0 {
        if cap < old.cap {
            panic(errorString("growslice: cap out of range"))
        }

        return slice{unsafe.Pointer(&zerobase), old.len, cap}
    }
    ...
}
/*
	当Slice size为0时，若将要扩容的容量比原本的容量小，则抛出异常（也就是不支持缩容操作）。否则，将重新生成一个新的Slice返回，其Pointer指向一个0 byte地址（不会保留老的Array指向）
*/
```

#### 扩容 - 计算策略

```go
func growslice(et *_type, old slice, cap int) slice {  
    // 第一个参数为 ， 第二参数为：旧的Slice， 第三个参数为：要扩容的容量
    ...
    newcap := old.cap
    doublecap := newcap + newcap
    if cap > doublecap {
        newcap = cap
    } else {
        if old.len < 1024 {
            newcap = doublecap
        } else {
            for 0 < newcap && newcap < cap {
                newcap += newcap / 4
            }
            ...
        }
    }
    ...
}
```

* 若Slice cap大于doublecap，则扩容后容量大小为新Slice的容量（超了基准值，我就只给你需要的容量大小）
* 若Slice len小于1024个，在扩容时，增长因子为1（也就是3个变为6个）
* 若slice len大于1024个，在扩容时，增长因子为0.25（增长原本容量的四分之一）

> 注：也就是小于1024个，增长2倍。大于1024个时，增长1.25倍

#### 扩容 - 内存策略

```go
func growslice(et *_type, old slice, cap int) slice {
    ...
    var overflow bool
    var lenmem, newlenmem, capmem uintptr
    const ptrSize = unsafe.Sizeof((*byte)(nil))
    switch et.size {
    case 1:
        lenmem = uintptr(old.len)
        newlenmem = uintptr(cap)
        capmem = roundupsize(uintptr(newcap))
        overflow = uintptr(newcap) > _MaxMem
        newcap = int(capmem)
        ...
    }

    if cap < old.cap || overflow || capmem > _MaxMem {
        panic(errorString("growslice: cap out of range"))
    }

    var p unsafe.Pointer
    if et.kind&kindNoPointers != 0 {
        p = mallocgc(capmem, nil, false)
        memmove(p, old.array, lenmem)
        memclrNoHeapPointers(add(p, newlenmem), capmem-newlenmem)
    } else {
        p = mallocgc(capmem, et, true)
        if !writeBarrier.enabled {
            memmove(p, old.array, lenmem)
        } else {
            for i := uintptr(0); i < lenmem; i += et.size {
                typedmemmove(et, add(p, i), add(old.array, i))
            }
        }
    }
    ...
}
```

扩容时的内存管理的选择项：

* 翻新扩展：当前元素为`kindNoPointers`，将在老Slice cap的地址后继续申请空间用于扩容
* 举家搬迁：重新申请一块内存地址，整体迁移并扩容

### 两个小“陷阱”

### 一、同根

```go
func main() {
    nums := [3]int{}
    nums[0] = 1

    fmt.Printf("nums: %v , len: %d, cap: %d\n", nums, len(nums), cap(nums))

    dnums := nums[0:2]
    dnums[0] = 5

    fmt.Printf("nums: %v ,len: %d, cap: %d\n", nums, len(nums), cap(nums))
    fmt.Printf("dnums: %v, len: %d, cap: %d\n", dnums, len(dnums), cap(dnums))
}
```

输出结果为

```go
$ go run 2.\ Slice学习.go
nums: [1 0 0] , len: 3, cap: 3
nums: [5 0 0] ,len: 3, cap: 3
dnums: [5 0], len: 2, cap: 3
```

在未扩容前，Slice array指向所引用的Array。因此在Slice上的变更。会直接修改到原始Array上（二者所引用的是同一个）

#### 二、时过境迁

随着Slice不断append，内在的元素越来越多，终于触发了扩容。如下代码

```go
func main() {
	nums := [3]int{}
	nums[0] = 1

	fmt.Printf("nums: %v , len: %d, cap: %d\n", nums, len(nums), cap(nums))

	dnums := nums[0:2]
	dnums = append(dnums, []int{2,3}...)
	dnums[0] = 5

	fmt.Printf("nums: %v ,len: %d, cap: %d\n", nums, len(nums), cap(nums))
	fmt.Printf("dnums: %v, len: %d, cap: %d\n", dnums, len(dnums), cap(dnums))
}
```

输出结果：

```go
$ go run 2.\ Slice学习.go
nums: [1 0 0] , len: 3, cap: 3
nums: [1 0 0] ,len: 3, cap: 3
dnums: [5 0 2 3], len: 4, cap: 6
```

往Slice append元素时，若满足扩容策略，也就是假设插入后，原本数组的容量就超过了最大值了

这时候内部就会重新申请一块内存空间，将原本的元素拷贝一份到新的内存空间上。此时其与原本的数组就没有任何关联了，再进行修改值也不会变动到原始数组。

### Slice的复制

#### 原型

```go
func copy(dst, src [] T) int
```

copy函数将数据从源Slice复制到目标Slice。它返回复制的元素数

示例：

```go
func main() {
	nums := [3]int{}
	nums[0] = 1

	fmt.Printf("nums: %v , len: %d, cap: %d\n", nums, len(nums), cap(nums))

	dnums := nums[0:2]
	dst := []int{1,2}
	copyn := copy(dst, dnums)

	fmt.Printf("dst: %v, n: %d\n", dst, copyn)
	fmt.Printf("dnums: %v, len: %d, cap: %d\n", dnums, len(dnums), cap(dnums))
}
```

输出结果

```go
$ go run 2.\ Slice学习.go
nums: [1 0 0] , len: 3, cap: 3
dst: [1 0], n: 2
dnums: [1 0], len: 2, cap: 3
```

copy函数支持在不同长度的Slice之间的进行复制，若出现长度不一致，在复制时会按照最少的Slice元素个数进行复制。

#### 复制的源码

```go
func slicecopy(to, fm slice, width uintptr) int {
    if fm.len == 0 || to.len == 0 {
        return 0
    }

    n := fm.len
    if to.len < n {
        n = to.len
    }

    if width == 0 {
        return n
    }

    ...

    size := uintptr(n) * width
    if size == 1 {
        *(*byte)(to.array) = *(*byte)(fm.array) // known to be a byte pointer
    } else {
        memmove(to.array, fm.array, size)
    }
    return n
}
```

* 若源Slice或目标Slice存在长度为0的情况，则直接返回0（因为不需要执行复制行为）
* 通过对比两个Slice，获取最小的Slice长度。便于后续操作
* 若Slice只有一个元素，则直接利用指针的特性进行转换
* 若Slice大于一个元素，则从`fm.array`复制`size`个字节到`to.array`的地址处

### 奇特的初始化

在Slice中流传着两个传说，分别为Empty和Nil Slice，则它们有什么区别呢

```go
func main() {
	// Empty
	 s := make([]int, 0)  // 或者写成s := []int{}

	fmt.Printf("s: %v, len: %d, cap: %d\n", s, len(s), cap(s))
	// Nil 
	var t []int
	fmt.Printf("t: %v, len: %d, cap: %d\n", t, len(t), cap(t))
}
```

输出结果

```go
$ go run 2.\ Slice学习.go
s: [], len: 0, cap: 0
t: [], len: 0, cap: 0
```

通过示例我们发现Empty slice和Nil Slice好像一模一样？不管是len，还是cap都为0。

区别

```go
func main() {
    var nums []int
    renums := make([]int, 0)
    if nums == nil {
        fmt.Println("nums is nil.")
    }
    if renums == nil {
        fmt.Println("renums is nil.")
    }
}
```

其实二者存在本质上的区别。其底层数组的指向指针是不一样的，Nil Slice指向的是nil，Empty Slice指向的是实际存在的空数组地址。

也可以这样认为，Nil Slice代指不存在的Slice，Empty Slice代指空集合。两者所代表的意义是完全不同的。

### 编程Tips

* 创建切片时可根据实际需要预分配容量，尽量避免追加过程中的扩容操作，有利于提升性能
* 切片拷贝时需要判断实际拷贝的元素个数
* 谨慎使用多个切片操作同一个数组，以防读写冲突

### Slice总结

* 每个切片都指向一个底层数组
* 每个切片都保存了当前切片的长度，底层数组可用容量
* 使用len()计算切片长度时间复杂度为O(1)，不需要遍历切片
* 使用cap()计算切片容量时间复杂度为O(1)，不需要遍历切片
* 通过函数传递切片时，不会拷贝整个切片，因为切片本身只是个结构体而已
* 使用append()向切片追加元素时有可能触发扩容，扩容后将会生成新的切片。

https://www.cnblogs.com/xbhog/p/15213838.html
