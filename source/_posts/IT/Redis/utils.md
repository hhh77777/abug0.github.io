# Utils.md

[TOC]

## string2ll

<utils.c/412Ln>

```c
/* Convert to negative if needed, and do the final overflow check when
     * converting from unsigned long long to long long. */
    if (negative) {
        if (v > ((unsigned long long)(-(LLONG_MIN+1))+1)) /* Overflow. */
            return 0;
        if (value != NULL) *value = -v;
    } else {
        if (v > LLONG_MAX) /* Overflow. */
            return 0;
        if (value != NULL) *value = v;
    }
```

解析：为什么写成 (v > ((unsigned long long)(-(LLONG_MIN+1))+1))？

此处的运算顺序：

* x = -(LLONG_MIN+1)，实际上，LLONG_MIN的大小：

  ```c
  # define LLONG_MIN (-LLONG_MAX - 1LL)
  ```

  直接-LLONG_MIN会发生溢出( |LLONG_MIN| > LLONG_MAX)，所以先算LLONG_MIN+1，得到的值恰为LLONG_MAX = |LLONG_MIN| - 1

* y = (ull)x，转换为unsigned long long
* v > (y+1)，转换为unsigned long long后此时不会溢出，(y+1) = LLONG_MAX+1 = |LLONG_MIN|