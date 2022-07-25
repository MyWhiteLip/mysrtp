# ReadMe

- **author  : Shuxin_Wang**
- **email   : 213202122@seu.edu.cn**
- **time    : 2022/6/2**



## V1

- 简单查询，只有`SearchManage`一个查询类，单线程查询，简单解析；



## V2

- 新增`Entities`,`EntitiesSearch`基本类，`Tools.py`提供功能函数接口;
- 支持多线程查询，支持N维列表数据输入；



## V3



- 新增解析工具函数，解析类，**（key='ids'时）支持正则表达目标解析，支持自定义解析函数的接口**；
- 支持wikidata数据模型中7种**值类型**数据的解析；
- 重新规划文件位置，类`SearchManage`作为类`EntitiesSearch`的子类
- 修复线程数过大导致的错误；



## 解析关键词规范

1. labels,descriptions,aliases

   以`labels`为例子

   - `labels`,`labels/`,`labels//`→labels下字典
   - `labels/xx`→`xx`语言下的值

2. claims

   - `claims`,`claims/`,`claims//`→claims下字典
   - `claims/P`,`claims/P/`,`claims/P//`→属性ID列表
   - `claims/P/value`→所有属性下的值
   - `claims/Pxx`,`claims/Pxx/`,`claims/Pxx//`→`Pxx`下的字典
   - `claims/Pxx/value`→`Pxx`的具体值
   - `claims/Pxx/qualifiers-order`→`Pxx`限定词顺序列表
   - `claims/Pxx/qualifiers`,`claims/Pxx/qualifiers/`,`claims/Pxx/qualifiers//`→`Pxx`限定词下字典
   - `claims/Pxx/references`,`claims/Pxx/references/`,`claims/Pxx/references//`→`Pxx`引用下字典

3. sitelinks

   - `sitelinks`,`sitelinks/`,`sitelinks//`→外部链接下的字典



## 7种值类型解析结果

- 列首的整数表示该值类型解析几个**主值**

```python
# Wikidata Value-type
value_type = {
    'wikibase-entityid': [1, 'id', 'entity-type', 'numeric-id'],
    'globecoordinate': [2, 'latitude', 'longitude', 'precision', 'globe'],
    'time': [1, 'time', 'precision', 'before', 'after', 'timezone'],
    'string': None,
    'monolingualtext': [2, 'text', 'language'],
    'quantity': [1, 'amount', 'lowerBound', 'upperBound']
}
```

