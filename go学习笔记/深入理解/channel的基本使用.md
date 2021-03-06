## channel的基本使用

channel用在数据流动的地方：1.消息传递、消息过滤；2. 信号广播；3. 事件订阅与广播；4. 请求、响应转发；5. 任务分发；6. 结果汇总；7. 并发控制；8. 同步与异步

#### 1. channel存在3种状态：

* nil，未初始化的状态，只进行了声明，或者手动赋值为nil
* active，正常的channel，可读或者可写
* closed，已关闭，千万不要无认为关闭channel后，channel的值是nil

#### 2. channel可进行3中操作

* 读
* 写
* 关闭

把这3种操作和3种channel状态可以组合出9种情况：

|   操作    | nil的channel | 正常的channel | 已关闭channel |
| :-------: | :----------: | :-----------: | :-----------: |
|   <- ch   |     阻塞     |  成功或阻塞   |   读到零值    |
|   ch <-   |     阻塞     |  成功或阻塞   |     panic     |
| close(ch) |    panic     |     成功      |     panic     |

对于nil通道的情况，也并非完全遵循上表，有1个特殊场景：当nil的通道在select的某个case中时，这个case会阻塞，但不会造成死锁。