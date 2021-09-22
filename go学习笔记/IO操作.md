## IO操作

### 1.1 输入输出的底层原理

终端其实是一个文件，相关实例如下

* `os.Stdin`：标准输入的文件实例，类型为`*File`
* `os.Stdout`：标准输出的文件实例，类型为`*File`
* `os.Stderr`：标准错误输出的文件实例，类型为`*File`

以文件的方式操作终端

```go
func main() {
	var buf [16]byte
	os.Stdin.Read(buf[:])
	os.Stdin.WriteString(string(buf[:]))
}
```

### 1.2 文件操作相关API

```go
// 根据提供的文件名创建新的文件，返回一个文件对象，默认权限是o666
func Create(name string) (file *File, err Error)

// 根据文件描述符创建相应的文件，返回一个文件对象
func NewFile(fd uintptr, name string) *File

// 只读方式打开一个名称为name的文件
func Open(name string) (file *File, err Error)

// 打开名称为name的文件，flag是打开的方式、只读、读写等，perm是权限
func OpenFile(name string, flag int, perm uint32) (file *File, err Error)

// 写入byte类型的信息到文件
func (file *File) Write(b []byte) (n int, err Error)

// 在指定位置开始写入byte类型的信息
func (file *File) WriteAt(b []byte, off int64) (n int, err Error)

// 写入string信息到文件
func (file *File) WriteString(s string) (ret int, err Error)

// 读取数据到b中
func (file *File) Read(b []byte) (n int, err Error)

// 从off开始读取数据到b中
func (file *File) ReadAt(b []byte, off int64) (n int, err Error)

// 删除文件名为name的文件
func Remove(name string) Error
```

### 1.3 打开和关闭文件,将文件的内容读出

`os.Open()`函数能够打开一个文件，返回一个`*File`和一个`err`。对得到的文件实例调用close()方法能够关闭文件

文件读取可以用`file.Read()`和`file.ReadAt()`，读到文件末尾会返回io.EOF的错误。

```go
func main() {
	// 只读方式打开当前目录下的main.go文件
	file, err := os.Open("./xx.text")
	if err != nil {
		fmt.Println("open file failed, err", err)
		return
	}
	// 关闭文件
	defer file.Close()

	// 定义接收文件读取的字节数组
	var buf [128]byte
	var content []byte

	for {
		n, err := file.Read(buf[:])
		fmt.Println(n)    // 读取字符的个数
		if err == io.EOF {   
			// 读取结束
			break
		}

		if err != nil {
			fmt.Println("read file err",err)
			return
		}

		content = append(content, buf[:n]...)
		fmt.Println("content===>", string(content))
	}
	fmt.Println(string(content))
}
```

```go
io.EOF：
// EOF is the error returned by Read when no more input is available.
// Functions should return EOF only to signal a graceful end of input.
// If the EOF occurs unexpectedly in a structured data stream,
// the appropriate error is either ErrUnexpectedEOF or some other error
// giving more detail.

表示的是当从文件把最后一个字符读出后， 再进行读数据的话（此时文件中的数据全部读出）err为io.EOF

```

### 1.4 写文件

```go
func main() {
	// 新建文件
	file, err := os.Create("./xx.txt")
	if err != nil {
		fmt.Println("err===>", err)
		return
	}
	// 关闭文件
	defer file.Close()
	file.WriteString("活火石")
	for i := 0; i < 5; i++ {
		file.WriteString("ab\n")
		file.Write([]byte("cd\n"))
	}

}
```

### 1.5 bufio

* bufio包实现了带缓冲区的读写，是对文件读写的封装
* bufio缓冲写数据

| 模式        | 含义     |
| ----------- | -------- |
| os.O_CREATE | 创建文件 |
| os.O_WRONLY | 只写     |
| os.O_RDONLY | 只读     |
| os.O_RDWR   | 读写     |
| os.O_TRUNC  | 清空     |
| os.O_APPEND | 追加     |

```go
func wr() {
	// 参数2：打开模式，所有模式都在上面
	// 参数3：权限控制
	file, err := os.OpenFile("./xx.txt", os.O_CREATE|os.O_WRONLY, 0666)
	if err != nil {
		return
	}

	defer file.Close()

	// 获取writer对象
	writer := bufio.NewWriter(file)
	for i := 0; i < 10; i++ {
		writer.WriteString("hello\n")
	}

	// 刷新缓冲区，强制写出
	writer.Flush()
}

func re(){
	file, err := os.Open("./xx.txt")

	if err != nil {
		return
	}
	defer file.Close()

	reader := bufio.NewReader(file)
	for {
		line, _, err := reader.ReadLine()
		if err == io.EOF {
			break
		}

		if err != nil {
			return
		}
		fmt.Println(string(line))
	}
}

func main() {
	wr()
}

```

