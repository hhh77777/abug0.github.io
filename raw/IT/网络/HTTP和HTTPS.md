# HTTP和HTTPS

## HTTP

HTTP：超文本传输协议。

HTTP使用明文传输，安全性低。

### HTTP的问题

* 明文传输，容易被监听
* 信息可以被篡改
* 不验证对方身份，可能遇到伪装

## 对称与非对称加密

对称加密/私钥加密：即加解密使用同一个密钥。

非对称加密/公钥加密：需要一对密钥--私钥和公钥。私钥加密的内容只有公钥能解密，公钥加密的内容只有私钥能解密。私钥私有，公钥对外发布。

一般来说，对称加解密速度更快，但安全性稍弱，而非对称加解密速度稍慢，但安全性更高。

## HTTPS

### 概论

HTTPS（Hypertext Transfer Protocol Secure，超文本传输安全协议），使用HTTP进行通信，SSL/TLS加密数据包。

HTTPS混合使用非对称加密与对称加密：http内容通过对称加密算法进行加密，而对称密钥的协商过程则使用非对称加密算法进行加密。

### 中间人攻击

加密问题解决了，但是通过中间人攻击仍旧可以对通信内容进行监听。

![image-20210726164436657](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210726180127.png)

![2116505485-5e8c93c2e0584](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210726215140.png)

​							（图片来自参考二）

### 数字签名

#### 摘要

> 给定一条消息M作为输入，加密散列函数的输出H称为这条消息的摘要或指纹H(M)。
>
> 摘要的特性：
>
> * 原像不可计算性：给定摘要H(M)而未知消息M的情况下，难以计算出消息M的值；
> * 原像不相同性：给定消息M1的摘要，找出一条消息M2（M2!=M1）使其摘要H(M2)等于M1的摘要（H(M1)==H(M2)）是十分困难的；
> * 抗碰撞性：找出一对摘要相同（H(M1)==H(M2)）而自身不同的消息（M2!=M1）是十分困难的。

#### 摘要算法

常见摘要算法有MD5、SHA-1、SHA256、SHA-2等。

目前，MD5已与2005年被宣告破解（两个不同的128字节的序列被证明具有相同的MD5值），而SHA-1、SHA-2也被认为具有潜在的脆弱性。<sup><a href='#ref1'>3</a></sup> 

2017年，CWI Amsterdam 与 Google 宣布了一个成功的 SHA-1 碰撞攻击。<sup><a href='#ref4'>4</a></sup>

#### 数字签名

使用私钥对消息摘要进行加密后，得到的输出称为数字签名。

* 签名：发送方使用私钥对消息摘要进行加密，得到签名。

* 验签：接收方使用公钥对签名进行解密，将得到的摘要与消息内容的摘要进行对比。

* 数字签名过程需要使用到私钥，所以除非私钥泄漏，其他人无法伪造。
* 数字签名的不可伪造性，使得它可以用来确认一个实体，类似于现实中的个人签名。

### 数字证书

数字签名依赖于公钥与私钥，但是客户端与服务端交换公钥的过程仍旧可能受到攻击，比如中间人攻击，客户端可能收到伪造的服务端公钥。

为了解决这一问题，引入数字证书。

数字证书由CA机构进行颁发，内容包括所有人信息、所有人公钥、有效期、以及认证机构信息、认证机构的数字签名等。数字证书的本质是数字签名+公钥+证书认证机构（Certificate Authority）。

通过证书上的数字签名可以对证书内容的完整性进行验证，验证通过后，客户端可以信任证书中的公钥即为证书所有人的公钥。

#### 数字证书的验证

数字证书由可信任的CA机构颁发，通常认为如果一个CA机构可信任，则由该机构颁发的证书为可信任证书。

在对数字证书进行验证时，也需要对签发这个证书的CA证书进行验证，一直到根证书为止。

#### 根证书

数字证书体系是一个分层级的、中心化的认证体系。

根证书，又称自签名证书，是指CA机构给自己颁发的证书。根证书也是信任链的起点。

根证书一般由操作系统/浏览器内置。

### HTTPS解决的问题

* 信息窃听问题：加密传输；
* 信息完整性问题：SSL/TLS具备完整性验证能力-MAC(Message Authentication code)；
* 遭遇伪装：数字证书，可以进行服务端和客户端的验证。

### HTTPS握手过程

依赖于client与server商定的具体加密套件，HTTPS握手可以分为两类：基于RSA的握手和基于Deffie-Hellman的握手。

两种握手方式主要是密钥交换和身份认证方式上的不同。

#### 基于Deffie Hellman方式的握手

![image-20210729162324573](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210729162324.png)

#### 基于RSA方式的握手

![image-20210729162239422](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210729162239.png)

#### 密码套件的格式说明

![ssl-handshake-ciphers](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210729162702.png)

#### 抓包

* 基于DH的握手

![image-20210729162803287](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210729162803.png)

* 基于RSA的握手

  ![image-20210729162840465](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210729162840.png)



## 附件

[https-DH.cap.pcapng](https://github.com/Abug0/abug0.github.io/raw/master/IT/imgs/https-DH.cap.pcapng)

[https-RSA.cap.pcapng](https://github.com/Abug0/abug0.github.io/raw/master/IT/imgs/https-RSA.cap.pcapng)

## 参考

[[1] HTTPS中CA证书的签发及使用过程](https://www.cnblogs.com/xdyixia/p/11610102.html)

[[2] Http和Https之间的区别，及原理分析](https://segmentfault.com/a/1190000022294393)

[[3] TCP/IP详解 卷1：协议 18.4.8(第2版)]()

[[4] 常用消息摘要算法简介](https://cloud.tencent.com/developer/article/1584742)

[[5] 使用openssl创建https证书](https://cloud.tencent.com/developer/article/1548350)

[[6] 在Linux下使用openssl创建根证书，中间证书和服务端证书](https://www.digac.cc/2020/06/use_openssl_to_create_root_certificate_intermediate_certificate_and_server_certificate.html)

[[7] der pem cer crt key pfx等概念及区别](https://blog.51cto.com/wushank/1915795)

[[8] 利用OpenSSL创建证书链并应用于IIS7](https://blog.csdn.net/HANQIAN12345/article/details/101971671)

[[9] 多域名证书签发](https://blog.opensvc.net/duo-yu-ming-zheng-shu-qian-fa/)

[[10] OpenSSL创建带SAN扩展的证书并进行CA自签](https://monkeywie.cn/2019/11/15/create-ssl-cert-with-san/)

[[11] HTTPS篇之SSL握手过程详解](https://razeencheng.com/post/ssl-handshake-detail.html)

[[12] TLS详解握手流程](https://juejin.cn/post/6895624327896432654)

[[13] 消息认证码与数字签名的理解](https://juejin.cn/post/6844904158319869960)

[[15] HTTPS解决了什么问题](https://segmentfault.com/a/1190000022012971)

[[16] 理解Deffie-Hellman密钥交换算法](http://wsfdl.com/algorithm/2016/02/04/%E7%90%86%E8%A7%A3Diffie-Hellman%E5%AF%86%E9%92%A5%E4%BA%A4%E6%8D%A2%E7%AE%97%E6%B3%95.html)

[17 图解TLS--字节级分析](https://tls.ulfheim.net/)

