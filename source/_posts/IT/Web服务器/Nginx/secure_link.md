# secure_link

python

```python
import base64
import hashlib

future = datetime.datetime.now() + datetime.timedelta(minutes=5)
url = "/securedir/file.txt"
timestamp = str(time.mktime(future.timetuple()))
security = base64.b64encode(hashlib.md5( secret ).digest()).replace('+', '-').replace('/', '_').replace("=", "")
data = str(url) + "?st=" + str(security) + "&e=" + str(timestamp)

```

