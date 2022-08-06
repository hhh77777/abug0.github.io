介绍

实验目的

本实验旨在了解和学习缓冲区溢出攻击的两种方式：

* Code Injection Attacks(CI)：代码注入攻击
* Return-Oriented Programming(ROP): ROP攻击

文件介绍

* README.md: 文件描述；
* ctarget: 可执行文件，存在CI漏洞，完成实验phase 1-3；
* rtarget: 可执行文件，存在ROP漏洞，完成实验phase 4-5;
* hex2raw: 将十六进制转换为对应的输入字符串；
* cookie.txt: 实验中需要用到的8位十六进制数。
* farm.c: 


程序说明

ctarget和rtarget都会从标准输入中读取字符串，函数如下：

```c
unsigned getbuf()
{
	char buf[BUFFER_SIZE];
	Gets(buf);
	return 1;
}

```

Gets类似于库函数gets，它会从标准输入读取字符串（“\n”作为结尾）存储到buf中，且不会检查缓冲区和字符串的长度，因而存在缓冲区溢出漏洞。

getbuf会在test中被调用：

```c
void test()
{
	int val;
	val = getbuf();
	printf("No exploit. Getbuf returned 0x%x\n", val);
}
```



ctarget和rtarget的使用：

> Both CTARGET and RTARGET take several different command line arguments: 
>
> -h: Print list of possible command line arguments 
>
> -q: Don’t send results to the grading server 
>
> -i FILE: Supply input from a file, rather than from standard input

使用带上-q参数以避免远程服务器校验。



实验目标

Part 1: Code Injection Attacks

ctarget被编译为固定栈地址且栈可执行，所以可以直接注入代码到栈上，并通过修改返回地址去执行注入代码。

Phase 1：getbuf执行后去调用touch1，而不再是返回test；

程序中存在代码：

```c
void touch1()
{
	vlevel = 1; /* Part of validation protocol */
	printf("Touch1!: You called touch1()\n");
	validate(1);
	exit(0);
}

```



Phase2: getbuf执行后去调用touch2;

```c
void touch2(unsigned val)
{
	vlevel = 2; /* Part of validation protocol */
	if (val == cookie) {
		printf("Touch2!: You called touch2(0x%.8x)\n", val);
		validate(2);
	} else {
		printf("Misfire: You called touch2(0x%.8x)\n", val);
		fail(2);
	}
	exit(0);
}

```

Phase 3:  getbuf执行后去调用touch3;

```c
/* Compare string to hex represention of unsigned value */
int hexmatch(unsigned val, char *sval)
{
	char cbuf[110];
	/* Make position of check string unpredictable */
	char *s = cbuf + random() % 100;
	sprintf(s, "%.8x", val);
	return strncmp(sval, s, 9) == 0;
}


void touch3(char *sval)
{
	vlevel = 3; /* Part of validation protocol */
	if (hexmatch(cookie, sval)) {
		printf("Touch3!: You called touch3(\"%s\")\n", sval);
		validate(3);
	} else {
        printf("Misfire: You called touch3(\"%s\")\n", sval);
		fail(3);
	}
	exit(0);
}
```

Part 2： Return-Oriented Programming

rtarget被编译为栈随机化，且栈不可执行。



Phase 4: getbuf执行后去调用touch2;

Phase 5: getbuf执行后去调用touch3;



实验过程

CI(phase 1)

使用objdump 反汇编看一下ctarget：

```shell
objdump -d ctarget
```

找到getbuf函数，如图。可以看到函数内部在栈上申请了40bytes的空间，而后调用Gets读取输入，并将之存储到栈上。

![image-20220806160116333](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/202208061601064.png)

回忆一下关于栈帧的知识，此时栈顶

CI(phase 2)

CI(phase 3)

ROP(phase 1)

ROP(phase 2)
