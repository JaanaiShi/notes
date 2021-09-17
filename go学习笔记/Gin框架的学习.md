## Gin路由

### 基本路由

* gin框架中采用的路由库是基于httprouter做的

```go
package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
)


func main() {
	// 1. 创建路由
	r := gin.Default()
	// 2. 绑定路由规则，执行的函数
	// gin.Context，封装了request和response
	r.GET("/", func(c *gin.Context) {
		c.String(http.StatusOK, "hello world!")
	})

	// 3. 监听端口，默认是8080
	// Run("里面不指定端口号默认为8080")
	r.Run(":8080")
}
```

### API参数

可以通过Context的Param方法来获取API参数，获取动态参数

```go
r.GET("/user/:name/*action", func(c *gin.Context) {
    name := c.Param("name")
    action := c.Param("action")
    // 截取
    action = strings.Trim(action, "/")
    c.String(http.StatusOK, name + " is " + action)

})
```

### URL参数

URL参数可以通过DefaultQuery()或Query()方法获取

DefaultQuery()若参数不存在，返回默认值，Query()若不存在，返回空串

```go
name := c.DefaultQuery("name", "lisi")
name1:= c.Query("name")
c.String(http.StatusOK, fmt.Sprintf("hello %s", name))
c.String(http.StatusOK, fmt.Sprintf("hello %s", name1))
```

### 表单参数

* 表单传输为post请求，http常见的传输格式为四种：
  * application/json
  * application/x-www-form-urlencoded
  * application/xml
  * multipart/form-data
* 表单参数可以通过PostForm()方法获取，该方法默认解析的是x-www-form-urlencoded或from-data格式的参数

```go
r.POST("/form", func(c *gin.Context) {
		types := c.DefaultQuery("type", "post")
		username := c.PostForm("username")
		password := c.PostForm("userpassword")
		c.String(http.StatusOK, fmt.Sprintf("username: %s, password: %s, type: %s", username, password, 		types))
})
```

### 上传单个文件

* multipart/form-data格式用于文件上传
* gin文件上传与原生的net/http方法类似，不同在于gin把原生的request封装到c.Request中

```go
r.POST("/upload", func(c *gin.Context) {
		types := c.DefaultQuery("type", "post")
		file, err := c.FormFile("file")
		c.String(http.StatusOK, fmt.Sprintf("%s", types))
		if err != nil {
			c.String(500, "上传图片出错")
		}
		c.SaveUploadedFile(file, file.Filename)
		c.String(http.StatusOK, file.Filename)
	})
```

### 上传多个文件

代码分析

```go
func main() {
	r := gin.Default()
	// 限制表单上传大小 8MB，默认为32MB
	r.MaxMultipartMemory = 8 << 20
	r.POST("/upload", func(c *gin.Context) {
		form, err := c.MultipartForm()  // MultipartForm 是解析后的 multipart 表单，包括文件上传。
		if err != nil {
			c.String(http.StatusBadRequest, fmt.Sprintf("get err %s", err.Error()))
		}
		// 获取所有图片
		files := form.File["files"]
		// 遍历所有图片
		for _, file := range files {
			// 逐个存
			err := c.SaveUploadedFile(file, file.Filename);  // 第一个参数为表单文件，第二个参数为地址（格式为字符串）
			if err != nil {
                // http.StatusBadRequest 表示的是400
				c.String(http.StatusBadRequest, fmt.Sprintf("upload err %s", err.Error()))
				return
			}
		}

		c.String(200, fmt.Sprintf("upload ok %d files", len(files)))
	})

	r.Run()
}
```

### gin框架的路由原理

httprouter是一个高性能路由分发器，它负责将不同方法的多个路径分别注册到各个handle函数，当收到请求时，负责快速查找请求的路径是否有相对应的处理函数，并且进行下一步业务逻辑处理。golang的gin框架采用了httprouter进行路由匹配，httprouter是通过**radixtree**来进行高效的路径查找；同时路径还支持两种通配符匹配。

未完

### 路由拆分与注册

当项目的规模增大后就不太适合继续在项目的main.go文件中去实现路由注册相关逻辑了，我们会倾向于把路由部分的代码都拆分出来，形成一个单独的文件或包



