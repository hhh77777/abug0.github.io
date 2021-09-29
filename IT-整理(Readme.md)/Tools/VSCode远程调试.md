# VSCode远程调试

[参考一: Remote Development配置](https://www.cnblogs.com/tinywan/p/11107397.html)

[参考二: 使用 VSCode 远程访问代码以及远程 GDB 调试](https://warmgrid.github.io/2019/05/21/remote-debug-in-vscode-insiders.html)

[参考三: VSCode配置文档](https://vscode.readthedocs.io/en/latest/editor/debugging/)

[TOC]

## Remote ssh配置文件

```
Host test-93.129
  HostName test-93.129
  Port 22
  User root
  IdentityFile C:\\Users\\user\\.ssh\\id_rsa

Host 192.168.93.129
  HostName 192.168.93.129
  User root
  IdentityFile C:\\Users\\user\\.ssh\\id_rsa
```



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

## VSCode远程调试配置实例一

### launch.json:

```
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "(gdb) remote",
            "type": "cppdbg",
            "request": "launch",
            "program": "${fileDirname}\\${fileBasenameNoExtension}", //调试时要运行的可执行文件,例如redis/src/redis-server
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}",
            "environment": [],
            "externalConsole": true,
            "MIMode": "gdb",
            "preLaunchTask": "gcc",
            "miDebuggerPath": "gdb.exe",
            "miDebuggerServerAddress": "10.10.10.1",  
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                }
            ]
        },

        {  
            "name": "(gdb) Launch", // 配置名称，将会在启动配置的下拉菜单中显示  
            "type": "cppdbg",       // 配置类型，这里只能为cppdbg  
            "request": "launch",    // 请求配置类型，可以为launch（启动）或attach（附加）  
            "program": "${workspaceFolder}/${fileBasenameNoExtension}.exe",// 将要进行调试的程序的路径  
            "args": [],             // 程序调试时传递给程序的命令行参数，一般设为空即可  
            "stopAtEntry": false,   // 设为true时程序将暂停在程序入口处，一般设置为false  
            "cwd": "${workspaceFolder}", // 调试程序时的工作目录，一般为${workspaceFolder}即代码所在目录  
            "environment": [],  
            "externalConsole": true, // 调试时是否显示控制台窗口，一般设置为true显示控制台  
            "MIMode": "gdb",  
            "miDebuggerPath": "C:\\Program Files (x86)\\CodeBlocks\\MinGW\\bin\\gdb32.exe", // miDebugger的路径，注意这里要与MinGw的路径对应  
            "preLaunchTask": "gcc", // 调试会话开始前执行的任务，一般为编译程序，c++为g++, c为gcc  
            "setupCommands": [  
                {   
		    "description": "Enable pretty-printing for gdb",  
                    "text": "-enable-pretty-printing",  
                    "ignoreFailures": true  
                }  
            ]  
        },

        {
            "name": "(gdb) Windows 上的 Bash 启动",
            "type": "cppdbg",
            "request": "launch",
            "program": "输入程序名称，例如 ${workspaceFolder}/a.exe",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}",
            "environment": [],
            "externalConsole": false,
            "pipeTransport": {
                "debuggerPath": "/usr/bin/gdb",
                "pipeProgram": "${env:windir}\\system32\\bash.exe",
                "pipeArgs": ["-c"],
                "pipeCwd": ""
            },
            "setupCommands": [
                {
                    "description": "为 gdb 启用整齐打印",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                }
            ]
        },
        {
            "name": "(Windows) 启动",
            "type": "cppvsdbg",
            "request": "launch",
            "program": "输入程序名称，例如 ${workspaceFolder}/a.exe",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}",
            "environment": [],
            "externalConsole": false
        }
    ]
}
```

### tasks.json

```
{
	"version": "2.0.0",
	"tasks": [
		{
			"type": "shell",
			"label": "gcc remote",
			"command": "/usr/bin/gcc",
			"args": [
				"-g",
				"${file}",
				"-o",
				"${fileDirname}\\${fileBasenameNoExtension}"
			],
			"options": {
				"cwd": "${workspaceFolder}"
			},
			"problemMatcher": [
				"$gcc"
			],
			"group": {
				"kind": "build",
				"isDefault": true
			}
		},

		{
			"type": "shell",
			"label": "gcc",
			"command": "D:\\awei-tools\\mingw\\bin\\gcc.exe",
			"args": [
				"-g",
				"${file}",
				"-o",
				"${fileDirname}\\${fileBasenameNoExtension}.exe"
			],
			"options": {
				"cwd": "${workspaceFolder}"
			},
			"problemMatcher": [
				"$gcc"
			],
			"group": {
				"kind": "build",
				"isDefault": true
			}
		}
	]
}
```

## VSCode远程调试配置实例二

### launch.json:

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
            "program": "${workspaceFolder}/src/redis-server",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}",
            "environment": [],
            "externalConsole": false,
            "MIMode": "gdb",
            "preLaunchTask": "gcc",
            "miDebuggerPath": "gdb",
            
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                }
            ]
        },
   
        {
            "name": "LaunchGo",
            "type": "go",
            "request": "launch",
            "mode": "auto",
            "remotePath": "",
            "port": 5546,
            "host": "127.0.0.1",
            "program": "${fileDirname}",
            //"env": {
            //    "GOPATH": "E:/GoCode",
            //    "GOROOT": "C:/Program Files/Go"
            //},
            "args": [],
            //"showLog": true
        },

        {
            "name": "Django",
            "type": "python",
            "request": "launch",
            
            "program": "D:\\codes\\demos\\django-test\\demo\\manage.py",
            "cwd": "${workspaceRoot}",
            "args": [
                "runserver",
                "5000"
            ],
            "env": {},
            "envFile": "${workspaceRoot}/.env",
            "debugOptions": [
                "WaitOnAbnormalExit",
                "WaitOnNormalExit",
                "RedirectOutput",
                "DjangoDebugging"
            ]
        },

        {
            "name": "Python: 当前文件",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        }
    ]
}
```

### tasks.json:

```json
{
    // See https://go.microsoft.com/fwlink/?LinkId=733558
    // for the documentation about the tasks.json format
    "version": "2.0.0",
    "tasks": [
        {
			"type": "shell",
			"label": "gcc",
			"command": "make",
			"args": [
				"CC=clang"
			],
			"options": {
				"cwd": "${workspaceFolder}"
			},
			"problemMatcher": [
				"$gcc"
			],
			"group": "build"
        },

        {
            "label": "build",
            "type": "shell",
            "command": "msbuild",
            "args": [
                "/property:GenerateFullPaths=true",
                "/t:build",
                "/consoleloggerparameters:NoSummary"
            ],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "reveal": "silent"
            },
            "problemMatcher": "$msCompile"
        }
    ]
}
```

