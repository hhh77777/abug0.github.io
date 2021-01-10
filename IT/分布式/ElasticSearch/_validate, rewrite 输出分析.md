# _validate/rewrite 输出分析

ElasticSearch执行query时会先将query重写成低级的term等查询，内部实际执行的就是重写后的低级query。

通过 _validate/query?rewrite可以查看query重写后的低级query。

本文对rewrite的输出含义进行总结。

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



## 一、bool查询

### 1、must查询：

#### 1） rewrite输出

```shell
curl localhost:9200/test/t1/_validate/query?rewrite=true

{
    "query": {
        "bool": {
            "must": [
                {
                    "match": {
                        "title": "brown rabbits"
                    }
                },
                {
                    "match": {
                        "body": "brown"
                    }
                }
            ]
        }
    }
}
```

```json
{
    "_shards": {
        "total": 1,
        "successful": 1,
        "failed": 0
    },
    "valid": true,
    "explanations": [
        {
            "index": "test",
            "valid": true,
            "explanation": "+(title:brown title:rabbits) +body:brown"
        }
    ]
}
```

explations的输出，可以解释为：

* 1、过滤条件，同时满足如下两个条件：
  * 1）title字段包含term: brown或者fox；
  * 2）body字段包含term: brown
* 2、score计算：两个field的score相加。

***tips: 查询条件中的“+”表示条件必须满足，“-”表示条件必须不满足，无符号表示可选条件 （参考一）***

```
+ 前缀表示必须与查询条件匹配。类似地， - 前缀表示一定不与查询条件匹配。没有 + 或者 - 的所有其他条件都是可选的——匹配的越多，文档就越相关。
```



#### 2） scoring细节

explain看scoring细节：

```shell
curl localhost:9200/test/t1/_search?explain=true&format=yaml

{
    "query": {
        "bool": {
            "must": [
                {
                    "match": {
                        "title": "brown rabbits"
                    }
                },
                {
                    "match": {
                        "body": "brown"
                    }
                }
            ]
        }
    }
}
```



```yaml
took: 18
timed_out: false
_shards:
  total: 5
  successful: 5
  skipped: 0
  failed: 0
hits:
  total: 1
  max_score: 1.5974035
  hits:
  - _shard: "[test][3]"
    _node: "Pj5kK5RaSq2K6FCefYOndQ"
    _index: "test"
    _type: "t1"
    _id: "Gznx5nYBq3EYBRDnWgZe"
    _score: 1.5974035
    _source:
      title: "Quick brown rabbits"
      body: "Brown rabbits are commonly seen."
    _explanation:
      value: 1.5974035
      description: "sum of:"
      details:
      - value: 1.3862944
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
        - value: 0.6931472
          description: "weight(title:rabbits in 0) [PerFieldSimilarity], result of:"
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
        description: "weight(body:brown in 0) [PerFieldSimilarity], result of:"
        details:
        - value: 0.21110918
          description: "score(doc=0,freq=1.0 = termFreq=1.0\n), product of:"
          details:
          - value: 0.18232156
            description: "idf, computed as log(1 + (docCount - docFreq + 0.5) / (docFreq\
              \ + 0.5)) from:"
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
```



**从输出可以看到，doc score = weight(title:brown in 0) + weight(title:rabbits in 0) + weight(body:brown in 0)**



### 2、should查询

#### 1） rewrite输出

```shell
curl localhost:9200/test/t1/_validate/query?rewrite=true

{
    "query": {
        "bool": {
            "should": [
                {
                    "match": {
                        "title": "brown rabbits"
                    }
                },
                {
                    "match": {
                        "body": "brown"
                    }
                }
            ]
        }
    }
}
```

```json
{
    "_shards": {
        "total": 1,
        "successful": 1,
        "failed": 0
    },
    "valid": true,
    "explanations": [
        {
            "index": "test",
            "valid": true,
            "explanation": "(title:brown title:rabbits) body:brown"
        }
    ]
}
```

explations的输出，可以解释为：

* 1、过滤条件，满足如下两个条件之一：
  * 1）title字段包含term: brown或者fox；
  * 2）body字段包含term: brown
* 2、score计算：两个field的score相加。

***tips: 如果两个条件都不满足，实际该文档不会被此次query查到，更谈不上score了***



#### 2） scoring细节

**从输出可以看到，doc score = weight(title:brown in 0) + weight(title:rabbits in 0) + weight(body:brown in 0)**

```shell
curl localhost:9200/test/t1/_search?explain=true&format=yaml

{
    "query": {
        "bool": {
            "must": [
                {
                    "match": {
                        "title": "brown rabbits"
                    }
                },
                {
                    "match": {
                        "body": "brown"
                    }
                }
            ]
        }
    }
}
```

```yaml
---
took: 12
timed_out: false
_shards:
  total: 5
  successful: 5
  skipped: 0
  failed: 0
hits:
  total: 2
  max_score: 1.5974035
  hits:
  - _shard: "[test][3]"
    _node: "Pj5kK5RaSq2K6FCefYOndQ"
    _index: "test"
    _type: "t1"
    _id: "Gznx5nYBq3EYBRDnWgZe"
    _score: 1.5974035
    _source:
      title: "Quick brown rabbits"
      body: "Brown rabbits are commonly seen."
    _explanation:
      value: 1.5974035
      description: "sum of:"
      details:
      - value: 1.3862944
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
        - value: 0.6931472
          description: "weight(title:rabbits in 0) [PerFieldSimilarity], result of:"
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
        description: "weight(body:brown in 0) [PerFieldSimilarity], result of:"
        details:
        - value: 0.21110918
          description: "score(doc=0,freq=1.0 = termFreq=1.0\n), product of:"
          details:
          - value: 0.18232156
            description: "idf, computed as log(1 + (docCount - docFreq + 0.5) / (docFreq\
              \ + 0.5)) from:"
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
    _score: 0.16044298
    _source:
      title: "Keeping pets healthy"
      body: "My quick brown fox eats rabbits on a regular basis."
    _explanation:
      value: 0.16044298
      description: "sum of:"
      details:
      - value: 0.16044298
        description: "weight(body:brown in 0) [PerFieldSimilarity], result of:"
        details:
        - value: 0.16044298
          description: "score(doc=0,freq=1.0 = termFreq=1.0\n), product of:"
          details:
          - value: 0.18232156
            description: "idf, computed as log(1 + (docCount - docFreq + 0.5) / (docFreq\
              \ + 0.5)) from:"
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

```



## 二、multi_match

### 1、best_fields

#### 1）rewrite输出

```shell
curl localhost:9200/test/t1/_validate/query?rewrite
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

```json
{
    "_shards": {
        "total": 1,
        "successful": 1,
        "failed": 0
    },
    "valid": true,
    "explanations": [
        {
            "index": "test",
            "valid": true,
            "explanation": "((body:brown body:fox) | (title:brown title:fox))"
        }
    ]
}
```

explations的输出，可以解释为：

* 1、过滤条件，满足如下条件之一：
  * 1）title字段包含term: brown或者fox；
  * 2）body字段包含term: brown或者fox。
* 2、score计算：
  * 计算每个field的score；
  * field score中取最大值作为doc score。



#### 2）scoring细节

**计算过程总结为：**

* 1）field_score_body = weight(body:brown in 0) + weight(body:fox in 0)
* 2）field_score_title = weight(title:brown in 0) + weight(title:fox 0)
* 3）doc_score = Max(field_score_body, field_score_title)

详细输出如下：

```yaml
---
took: 10
timed_out: false
_shards:
  total: 5
  successful: 5
  skipped: 0
  failed: 0
hits:
  total: 2
  max_score: 0.77041245
  hits:
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
      description: "max of:"
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
  - _shard: "[test][3]"
    _node: "Pj5kK5RaSq2K6FCefYOndQ"
    _index: "test"
    _type: "t1"
    _id: "Gznx5nYBq3EYBRDnWgZe"
    _score: 0.6931472
    _source:
      title: "Quick brown rabbits"
      body: "Brown rabbits are commonly seen."
    _explanation:
      value: 0.6931472
      description: "max of:"
      details:
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

```



### 1-1 tie_breaker

#### 1）rewrite输出

```shell
curl localhost:9200/test/t1/_validate/query?rewrite
{
    "query": {
        "multi_match": {
            "query": "brown fox",
            "fields": ["title", "body"],
            "tie_breaker": 0.7,
            "type": "best_fields"
        }
    }
}
```

```json
{
    "_shards": {
        "total": 1,
        "successful": 1,
        "failed": 0
    },
    "valid": true,
    "explanations": [
        {
            "index": "test",
            "valid": true,
            "explanation": "((body:brown body:fox) | (title:brown title:fox))~0.7"
        }
    ]
}
```

explations的输出，可以解释为：

* 1、过滤条件，满足如下条件之一：
  * 1）title字段包含term: brown或者fox；
  * 2）body字段包含term: brown或者fox。
* 2、score计算：
  * 计算每个field的score；
  * field score中取最大值加上(其他字段 * 0.7)的和作为doc score。



#### 2）scoring细节

**计算过程总结为：**

* 1）field_score_body = weight(body:brown in 0) + weight(body:fox in 0)
* 2）field_score_title = weight(title:brown in 0) + weight(title:fox 0)
* 3）doc_score = Max(field_score_body, field_score_title) + 0.7 * (field_score_*any*) （tips: field_score__*any*表示best_field以外的其他字段的score）

详细输出如下：

```yaml
---
took: 8
timed_out: false
_shards:
  total: 5
  successful: 5
  skipped: 0
  failed: 0
hits:
  total: 2
  max_score: 0.8409236
  hits:
  - _shard: "[test][3]"
    _node: "Pj5kK5RaSq2K6FCefYOndQ"
    _index: "test"
    _type: "t1"
    _id: "Gznx5nYBq3EYBRDnWgZe"
    _score: 0.8409236
    _source:
      title: "Quick brown rabbits"
      body: "Brown rabbits are commonly seen."
    _explanation:
      value: 0.8409236
      description: "max plus 0.7 times others of:"
      details:
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
      description: "max plus 0.7 times others of:"
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



### 2、most_fields

#### 1）rewrite输出

```shell
curl localhost:9200/test/t1/_validate/query?rewrite
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

```json
{
    "_shards": {
        "total": 1,
        "successful": 1,
        "failed": 0
    },
    "valid": true,
    "explanations": [
        {
            "index": "test",
            "valid": true,
            "explanation": "(body:brown body:fox) (title:brown title:fox)"
        }
    ]
}
```

explations的输出，可以解释为：

* 1、过滤条件，满足如下条件之一：
  * 1）title字段包含term: brown或者fox；
  * 2）body字段包含term: brown或者fox。
* 2、score计算：
  * 计算每个field的score；
  * field score相加作为doc score。



#### 2）scoring细节

**计算过程总结为：**

* 1）field_score_body = weight(body:brown in 0) + weight(body:fox in 0)
* 2）field_score_title = weight(title:brown in 0) + weight(title:fox 0)
* 3）doc_score = field_score_body + field_score_title

详细输出如下：

```yaml
---
took: 9
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



### 3、cross_fields

#### 1）rewrite输出

```shell
curl localhost:9200/test/t1/_validate/query?rewrite
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

```json
{
    "_shards": {
        "total": 1,
        "successful": 1,
        "failed": 0
    },
    "valid": true,
    "explanations": [
        {
            "index": "test",
            "valid": true,
            "explanation": "(body:brown | title:brown) (body:fox | title:fox)"
        }
    ]
}
```

explations的输出，可以解释为：

* 1、过滤条件，满足如下条件之一：
  * 1）brown出现在field: title或者body中；
  * 2）fox出现在field: title或者body中；
* 2、score计算：
  * 计算每个term的score：term_score = Max(score_field_body, score_field_title)
  * term score相加作为doc score。



#### 2）scoring细节

**计算过程总结为：**

* 1）term_score_brown = Max(field_score_body, field_score_title) = Max(weight(body:brown in 0), weight(title:brown in 0))
* 2）term_score_fox = Max(field_score_body, field_score_title) = Max(weight(body:fox in 0), weight(title:fox in 0))
* 3）doc_score = term_score_brown + term_score_fox

详细输出如下：

```yaml
---
took: 21
timed_out: false
_shards:
  total: 5
  successful: 5
  skipped: 0
  failed: 0
hits:
  total: 2
  max_score: 0.77041245
  hits:
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
      - value: 0.16044298
        description: "max of:"
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
        description: "max of:"
        details:
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
  - _shard: "[test][3]"
    _node: "Pj5kK5RaSq2K6FCefYOndQ"
    _index: "test"
    _type: "t1"
    _id: "Gznx5nYBq3EYBRDnWgZe"
    _score: 0.21110918
    _source:
      title: "Quick brown rabbits"
      body: "Brown rabbits are commonly seen."
    _explanation:
      value: 0.21110918
      description: "sum of:"
      details:
      - value: 0.21110918
        description: "max of:"
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
        - value: 0.18232156
          description: "weight(title:brown in 0) [PerFieldSimilarity], result of:"
          details:
          - value: 0.18232156
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

```



### 参考

[参考一: ES中的轻量搜索](https://www.elastic.co/guide/cn/elasticsearch/guide/current/search-lite.html)

[参考二: validate API](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-validate.html)

[参考三: 跨字段搜索](https://www.elastic.co/guide/cn/elasticsearch/guide/current/_cross_fields_queries.html)