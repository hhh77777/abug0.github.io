# VSCode远程调试

[参考一: Remote Development配置](https://www.cnblogs.com/tinywan/p/11107397.html)

## Redis远程调试-配置文件

* tasks.json

  ```json
  {
  	"version": "2.0.0",
  	"tasks": [
  		{
  			"type": "shell",
  			"label": "gcc",
  			"command": "make",
  			
  			"options": {
  				"cwd": "${workspaceFolder}"
  			},
  			"problemMatcher": [
  				"$gcc"
  			],
  			"group": "build"
  		}
  	]
  }
  ```

  

* launch.json

  ```json
  {
      // Use IntelliSense to learn about possible attributes.
      // Hover to view descriptions of existing attributes.
      // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
      "version": "0.2.0",
      "configurations": [
          {
              "name": "(gdb) Launch",
              "type": "cppdbg",
              "request": "launch",
              "program": " /root/awei/codes/redis/src/redis-server",
              "args": [],
              "stopAtEntry": false,
              "cwd": "${workspaceFolder}",
              "environment": [],
              "externalConsole": false,
              "MIMode": "gdb",
              "preLaunchTask": "gcc",
              "setupCommands": [
                  {
                      "description": "Enable pretty-printing for gdb",
                      "text": "-enable-pretty-printing",
                      "ignoreFailures": true
                  }
              ]
          },
  
  
          {
              "type": "pwa-chrome",
              "request": "launch",
              "name": "Launch Chrome against localhost",
              "url": "http://localhost:8080",
              "webRoot": "${workspaceFolder}"
          }
      ]
  }
  ```

  

## stfp远程同步配置样例

```json
[
    {
        "name": "test01",
        "protocol": "sftp",
        "host": "10.10.10.1",
        "port": 22,
        "username": "root",
        "password": "aaaaa",
        "context": "E:\\test01",
        "remotePath": "/root/test01",
        "uploadOnSave": false,
        "connectTimeout":100000,
        "profiles": {
            "test-01": {
                "host": "10.10.10.1",
                "password": "123456"
            },

            "test-02": {
                "host": "10.10.10.2"
            }
        }
    },

    {
        "name": "test02",
        "protocol": "sftp",
        "port": 22,
        "username": "root",
        "password": "bbbbb",
        "context": "E:\\test02",
        "remotePath": "/root/test02",
        "uploadOnSave": false,
        "connectTimeout":100000,
        "profiles": {
            "test-03": {
                "host": "10.10.20.1"
            },
            
            "test-04": {
                "host": "10.10.20.2"
            }
        }
    } 
]
```

