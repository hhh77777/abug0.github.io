---
title: "推送单次commit"
isCJKLanguage: true
date: 2021-03-13 20:45:54
updated: 2021-03-13 20:45:54
categories: 
- Tools
- git
tags: 
- git
---

# git推送单次commit

一、将某次commit

{%spoiler 示例代码%}
```bash
git push <remote name> <commit hash>:<remote branch name>

比如：
$ git push origin 2dc2b7e393e6b712ef103eaac81050b9693395a4:master
```
{%endspoiler%}