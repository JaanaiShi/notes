## fmt

### 1.1 向外输出

标准库fmt提供了几种输出相关函数

#### Print

Print系列函数会将内容输出到系统的标准输出，区别在于Print函数直接输出内容，Printf函数支持格式化输出字符串，Println函数会在输出内容的结尾添加一个换行符

```go
func Print(a ...interface{}) (n int, err error)
func Printf(format string, a ...interface{}) (n int, err error)
func Println(a ...interface{}) (n int, err error)
```

示例：

```go
func main() {
	fmt.Print("在终端打印该信息")
	name := "枯藤"
	fmt.Printf("我是%s\n", name)
	fmt.Println("大家好")
}
```

#### Fprint

Fprint系列函数会将内容输出到一个io.Writer()接口类型的变量w中，我们

```go
func Fprint(w io.Writer, a ...interface{}) (n int, err error)
func Fprintf(w io.Writer, format string, a ...interface{}) (n int, err error)
func Fprintln(w io.Writer, a ...interface{}) (n int, err error)
```

示例：

```go
func main() {
	// 向标准输出写入内容
	fmt.Fprintln(os.Stdout, "向标准输出写入内容")
	fileObj, err := os.OpenFile("./xx.text", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		fmt.Println("打开文件出错，err:", err)
		return
	}
	name := "活火石"
	fmt.Println(fileObj)
	// 向打开的文件句柄中写入内容
	fmt.Fprintf(fileObj, "往文件中写入信息： %s", name)
}
```

在此解释一下文件句柄和文件描述符

文件描述符：

本质上是一个索引号（非负整数），系统用户层可以根据它找到系统内核层的文件数据。这是一个POSIX标准下的概念，常见于Linux系统。

文件句柄：

Windows下的概念。句柄是Windows下各种对象的标识符，比如文件、资源、菜单、光标等等。文件句柄和文件描述符类似，它也是一个非负整数，也用于定位文件数据在内存中的位置。

因为在Linux中所有的东西都被看成文件，所以Linux下的文件描述符其实就是相当于Windows下的句柄。

#### Sprint

Sprint系列函数会把传入的数据生成并**返回一个字符串**。

```go
func Sprint(a ...interface{}) string
func Sprintf(format string, a ...interface{}) string
func Sprintln(a ...interface{}) string
```

示例：

```go
	s1 := fmt.Sprint("枯藤")
	name := "枯藤"
	age := 18
	s2 := fmt.Sprintf("name:%s, age:%d\n", name, age)
	s3 := fmt.Sprintln("枯藤")
	fmt.Println(s1, s2, s3)
```

#### Errorf

Errorf函数根据format参数生成格式化字符串并返回一个包含该字符串的错误。

```go
func Errorf(format string, a ...interface{}) error
```

### 1.2 格式化占位符

`*printf`系列函数都支持format格式化参数

#### 通用占位符

| 占位符 |                说明                |
| :----: | :--------------------------------: |
|   %v   |          值得默认格式表示          |
|  %+v   | 类似%v，但输出结构体时会添加字段名 |
|  %#v   |           值的Go语法表示           |
|   %T   |            打印值的类型            |
|   %%   |               百分号               |

#### 布尔型

| 占位符 | 说明        |
| ------ | ----------- |
| %t     | true或false |

#### 整型

| 占位符 | 说明       |
| ------ | ---------- |
| %b     | 表示二进制 |
|        |            |
|        |            |

#### 指针

| 占位符 | 说明                           |
| ------ | ------------------------------ |
| %p     | 表示为十六进制，并加上前导的ox |

### 1.3 获取输入

Go语言fmt包下有fmt.Scan、fmt.Scanf、fmt.Scanln三个函数，可以在程序运行过程中从标准输入获取用户的输入

#### fmt.Scan

函数定签名如下：

```go
func Scan(a ...interface{}) (n int, err error)
```

* Scan从标准输入扫描文本，读取由空白符分隔的值保存到传递给本函数的参数中，换行符视为空白符。
* 本函数返回成功扫描的数据个数和遇到的任何错误。如果读取的数据个数比提供的参数少，会返回一个错误报告原因。

示例：

```go
func main() {
	var (
		name string
		age int
		married bool
	)

	fmt.Scan(&name, &age, &married)
	fmt.Printf("扫描结果 name:%s age:%d married:%t\n", name, age, married)
}
```

结果：

```go
$ go run 1.\ Buttle\ Sort.go
lisi 12 false
扫描结果 name:lisi age:12 married:false

$ go run 1.\ Buttle\ Sort.go
lisi 18 fou
扫描结果 name:lisi age:18 married:false

// 不知道为什么会出现这种情况
$ go run 1.\ Buttle\ Sort.go   
lisi 12
扫描结果 name:u age:0 married:false    

$ go run 1.\ Buttle\ Sort.go
lisi 29 true
扫描结果 name:lisi age:29 married:true

```

#### fmt.Scanf

函数签名：

```go
func Scanf(format string, a ...interface{}) (n int, err error)
```

* Scanf从标准输入扫描文本，根据format参数指定的格式取读取由空白符分隔的值保存到传递给本函数的参数中
* 本函数返回成功扫描的数据个数和遇到的任何错误。

示例：

```go
func main() {
	var (
		name string
		age int
		married bool
	)

	fmt.Scanf("1:%s 2:%d 3:%t",&name, &age, &married)
	fmt.Printf("扫描结果 name:%s age:%d married:%t\n", name, age, married)
}
```

fmt.Scanf不同于fmt.Scan简单的以空格作为输入数据的分隔符，fmt.Scanf为输入数据指定了具体的输入内容格式，只有按照格式输入数据才会被扫描并存入对应变量。

#### fmt.Scanln

函数签名

```go
func Scanln(a ...interface{}) (n int, err error)
```

* Scanfln类似Scan，它在遇到换行时才停止扫描。最后一个数据后面必须有换行或者到达结束位置。
* 本函数返回烧苗的数据个数和遇到的任何错误