## string的底层原理

### string的标准概念

string是8比特字节的集合，通常是但不一定非得是UTF-8编码的文本

* string可以为空（长度为0），但不会是nil；
* string对象不可以修改

### string的数据结构

string的数据结构

```go
type stringStruct struct {
    str unsafe.Pointer
    len int
}
```

其数据结构很简单：

* stringStruct.str：字符串的首地址
* stringStruct.len：字符串的长度；

### string的操作

#### 声明

如下代码所示，可以声明一个string变量赋予初值

```go
var str string
str = "Hello World"
```

字符串构建过程是先根据字符串构建stringStruct，再转换成string。转换的源码如下：

```go
func gostringnocopy(str *byte) string { // 根据字符串地址构建string
    ss := stringStruct{str: unsafe.Pointer(str), len: findnull(str)} // 先构造stringStruct
    s := *(*string)(unsafe.Pointer(&ss))                             // 再将stringStruct转换成string
    return s
}
// string在runtime包中就是stringStruct，对外呈现叫做string
```

#### []byte转string

byte切片可以很方便地转换成string， 如下所示

```go
func GetStringBySlice(s []byte) string {
    return string(s)
}
```

需要注意的是这种转换需要一次内存拷贝。

转换过程如下：

1. 根据切片的长度申请内存空间，假设内存地址为p，切片长度为len(b);
2. 构建string（`string.str = p; string.len = len;`）
3. 拷贝数据（切片中数据拷贝到新申请的内存空间）

转换示意图：

![image-20210816145539808](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20210816145539808.png)

#### string转[]byte

string也可以方便地转成byte切片，如下所示：

```go
func GetSliceByString(str string) []byte {
    return []byte(str)
}
```

string转换成byte切片，也需要一次内存拷贝，其过程如下：

* 申请切片内存空间
* 将string拷贝到切片

转换示意图：

![image-20210816145834385](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20210816145834385.png)

#### 字符串的拼接

字符串可以很方便的拼接，像下面这样：

```go
str := "str1" + "str2" + "str3"
```

即便有非常多的字符串需要拼接，性能上也有比较好的保证，因为新字符串的内存空间是一次分配完成的，所以性能消耗主要在拷贝数据上。

一个拼接语句的字符串编译时都会被存放到一个切片中，拼接过程需要遍历两次切片，第一次遍历获取总的字符串长度，据此申请内存，第二次遍历会把字符串逐个拷贝过去。

#### 为什么字符串不允许修改？

在Go语言的实现中，string不包含内存空间，只有一个内存的指针，这样做的好处是string变得非常轻量，可以很方便地进行传递而不用担心内存拷贝。

因为string通常指向字符串字面量，而字符串字面量存储位置是只读段，而不是堆或栈上，所以才有了string不可修改的约定。

#### []byte转换成string一定会拷贝内存吗？

byte切片转换成string的场景很多，为了性能上的考虑，有时候只是临时需要字符串的场景下，byte切片转换成string时并不会拷贝内存，而是直接返回一个string，这个string的指针（string.str）指向切片的内存。

#### string和[]byte如何取舍

string和[]byte都可以表示字符串，但因数据结构不同，其衍生出来的方法也不相同，要根据实际应用场景来选择。

string擅长的场景：

* 需要字符串比较的场景
* 不需要nil字符串的场景

[]byte擅长的场景：

* 修改字符串的场景，尤其是修改粒度为1个字节；
* 函数返回值，需要用nil表示含义的场景
* 需要切片操作的场景；

需求1：遍历字符串

对于初学者，面对此需求，肯定是一个大问好（字符串还可以遍历），当百度一下一看竟然有两种遍历方式，对此更加疑惑了，再往下探索，发现一种是下标遍历，一种是range遍历。头越来越大……

对此，我们只能靠代码说话了，先尝试一下

### 下标遍历

```go
func main() {
	str := "hello 世界"
    l := len(str)
	fmt.Println("str的长度是：", l)
	for i := 0; i < len(str); i++ {
		fmt.Printf("%d = %c = %d  \n", i, str[i], str[i])
	}
}

// output
$ go run 3.\ 字符串的遍历.go
str的长度是： 12
0 = h = 104
1 = e = 101
2 = l = 108
3 = l = 108
4 = o = 111
5 =   = 32
6 = ä = 228
7 = ¸ = 184
9 = ç = 231
10 =   = 149
11 =   = 140
......
```

这时，我们会发现下标为6，7，9的是什么鬼了。然后查看字符串的内容，发现这可能是汉字的乱码。

为什么会出现这种情况呢？对其继续深究，发现len()函数会将字符串的字节总数统计出来，这时灵光一闪，想到了一个英文字母和一个汉字的所占的字节是不一样的。

> 需要了解的是Go语言中使用的是utf-8的编码方式。
>
> utf-8采用的是变长编码方式，1-4字节表示一个字符，可节省存储空间；其中英文1个字节，中文一般3字节，最多4字节。

有了这个知识我们就理解了，为什么汉字那块会出现乱码，因为汉字的编码一般是3个，超出了单字节的编码，所以会出现乱码

### range遍历

```go
func main() {
	str := "hello 世界"
	for index, c := range str {
		fmt.Printf("%d  %c  %d\n", index, c, c)
	}
}

// output
$ go run 3.\ 字符串的遍历.go
0  h  104
1  e  101
2  l  108
3  l  108
4  o  111
5     32
6  世  19990
9  界  30028
```

这就是我们想要的结果，好了，满足需求，打游戏了……

……………………………………………………………………………………

为什么使用range会出现这种情况呢， 等等我们发现下标从6直接到9了，经过前面的铺垫，是因为一个中文字符占3个字节。

很明显得情况就是，range遍历是按照字符进行遍历的。我们可以分析其类型

```go
func main() {
	str := "hello 世界"
	for index, c := range str {
		fmt.Printf("%d %T\n", index, c)
	}
}

// output
$ go run 3.\ 字符串的遍历.go
0 int32
1 int32
2 int32
3 int32
4 int32
5 int32
6 int32
9 int32
```

而int32类型不就是rune类型吗，这样我们就可以正常输出了。





