### select实现原理

Golang实现select时，定义了一个数据结构表示每个case语句（含default，default实际上是一种特殊的case），select执行过程可以类比成一个函数，函数输入case数组，输出选中的case，然后程序流程转到选中的case中。