---
title: "secure_link"
isCJKLanguage: true
date: 2021-05-23 21:45:28
updated: 2021-05-23 21:45:28
categories: 
- Web服务器
- Nginx
tags: 
- Nginx
---

# secure_link

python

{%spoiler 示例代码%}
```python
import base64
import hashlib

future = datetime.datetime.now() + datetime.timedelta(minutes=5)
url = "/securedir/file.txt"
timestamp = str(time.mktime(future.timetuple()))
security = base64.b64encode(hashlib.md5( secret ).digest()).replace('+', '-').replace('/', '_').replace("=", "")
data = str(url) + "?st=" + str(security) + "&e=" + str(timestamp)

```
{%endspoiler%}