# Best_fields, most_fields与cross_fields

本文使用的ES版本为6.4.0。

![ES信息](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210109205211.png)



添加测试数据：

```shell
PUT /my_index/my_type/1
{
    "title": "Quick brown rabbits",
    "body":  "Brown rabbits are commonly seen."
}

PUT /my_index/my_type/2
{
    "title": "Keeping pets healthy",
    "body":  "My quick brown fox eats rabbits on a regular basis."
}
```





## 一、bool

bool查询，加入explain=true查看scoring细节：

```shell
curl localhost:9200/test/t1/_search?explain=true

{
    "query": {
        "bool": {
            "should": [
                {
                    "match": {
                        "title": "brown fox"
                    }
                },
                {
                    "match": {
                        "body": "brown fox"
                    }
                }
            ]
        }
    }
}
```

结果：

```json
{
    "took": 35,
    "timed_out": false,
    "_shards": {
        "total": 5,
        "successful": 5,
        "skipped": 0,
        "failed": 0
    },
    "hits": {
        "total": 2,
        "max_score": 0.90425634,
        "hits": [
            {
                "_shard": "[test][3]",
                "_node": "Pj5kK5RaSq2K6FCefYOndQ",
                "_index": "test",
                "_type": "t1",
                "_id": "Gznx5nYBq3EYBRDnWgZe",
                "_score": 0.90425634,
                "_source": {
                    "title": "Quick brown rabbits",
                    "body": "Brown rabbits are commonly seen."
                },
                "_explanation": {
                    "value": 0.90425634,
                    "description": "sum of:",
                    "details": [
                        {
                            "value": 0.6931472,
                            "description": "sum of:",
                            "details": [
                                {
                                    "value": 0.6931472,
                                    "description": "weight(title:brown in 0) [PerFieldSimilarity], result of:",
                                    "details": [
                                        {
                                            "value": 0.6931472,
                                            "description": "score(doc=0,freq=1.0 = termFreq=1.0\n), product of:",
                                            "details": [
                                                {
                                                    "value": 0.6931472,
                                                    "description": "idf, computed as log(1 + (docCount - docFreq + 0.5) / (docFreq + 0.5)) from:",
                                                    "details": [
                                                        {
                                                            "value": 1.0,
                                                            "description": "docFreq",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 2.0,
                                                            "description": "docCount",
                                                            "details": []
                                                        }
                                                    ]
                                                },
                                                {
                                                    "value": 1.0,
                                                    "description": "tfNorm, computed as (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * fieldLength / avgFieldLength)) from:",
                                                    "details": [
                                                        {
                                                            "value": 1.0,
                                                            "description": "termFreq=1.0",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 1.2,
                                                            "description": "parameter k1",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 0.75,
                                                            "description": "parameter b",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 3.0,
                                                            "description": "avgFieldLength",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 3.0,
                                                            "description": "fieldLength",
                                                            "details": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "value": 0.21110918,
                            "description": "sum of:",
                            "details": [
                                {
                                    "value": 0.21110918,
                                    "description": "weight(body:brown in 0) [PerFieldSimilarity], result of:",
                                    "details": [
                                        {
                                            "value": 0.21110918,
                                            "description": "score(doc=0,freq=1.0 = termFreq=1.0\n), product of:",
                                            "details": [
                                                {
                                                    "value": 0.18232156,
                                                    "description": "idf, computed as log(1 + (docCount - docFreq + 0.5) / (docFreq + 0.5)) from:",
                                                    "details": [
                                                        {
                                                            "value": 2.0,
                                                            "description": "docFreq",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 2.0,
                                                            "description": "docCount",
                                                            "details": []
                                                        }
                                                    ]
                                                },
                                                {
                                                    "value": 1.1578947,
                                                    "description": "tfNorm, computed as (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * fieldLength / avgFieldLength)) from:",
                                                    "details": [
                                                        {
                                                            "value": 1.0,
                                                            "description": "termFreq=1.0",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 1.2,
                                                            "description": "parameter k1",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 0.75,
                                                            "description": "parameter b",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 7.5,
                                                            "description": "avgFieldLength",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 5.0,
                                                            "description": "fieldLength",
                                                            "details": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            },
            {
                "_shard": "[test][3]",
                "_node": "Pj5kK5RaSq2K6FCefYOndQ",
                "_index": "test",
                "_type": "t1",
                "_id": "HDnx5nYBq3EYBRDnjwZW",
                "_score": 0.77041245,
                "_source": {
                    "title": "Keeping pets healthy",
                    "body": "My quick brown fox eats rabbits on a regular basis."
                },
                "_explanation": {
                    "value": 0.77041245,
                    "description": "sum of:",
                    "details": [
                        {
                            "value": 0.77041245,
                            "description": "sum of:",
                            "details": [
                                {
                                    "value": 0.16044298,
                                    "description": "weight(body:brown in 0) [PerFieldSimilarity], result of:",
                                    "details": [
                                        {
                                            "value": 0.16044298,
                                            "description": "score(doc=0,freq=1.0 = termFreq=1.0\n), product of:",
                                            "details": [
                                                {
                                                    "value": 0.18232156,
                                                    "description": "idf, computed as log(1 + (docCount - docFreq + 0.5) / (docFreq + 0.5)) from:",
                                                    "details": [
                                                        {
                                                            "value": 2.0,
                                                            "description": "docFreq",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 2.0,
                                                            "description": "docCount",
                                                            "details": []
                                                        }
                                                    ]
                                                },
                                                {
                                                    "value": 0.88,
                                                    "description": "tfNorm, computed as (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * fieldLength / avgFieldLength)) from:",
                                                    "details": [
                                                        {
                                                            "value": 1.0,
                                                            "description": "termFreq=1.0",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 1.2,
                                                            "description": "parameter k1",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 0.75,
                                                            "description": "parameter b",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 7.5,
                                                            "description": "avgFieldLength",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 10.0,
                                                            "description": "fieldLength",
                                                            "details": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "value": 0.6099695,
                                    "description": "weight(body:fox in 0) [PerFieldSimilarity], result of:",
                                    "details": [
                                        {
                                            "value": 0.6099695,
                                            "description": "score(doc=0,freq=1.0 = termFreq=1.0\n), product of:",
                                            "details": [
                                                {
                                                    "value": 0.6931472,
                                                    "description": "idf, computed as log(1 + (docCount - docFreq + 0.5) / (docFreq + 0.5)) from:",
                                                    "details": [
                                                        {
                                                            "value": 1.0,
                                                            "description": "docFreq",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 2.0,
                                                            "description": "docCount",
                                                            "details": []
                                                        }
                                                    ]
                                                },
                                                {
                                                    "value": 0.88,
                                                    "description": "tfNorm, computed as (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * fieldLength / avgFieldLength)) from:",
                                                    "details": [
                                                        {
                                                            "value": 1.0,
                                                            "description": "termFreq=1.0",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 1.2,
                                                            "description": "parameter k1",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 0.75,
                                                            "description": "parameter b",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 7.5,
                                                            "description": "avgFieldLength",
                                                            "details": []
                                                        },
                                                        {
                                                            "value": 10.0,
                                                            "description": "fieldLength",
                                                            "details": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
}
```



分析_explaination部分可以看出，计算过程：

* 1）计算match子句内部每个term的score，结果相加作为match子句（即每个field）的score；比如doc2对于match子句

  ```shell
  "match": {
  	"body": "brown fox"
  }
  ```

  的score为

  ```shell
  "value": 0.77041245,
  "description": "sum of:",
  "details": [
  	{
          "value": 0.16044298,
          "description": "weight(body:brown in 0) [PerFieldSimilarity], result of:",
          "details": [
              ...
          ]
  	},
  	
  	{
  		"value": 0.6099695,
          "description": "weight(body:fox in 0) [PerFieldSimilarity], result of:",
          "details": [
              ...
          ]
  	}
   ]
  ```

* 2）每个match子句（即每个field）的score相加，作为doc对应于should的score，比如doc1最终的score计算为：

  ```shell
  "value": 0.90425634,
  "description": "sum of:",
  "details": [
  	{
          "value": 0.6931472,
          "description": "sum of:",
          "details": [
              {
              "value": 0.6931472,
              "description": "weight(title:brown in 0) [PerFieldSimilarity], result of:",
              "details": [
                  ...
              ]
      }，
      {
          "value": 0.21110918,
          "description": "sum of:",
          "details": [
          {
              "value": 0.21110918,
              "description": "weight(body:brown in 0) [PerFieldSimilarity], result of:",
              "details": [
              	...
              ]
          }
      }
  ]
  ```

* 3）因为该查询只有一个should子句，所以should子句的socre作为最终score返回。

  

***PS：根据《ElasticSearch权威指南》(基于ES2.x)，步骤三的时候实际要乘以 （匹配语句的总数）/ （所有语句总数）作为最终的score。***

***同样的测试语句，书中给出的计算过程截图：***

![ES权威指南给出的scoring过程](C:\Users\zhouguangwei01\AppData\Roaming\Typora\typora-user-images\image-20210109205327826.png)

***此次基于ES6.4测试，发现没有3、4两个步骤。***



## 二、dis_max

* 问题：分析上文bool查询的计算过程，可以看出，命中的match子句越多，文档的score也就倾向于越高。所以，bool最后查到的实际是在匹配的field更多的docs。假如想查到，和某个field（title或者body）匹配度最高的docs，bool查询并不能满足需求。

对此，可使用dis_max查询，不再将每个field的score相加、而是使用Max_Score(field_1, field_2...field_n)作为最终的score。

构造查询：

```shell
curl localhost:9200/test/t1/_search?explain=true

{
    "query": {
        "bool": {
            "should": [
                {
                    "match": {
                        "title": "brown fox"
                    }
                },
                {
                    "match": {
                        "body": "brown fox"
                    }
                }
            ]
        }
    }
}
```

返回结果：

```yaml
---
took: 17
timed_out: false
_shards:
  total: 5
  successful: 5
  skipped: 0
  failed: 0
hits:
  total: 2
  max_score: 0.90425634
  hits:
  - _shard: "[test][3]"
    _node: "Pj5kK5RaSq2K6FCefYOndQ"
    _index: "test"
    _type: "t1"
    _id: "Gznx5nYBq3EYBRDnWgZe"
    _score: 0.90425634
    _source:
      title: "Quick brown rabbits"
      body: "Brown rabbits are commonly seen."
    _explanation:
      value: 0.90425634
      description: "sum of:"
      details:
      - value: 0.6931472
        description: "sum of:"
        details:
        - value: 0.6931472
          description: "weight(title:brown in 0) [PerFieldSimilarity], result of:"
          details:
          - value: 0.6931472
            description: "score(doc=0,freq=1.0 = termFreq=1.0\n), product of:"
            details:
            - value: 0.6931472
              description: "idf, computed as log(1 + (docCount - docFreq + 0.5) /\
                \ (docFreq + 0.5)) from:"
              details:
              - value: 1.0
                description: "docFreq"
                details: []
              - value: 2.0
                description: "docCount"
                details: []
            - value: 1.0
              description: "tfNorm, computed as (freq * (k1 + 1)) / (freq + k1 * (1\
                \ - b + b * fieldLength / avgFieldLength)) from:"
              details:
              - value: 1.0
                description: "termFreq=1.0"
                details: []
              - value: 1.2
                description: "parameter k1"
                details: []
              - value: 0.75
                description: "parameter b"
                details: []
              - value: 3.0
                description: "avgFieldLength"
                details: []
              - value: 3.0
                description: "fieldLength"
                details: []
      - value: 0.21110918
        description: "sum of:"
        details:
        - value: 0.21110918
          description: "weight(body:brown in 0) [PerFieldSimilarity], result of:"
          details:
          - value: 0.21110918
            description: "score(doc=0,freq=1.0 = termFreq=1.0\n), product of:"
            details:
            - value: 0.18232156
              description: "idf, computed as log(1 + (docCount - docFreq + 0.5) /\
                \ (docFreq + 0.5)) from:"
              details:
              - value: 2.0
                description: "docFreq"
                details: []
              - value: 2.0
                description: "docCount"
                details: []
            - value: 1.1578947
              description: "tfNorm, computed as (freq * (k1 + 1)) / (freq + k1 * (1\
                \ - b + b * fieldLength / avgFieldLength)) from:"
              details:
              - value: 1.0
                description: "termFreq=1.0"
                details: []
              - value: 1.2
                description: "parameter k1"
                details: []
              - value: 0.75
                description: "parameter b"
                details: []
              - value: 7.5
                description: "avgFieldLength"
                details: []
              - value: 5.0
                description: "fieldLength"
                details: []
  - _shard: "[test][3]"
    _node: "Pj5kK5RaSq2K6FCefYOndQ"
    _index: "test"
    _type: "t1"
    _id: "HDnx5nYBq3EYBRDnjwZW"
    _score: 0.77041245
    _source:
      title: "Keeping pets healthy"
      body: "My quick brown fox eats rabbits on a regular basis."
    _explanation:
      value: 0.77041245
      description: "sum of:"
      details:
      - value: 0.77041245
        description: "sum of:"
        details:
        - value: 0.16044298
          description: "weight(body:brown in 0) [PerFieldSimilarity], result of:"
          details:
          - value: 0.16044298
            description: "score(doc=0,freq=1.0 = termFreq=1.0\n), product of:"
            details:
            - value: 0.18232156
              description: "idf, computed as log(1 + (docCount - docFreq + 0.5) /\
                \ (docFreq + 0.5)) from:"
              details:
              - value: 2.0
                description: "docFreq"
                details: []
              - value: 2.0
                description: "docCount"
                details: []
            - value: 0.88
              description: "tfNorm, computed as (freq * (k1 + 1)) / (freq + k1 * (1\
                \ - b + b * fieldLength / avgFieldLength)) from:"
              details:
              - value: 1.0
                description: "termFreq=1.0"
                details: []
              - value: 1.2
                description: "parameter k1"
                details: []
              - value: 0.75
                description: "parameter b"
                details: []
              - value: 7.5
                description: "avgFieldLength"
                details: []
              - value: 10.0
                description: "fieldLength"
                details: []
        - value: 0.6099695
          description: "weight(body:fox in 0) [PerFieldSimilarity], result of:"
          details:
          - value: 0.6099695
            description: "score(doc=0,freq=1.0 = termFreq=1.0\n), product of:"
            details:
            - value: 0.6931472
              description: "idf, computed as log(1 + (docCount - docFreq + 0.5) /\
                \ (docFreq + 0.5)) from:"
              details:
              - value: 1.0
                description: "docFreq"
                details: []
              - value: 2.0
                description: "docCount"
                details: []
            - value: 0.88
              description: "tfNorm, computed as (freq * (k1 + 1)) / (freq + k1 * (1\
                \ - b + b * fieldLength / avgFieldLength)) from:"
              details:
              - value: 1.0
                description: "termFreq=1.0"
                details: []
              - value: 1.2
                description: "parameter k1"
                details: []
              - value: 0.75
                description: "parameter b"
                details: []
              - value: 7.5
                description: "avgFieldLength"
                details: []
              - value: 10.0
                description: "fieldLength"
                details: []

```

分析_explantion，可以看出计算过程：

* 1）计算每个term的score，相加作为field的score；

* 2）选取前一步计算结果中最大的score作为doc的score返回。

  

### tie_breaker

加入tie_breaker后，综合考虑其他field的score。计算过程变为：

* 1）计算每个term的score，相加作为field的score；
* 2）选取前一步计算结果中最大的score，其他field的score的总和乘以tie_breaker，与max_score相加的和作为doc的score返回。即doc_score = max_score + tie_breaker * (score_field_1 + score_field_2 + ... + score_field_n)。

```shell
{
    "query": {
        "dis_max": {
            "queries": [
                {
                    "match": {
                        "title": "brown fox"
                    }
                },
                {
                    "match": {
                        "body": "brown fox"
                    }
                }
            ],

            "tie_breaker": 0.3
        }
    }
}
```



## 三、multi_match



### 1、best_fields

```shell
curl localhost:9200/test/t1/_search?explain=true

{
    "query": {
        "multi_match": {
            "query": "brown fox",
            "fields": ["title", "body"]
        }
    }
}
```



```shell
curl localhost:9200/test/t1/_search?explain=true

{
    "query": {
        "multi_match": {
            "query": "brown fox",
            "fields": ["title", "body"],
            "type": "best_fields"
        }
    }
}
```



### 2、most_fields

```shell
curl localhost:9200/test/t1/_search?explain=true

{
    "query": {
        "multi_match": {
            "query": "brown fox",
            "fields": ["title", "body"],
            "type": "most_fields"
        }
    }
}
```



### 3、cross_fields

```shell
curl localhost:9200/test/t1/_search?explain=true

{
    "query": {
        "multi_match": {
            "query": "brown fox",
            "fields": ["title", "body"],
            "type": "cross_fields"
        }
    }
}
```



## 参考

[参考一: ES跨字段查询](https://www.elastic.co/guide/cn/elasticsearch/guide/current/_cross_fields_queries.html)

[参考二: most_fields的问题](https://www.elastic.co/guide/cn/elasticsearch/guide/current/_cross_fields_entity_search.html)

[参考三: _validate, rewrite 输出分析.md](_validate, rewrite 输出分析.md)