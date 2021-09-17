## 什么是Context？

Context，也叫做上下文，它的接口定义如下：

```go
type Context interface {
    Deadline() (deadline time.Time, ok bool)
    Done() <-chan struct{}
    Err() error
    Value(key interface{}) interface{}
}
```

Context接口的4个方法

* `Deadline`：返回的第一个值是截止时间，到了这个时间点， context会自动触发Cancel动作。返回的第二个值是一个布尔值，true表示设置了截止时间，false表示没有设置截止时间，如果没有设置截止时间，就要手动调用cancel函数取消Context。
* `Done`：返回一个只读的通道（只有在被cancel），类型为`struct{}`。当这个通道可读时，意味着parent context已经发起了取消请求，根据这个信号，开发者就可以做一些清理动作，退出goroutine。
* `Err`：返回context被cancel的原因
* `value`：返回被绑定到Context的值，是一个键值对，所以要通过一个Key才可以获取对应的值，这个值一般是线程安全的。

## 为何需要Context

当一个协程（goroutine）开启后，我们是无法强制关闭的。

常见的关闭协程的原因有如下几种

1. goroutine自己跑完结束退出
2. 主进程crash退出，goroutine被迫退出
3. 通过通道发送信号，引导协程的关闭

第一种：属于正常关闭，

第二种：属于异常关闭，应当优化代码

第三种：开发者可以手动控制协程的方法。

```go
package main

import (
	"context"
	"fmt"
	"time"
)

func monitor( ctx context.Context, number int) {
	for {
		select {
		// 其实还可以写成case <- ctx.Done()
		// 这里仅是为了让我们可以看到Done返回的内容。

		// 在所有的goroutine里利用for + select搭配来不断检查ctx.Done()是否可读，可读说明该
		// context已经取消，你可以清理goroutine并退出了。
		case v :=<- ctx.Done():
			fmt.Printf("监控器%v，接收到通道值为：%v， 监控结束。\n", number, v)
			return
		default:
			fmt.Printf("监控器%v，正在监控中……\n", number)
			time.Sleep(2 * time.Second)
		}
	}
}

func main() {
	// 定义一个可取消的context
	ctx, cancel := context.WithCancel(context.Background())

	for i := 1; i <= 5; i++{
		go monitor(ctx, i)
	}

	time.Sleep(1 * time.Second)
	// 当你想到取消context的时候，只要调用一下cancel方法即可。这个cancel就是我们在创建
	// ctx的时候返回的第二个值。
	cancel()

	// 为了监控过是否停止，如果没有监控输出，就表示停止了
	time.Sleep(5 * time.Second)

	fmt.Println("主程序退出！！")
}
```

## 根Context是什么？

创建Context必须要指定一个父Context，Go已经帮我们实现了2个，

```go
var (
    background = new(emptyCtx)
    todo       = new(emptyCtx)
)

func Background() Context {
    return background
}

func TODO() Context {
    return todo
}
```

一个是Background，主要用于main函数、初始化以及测试代码中，作为Context这个树结构的最顶层的Context，也就是根Context，它不能被取消。

一个是TODO，如果我们不知道该使用什么Context的时候，可以使用这个，

他们两个本质上都是emptyCtx结构体类型，是一个不可取消，没有设置截止时间，没有携带任何值得Context。

### Context使用注意事项

1. 通常Context都是作为函数的第一个参数进行传递（规范性做法），并且变量名建议统一叫ctx
2. Context是线程安全的，可以放心地在多个goroutine中使用
3. 当你把Context传递给多个goroutine使用时，只要执行一次cancel操作，所有的goroutine就可以收到取消的信号。
4. 不要把原本可以由函数参数来传递的变量，交给Context的Value来传递
5. 当一个函数需要接收一个Context时，但是此时你还不知道要传递什么context时，可以先用context.TODO来代替，而不要选择传递一个nil
6. 当一个Context被cancel时，继承自该Context的所有子Context都会被cancel。