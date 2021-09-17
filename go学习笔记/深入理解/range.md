### 1. range

range是Golang提供的一种迭代遍历手段，可操作的类型有数组、切片、Map、channel等，实际使用频率非常高

### 2. 有关range的题目

#### 2.1 切片遍历

下面函数通过遍历切片，打印切片的下标和元素值，请问性能上有没有可优化的空间？

```go
func RangeSlice(slice []int) {
    for index, value := range slice {
        _, _ = index, value
    }
}
```

参考答案：

遍历过程中每次迭代会对index和value进行赋值，如果数据量大或者value类型为string时，对value的赋值操作可能是多余的，可以在for-range中忽略value值，使用slice[index]引用value值。

#### 2.2 Map遍历

下面函数通过遍历Map，打印Map的key和value，请问性能上有没有可优化的空间？

```go
func RangeMap(myMap map[int]string) {
    for key, _ := range myMap {
        _, _ = key, myMap[key]
    }
}
```

参考答案：
函数中for-range语句中只获取key值，然后根据key值获取value值，虽然看似减少了一次赋值，但通过key值查找value值的性能消耗可能高于赋值消耗。能否优化取决于map所存储数据结构特征、结合实际情况进行。

#### 2.3 动态遍历

请问如下程序是否能正常结束？

```go
func main() {
    v := []int{1, 2, 3}
    for i:= range v {
        v = append(v, i)
    }
}
// slice会自动扩容的
```

程序解释：

main()函数中定义一个切片v，通过range遍历v，遍历过程中不断向v中添加新的元素。

参考答案：

能够正常结束。循环内改变切片的长度，不影响循环次数，循环次数在循环开始前就已经确定了。

### 3. 实现原理

对于for-range语句的实现，可以从编译器源码中找到答案

```go
// Arrange to do a loop appropriate for the type.  We will produce
//   for INIT ; COND ; POST {
//           ITER_INIT
//           INDEX = INDEX_TEMP
//           VALUE = VALUE_TEMP // If there is a value
//           original statements
//   }
```

可见range实际上是一个C风格的循环结构。range支持数组、数组指针、切片、map和channel类型，对于不同类型有些细节上的差异

#### 3.1 range for slice

```go
// The loop we generate:
//   for_temp := range
//   len_temp := len(for_temp)
//   for index_temp = 0; index_temp < len_temp; index_temp++ {
//           value_temp = for_temp[index_temp]
//           index = index_temp
//           value = value_temp
//           original body
//   }
```

遍历slice前会先获取slice的长度len_temp作为循环次数，循环体中，每次循环会先获取元素值，如果for-range中接收index和value的话，则会对index和value进行一次赋值。

由于循环开始前循环次数就已经确定了，所以循环过程中新添加的元素时没办法遍历到的。

#### 3.2 range for map

```go
// The loop we generate:
//   var hiter map_iteration_struct
//   for mapiterinit(type, range, &hiter); hiter.key != nil; mapiternext(&hiter) {
//           index_temp = *hiter.key
//           value_temp = *hiter.val
//           index = index_temp
//           value = value_temp
//           original body
//   }
```

遍历map时没有指定循环次数，循环体与遍历slice类似。由于map底层实现与slice不同，map底层使用hash表实现，插入数据位置是随机的，所以遍历过程中新插入的数据不能保证遍历到。

#### 3.3 range for channel

遍历channel是最特殊的，这是由channel的实现机制决定的：

```go
// The loop we generate:
//   for {
//           value_temp, ok_temp = <-range
//           if !ok_temp {
//                   break
//           }
//           value = value_temp
//           original body
//   }
```

channel遍历时依次从channel中读取数据，读取前是不知道里面有多少个元素的。如果channel中没有元素，则会阻塞等待，如果channel已被关闭，则会解除阻塞并退出循环。

### 4. 编程Tips

* 遍历过程中可以视情况放弃接收index或value，可以一定程度上提升性能
* 遍历channel时，如果channel中没有数据，可能会阻塞
* 尽量避免遍历过程中修改原数据。

### 5. 总结

* for-range的实现实际上是C风格的for循环
* 使用inde, value接收range返回值会发生一次数据拷贝