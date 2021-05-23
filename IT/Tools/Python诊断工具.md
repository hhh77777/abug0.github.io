# Python诊断工具

## 一、pyrasite

使用pyrasite可以attach到正在运行的python进程上：

```bash
pyrasite-shell <PID>
```

*使用时遇到一个问题: 尝试打印复杂变量时，有可能导致pyrasite异常退出，暂未找到原因，不过可以尝试做类型转换来绕过这个问题。*

### 问题

#### （一）阻塞

执行如下命令后无反应：

```shell
pyrasite-shell 28414
```

原因可能是当前登陆用户与进程执行的用户不同，可以使用runuser命令以指定用户进行pyrasite-shell。

问题可见[ipc.connect hang forever](https://github.com/lmacken/pyrasite/issues/60)

## 二、py-spy

安装

```bash
pip install py-spy
```

