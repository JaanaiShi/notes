## HTTP

Go语言内置的net/http包十分的优秀，提供了HTTP客户端和服务端的实现。

### 1. HTTP协议

超文本传输协议（HTTP，HyperText Transfer Protocol）是互联网上应用最为广泛的一种网络传输协议，所有的WWW文件都必须遵守这个标准。

### 2. HTTP客户端

基本的HTTP/HTTPS请求Get、Head、Post和PostForm函数发出HTTP/HTTPS请求。

```go
resp, err := http.Get("http://51mh.com/")

resp, err := http.Post("http://51mh.com/upload", "image/jpeg", &buf)

resp, err := http.PostForm("http://51mh.com/form", url.Values{"key": {"value"}, "id": {"123"}})
```

程序在使用完response后必须关闭回复的主体。

```go
func main() {
	resp, err := http.Get("http://51mh.com/")
	if err != nil {
		//handle error
		fmt.Println("err===>", err)
		return
	}

	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)

	if err != nil {
		fmt.Println("err===>", err)
		return
	}

	fmt.Printf("body===>%s", body)
}
```

### 3. GET请求示例

使用net/http包编写一个简单的发送HTTP请求的Client端，代码如下：

```go
func main() {
	resp, err := http.Get("http://www.51hm.com/")
	if err != nil {
		fmt.Println("get failed, err:", err)
		return
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)

	if err != nil {
		fmt.Println("read from resp.Body failed, err", err)
		return
	}

	fmt.Print(string(body))
}
```

### 4. 带参数的GET请求示例

关于GET请求的参数需要使用Go语言内置的net/url这个标准库来处理

```go
```

