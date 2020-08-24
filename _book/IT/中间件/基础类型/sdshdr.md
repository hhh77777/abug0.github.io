# Redis底层数据类型1 -- sds

sds-动态字符串

数据类型sdshdr_5/8/16/32/64。分别用8/16/32/64位表示字符串长度，其中sdshdr_5是一个特例。

数据类型定义：
`struct __attribute__ ((__packed__)) sdshdr16 {

  uint16_t len; /* used */

  uint16_t alloc; /* excluding the header and null terminator */

  unsigned char flags; /* 3 lsb of type, 5 unused bits */

  char buf[];

};`

sdshdr_8/32/64格式与此相似，只是数据长度由16位变为8/32/64位。但是sdshdr_5的声明：
`struct __attribute__ ((__packed__)) sdshdr5 {

  unsigned char flags; /* 3 lsb of type, and 5 msb of string length */

  char buf[];

};`

各字段含义：

* len: 字符串的长度（已使用空间）

* alloc: 分配空间的总长度

* flags: 低三位标识sds类型（sdshdr_5会用高五位表示字符串长度）

* buf: 保存字符串

  sdshdr实际占用的空间=alloc+1,最后一位额外空间为‘/0’。

