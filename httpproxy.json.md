# SWProxy 代理配置说明
### 摘要
swproxy代理是通过httpproxy.json文件进行配置的，文件内容为json格式。通过配置文件，能够直接控制代理进行请求/响应替换、请求/响应数据存储等。

### 字段说明
1、replace字段用于数据替换，store用于数据存储，可以同时配置，对应的值为数组形式。  
2、规则字段介绍如下：  
    a. 数组内为具体的规则，可以同时配置多个。  
    b. 规则字段包括：id、point、match、replace、count、ignorecase、script、store、crossrow。  
    c. 【必填】id为规则的唯一标识，必须填写且唯一，可以通过ID在结果中判断哪条规则匹配到的。  
    d. 【非script必填】point为规则作用的对象，包括：url、reqheader、reqbody、rspheader、rspbody。  
    e. 【非script必填】 match为正则表达式，用于匹配point对象的值，支持中英文等(注意：如果数据经过了URL编码，需要填写编码后的字符串)。 
    f. replace表示数据替换(match正则为需要替换的值，replace为替换成的值)。  
    g. store表示数据存储(match正则为需要满足的条件，store为存储哪些字段)，store中可以存储的数据类型包括：method|url|reqheader|reqbody|proto|code|reason|rspheader|rspbody，如果全部存储只需要填写all即可。  
    h. count为替换的个数，默认为1，当为0的时候表示替换所有。  
    i. ignorecase为true时忽略大小写，默认为false。  
    k. 【script必填】script关键字对应的是处理脚本(不需要带py后缀)，位置需要放置在./scripts/下面，编写参考Base.py。  
    l. crossrow为跨行匹配，仅能用于存储功能且匹配为请求体或响应体的时候。
    m. 每一条规则中script关键字不能和其他关键字同时使用(除了id关键字)。如果同时出现，也会优先script。


### 示例
```
{ 
  "replace": [
    {
      "id": 1,
      "point":"url",
      "match":"ppp",
      "replace":"get",
      "count": 1,
      "ignorecase": true
    },
    {
      "id": 2,
      "script": "replaceua"
    },
    {
      "id": 3,
      "point":"rspheader",
      "match":"ppp",
      "store":"url",
      "count": 1,
      "ignorecase": true
    }
  ],
  "store": [
    {
      "id": 4,
      "script": "storedata"
    },
    {
      "id": 5,
      "point":"rspbody",
      "match":"^\\w+\\(.*?\\)",
      "store":"url|host|rspbody",
      "count": 1,
      "ignorecase": true,
      "crossrow": true
    }
  ]
}
```