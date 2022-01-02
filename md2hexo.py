import os
import sys
import re
import time
import datetime
# import enchant
import jieba


class HugoMarkdown:

    # __srcDir = 'I:\src\hugo\docs' #源文章目录
    # __desDir = 'I:\src\hugo\9ong\content\post' #目的文件目录

    __srcDir = 'IT' #源文章目录
    __desDir = 'IT' #目的文件目录
    __ignoreFile = ["index.md","README.md",'more.md']#文件忽略
    __ignoreParentDir = ["docs","post","content","互联网"]#分类忽略（父级目录）


    def __init__(self):
        print("···HugoMarkdown···\n")

    @classmethod
    def setDesDir(cls, desdir=""):
        cls.__desDir = desdir

    #遍历源日志目录所有文件，批量处理
    def scanFiles(self):
        print("不再使用，除非有新的md文件目录需要批量转换")
        

        print("开始遍历源文章目录：",self.__srcDir,"\n")
        for root,dirs,files in os.walk(self.__srcDir):
            for file in files:   
                
                print("\n-----开始处理文章：",os.path.join(root,file),"-----\n")

                if self.__isIgnoreFile(file):            
                    print("忽略",file,"\n")
                    continue


                fileInfoDict = self.__getFileInfo(root,file)

                if (fileInfoDict['fileExt'] != ".md") or (fileInfoDict['parentDir']==''):
                    print("忽略",file,"\n")
                    continue                

                #测试输出    
                print(fileInfoDict,"\n")                

                self.__adjustFIleContent(fileInfoDict)

                #只循环一次，跳出所有循环
                # return 

    def scanFile(self,filePath):           

        self.__srcDir = self.__desDir

        root = os.path.dirname(filePath)
        file = os.path.basename(filePath)
        # print(os.path.join(root,file))
        # return False

        print("\n-----开始处理文章：",os.path.join(root,file),"-----\n")
        if self.__isIgnoreFile(file):
            print("忽略",file,"\n")
            return False


        fileInfoDict = self.__getFileInfo(root,file)

        if (fileInfoDict['fileExt'] != ".md") or (fileInfoDict['parentDir']==''):
            print("忽略",file,"\n")
            return False            

        #测试输出    
        print(fileInfoDict,"\n")                

        self.__adjustFIleContent(fileInfoDict)
        

    def __getFileInfo(self,root,file):
        print("获取文章信息：\n")
        #文件全路径                
        filePath = os.path.join(root,file)
        #文件名、扩展名
        filename,fileExt = os.path.splitext(file)
        #所在目录及上级目录
        parentDir = os.path.basename(root)
        grandpaDir = os.path.basename(os.path.dirname(root))
        if self.__isIgnoreParentDir(parentDir):
            parentDir = ""

        if self.__isIgnoreParentDir(grandpaDir):
            grandpaDir = ""

        # 文件相关时间
        fileCtime = self.__timeToDate(os.path.getctime(filePath), "%Y-%m-%d")
        fileMtime = self.__timeToDate(os.path.getmtime(filePath), "%Y-%m-%d")

        return {
            "filePath":filePath,
            "fileName":filename,
            "fileExt":fileExt,
            "parentDir":parentDir,
            "grandpaDir":grandpaDir,
            "fileCtime":fileCtime,
            "fileMtime":fileMtime
        }

    def __isIgnoreParentDir(self, parentDir):
        if parentDir in self.__ignoreParentDir:
            return True

    # 调整文章内容 比如meta设置、TOC、MORE设置，
    def __adjustFIleContent(self, fileInfoDict):
        # 读取文章内容 及 关键词
        print("读取文章内容...\n")
        with open(fileInfoDict['filePath'], "r", encoding="utf-8") as mdFile:
            content = mdFile.read().strip() 

            fileInfoDict['keywords'] = self.__getKeywords(content, fileInfoDict['fileName'])

            #content = self.__getMmeta(fileInfoDict) + self.__insertMoreToContent(content)
            pattern = re.compile(r"---((?!---).*title.*date.*)---", re.I|re.M|re.S)
            # 已经存在meta
            if re.search(pattern, content):
                print("存在meta")
                content = self.updateMeta(content, fileInfoDict)
                content = self.__insertSpoilerToContent(content)
            else:
                content = self.__getMmeta(fileInfoDict) + self.__insertSpoilerToContent(content)

            # 写入新文件
            self.__writeNewMarkdownFile(content, fileInfoDict)

    def getCategories(self, fileInfoDict):
        metaParentCategory = ""
        metaGrandpaCategory = ""
        if fileInfoDict['grandpaDir']!='':
            metaGrandpaCategory = "- "+fileInfoDict['grandpaDir']+"\n"
        
        if fileInfoDict['parentDir']!='':
            metaParentCategory = "- "+fileInfoDict['parentDir']+"\n"

        return metaGrandpaCategory + metaParentCategory

    def getTags(self, fileInfoDict):
        metaParentCategory = ""
        metaGrandpaCategory = ""
        if fileInfoDict['parentDir']!='':
            metaParentCategory = "- "+fileInfoDict['parentDir']+"\n"
        
        return metaParentCategory
        
    # 获取meta
    def __getMmeta(self, fileInfoDict):
        print("准备文章meta信息：", "\n") 
        meta = ""
        metaTitle = "title: \""+fileInfoDict['fileName']+"\"\n"
        metaCJK = "isCJKLanguage: true\n"
        metaDate = "date: "+fileInfoDict['fileCtime']+"\n"
        metaUpdateDate = "updated: "+fileInfoDict['fileMtime']+"\n"
        metaCategories = "categories: \n"
        metaParentCategory = ""
        metaGrandpaCategory = ""
        metaTags = "tags: \n"
        metaTagsList = ""
        metaKeywords = "keywords: \n"
        metaKeywordsList = ""

        if fileInfoDict['grandpaDir']!='':
            metaGrandpaCategory = "- "+fileInfoDict['grandpaDir']+"\n"
        
        if fileInfoDict['parentDir']!='':
            metaParentCategory = "- "+fileInfoDict['parentDir']+"\n"
        
        if fileInfoDict['keywords']:
            for word in fileInfoDict['keywords']:
                metaTagsList += "- "+word+"\n"
                metaKeywordsList += "- "+word+"\n"

        meta = "---\n"+metaTitle+metaCJK+metaDate+metaUpdateDate+metaCategories+metaGrandpaCategory+metaParentCategory+\
                metaTags+metaParentCategory+"---\n\n"
        print(meta, "\n")
        return meta

    def updateMeta(self, content, fileInfoDict):
        """更新文章元信息，只对title/updated/categories/tags进行更新
        """
        meta = re.search(r"---.*title.*date.*?---", content, re.I|re.M|re.S)
        if meta:
            meta = meta.group()
            meta = re.sub(r"title: .*?\n", "title: \""+fileInfoDict['fileName']+"\"\n", meta)
            meta = re.sub(r"updated: .*?\n", "updated: \""+fileInfoDict['fileMtime']+"\"\n", meta)
            print(meta)
            meta = re.sub(r"categories: .*?\n([-].*?\n)*", "categories: \n"+self.getCategories(fileInfoDict), meta)
            meta = re.sub(r"tags: .*?\n([-].*?\n)*", "tags: \n"+self.getTags(fileInfoDict), meta)
            content = re.sub(r"---.*title.*date.*?---", meta, content, flags=re.I|re.M|re.S)

        return content

    #插入<!--more-->到文章
    def __insertMoreToContent(self,content):        
        tocFlag = '<!--more-->'
        if (content.find(tocFlag) != -1):            
            print("发现",tocFlag,"\n")
            content = content.replace(tocFlag,tocFlag+"\n"+'<!--more-->'+"\n")
        else:
            print("没有发现",tocFlag,"\n")
            contents = content.splitlines()
            contentsLen = len(contents)
            if contentsLen>4:
                contents[4] = contents[4]+"\n"+'<!--more-->'+"\n"
                content = "\n".join(contents)

        print("插入<!--more-->...","\n")
        return content
    
    def __insertSpoilerToContent(self, content):
        """插入{%spoiler%}{%endspoiler%},提供代码折叠选项
        """
        def repl(mo):
            return r"{%spoiler 示例代码%}"+ "\n" + mo.string[mo.start(): mo.end()] + "\n" +r"{%endspoiler%}"

        flag = '```'
        # pattern = r"(```[^```]*```)"
        pattern = r"(?<!{%spoiler 示例代码%}\n)```((?!```).)*```"
        # pattern = re.compile(r"```((?!```).)*```", re.I|re.M|re.S)
        pattern = re.compile(pattern, re.I|re.M|re.S)
        if (re.search(pattern, content)):       
            print("发现代码", flag, "\n")
            content = re.sub(pattern, repl, content)
        else:
            print("没有发现代码", pattern, "\n")

        return content


    def __writeNewMarkdownFile(self,content,fileInfoDict):        
        relativeFilePath = fileInfoDict['filePath'].replace(self.__srcDir,"")

        desFilePath = self.__desDir+relativeFilePath
        print("写入新文件：",desFilePath,"\n")
        desDirPath = os.path.dirname(desFilePath)
        # print("##Final Path："+desFilePath)
        # return 
        if not os.path.exists(desDirPath):
            os.makedirs(desDirPath)
        with open(desFilePath,"w",encoding="utf-8") as nf:
            nf.write(content)

        if os.path.exists(desFilePath):
            print("----- 完成文章处理：",desFilePath," -----\n")
        else:
            print("---- 写入新文件失败! -----\n")

    def __isIgnoreFile(self,file):
        if file in self.__ignoreFile:
            return True

    #时间戳转换成日期
    def __timeToDate(self,timeStamp,format="%Y-%m-%d %H:%M:%S"):
        timeArray = time.localtime(timeStamp)
        return time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    

    #获取文章关键词
    def __getKeywords(self,content,filename):
        keywords = self.__wordStatistics(content,filename)
        keywordsList = sorted(keywords.items(), key=lambda item:item[1], reverse=True)            
        keywordsList = keywordsList[0:50]   
        keywordsList = self.__filterKeywords(keywordsList,filename)   
        print("保留关键词：",keywordsList,"\n")           
        return keywordsList

    #词频统计
    def __wordStatistics(self,content,filename):        
        stopwords = open('stopwords.txt', 'r', encoding='utf-8').read().split('\n')[:-1]        
        words_dict = {}
    
        temp = jieba.cut(content)
        for t in temp:
            if t in stopwords or t == 'unknow' or t.strip() == "":
                continue
            if t in words_dict.keys():
                words_dict[t] += 1
            else:
                words_dict[t] = 1

        # filenameCuts = jieba.cut(filename)                
        # for fc in filenameCuts:
        #     if fc in stopwords or fc == 'unknow' or fc.strip() == "":
        #         continue
        #     if fc in words_dict.keys():
        #         words_dict[fc] += 100
        #     else:
        #         words_dict[fc] = 100
        return words_dict

    #再次过滤关键词：在文件名也就是标题中，且汉字不少于2个，字符串不少于3个，不是纯数字
    def __filterKeywords(self,keywordsList,filename):
        print("分析文章标签/关键词...\n")
        newKeywordsList = []
        # print(keywordsList)
        # enD = enchant.Dict("en_US")
        for word,count in keywordsList:            

            # print(word,"\t",count)            
            wordLen = len(word)
            if filename.find(word)!=-1:
                if self.__isChinese(word) and wordLen<2:
                    continue
                elif wordLen<3:
                    continue                                        
                elif word.isdigit():
                    continue
                else:
                    newKeywordsList.append(word)
            # else:
            #     if wordLen>1 and self.__isChinese(word) and count>5:
            #         newKeywordsList.append(word)                
            #     elif wordLen>2 and enD.check(word) and count>5:
            #         newKeywordsList.append(word)   
            #     else:
            #         continue

        return newKeywordsList

    def __isChinese(self,word):
        for ch in word:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False


if __name__ == '__main__':
    hm = HugoMarkdown()
    #scanFiles 扫描一个目录下所有文件，批量处理
    if len(sys.argv) <= 1:
        hm.scanFiles()

    #单独处理一个文件，覆盖原文件，注意保存
    #theFile = input(r'输入文章绝对路径，比如I:\src\xxx\xxx\content\post\其他\xxx.md：')
    hm.setDesDir("")
    path = sys.path[0]
    for file in sys.argv[1:]:
        hm.scanFile(os.path.join(sys.path[0], file))
    # theFile = r'I:\srcxxx\xxxx\content\post\其他\xxx.md'