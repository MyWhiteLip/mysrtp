import sys
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
import get_item
from collections import Counter
from similarity import simi
from spellchecker import SpellChecker
import numpy as np

spell = SpellChecker()
endpoint_url = "https://query.wikidata.org/sparql"

query = """
SELECT ?item ?itemLabel 
WHERE 
{
      wd:Q125977 wdt:P279 ?item.
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}"""


# UNION {wd:"""+id+""" wdt:P279?item.}
# UNION {wd:"""+id+""" wdt:P361?item.}
def get_querylist_p31(ids):
    querylist = []
    for id in ids:
        query = """
        SELECT ?item ?itemLabel 
        WHERE 
        {
             {wd:""" + id + """ wdt:P31?item.} 
            
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        }"""
        querylist.append(query)
    return querylist


def get_querylist_p361(ids):
    querylist = []
    for id in ids:
        query = """
        SELECT ?item ?itemLabel 
        WHERE 
        {
             {wd:""" + id + """ wdt:P361?item.} 

            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        }"""
        querylist.append(query)
    return querylist


def get_querylist_p279(ids):
    querylist = []
    for id in ids:
        query = """
        SELECT ?item ?itemLabel 
        WHERE 
        {
             {wd:""" + id + """ wdt:P279?item.} 

            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        }"""
        querylist.append(query)
    return querylist


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


print("sb程序跑不动")


# 初筛选出三个可能的候选
def get_type(label_list):
    description = ''
    results_list_P31 = []
    # 获取候选实体id,以及它们的描述拼接
    for label in label_list:
        candidate, text = get_item.get_item(label)
        description += text
        for query in get_querylist_p31(candidate):
            results_list_P31.append(get_results(endpoint_url, query))

    type_list = []
    # 获取p31,p279,p361属性
    for results in results_list_P31:
        for result in results["results"]["bindings"]:
            type_list.append(
                (result['item']['value'].replace('http://www.wikidata.org/entity/', ''), result['itemLabel']['value']))

    # 统计出现最多的type
    collection_words = Counter(type_list)
    most_counterNum = collection_words.most_common(5)
    most_ids = []
    results_list_P279 = []
    for type in most_counterNum:
        most_ids.append(type[0][0])
    querylist_P279 = get_querylist_p279(most_ids)
    for query in querylist_P279:
        results_list_P279.append(get_results(endpoint_url, query))
    f = False
    ans_279 = []
    for i in range(len(most_counterNum)):
        for result in results_list_P279[i]['results']['bindings']:
            for j in range(len(most_counterNum)):
                if i != j and most_counterNum[j][0][0] == result['item']['value'].replace(
                        'http://www.wikidata.org/entity/', ''):
                    ans_279.append(most_counterNum[j])
                    f = True
    if f:
        return ans_279, description

    return most_counterNum, description


# 过滤
def check(filename, col):
    datafr = pd.read_csv('../source/Tables_Round1/tables/' + filename + '.csv').head(10)
    test_list = list(datafr['col' + col])
    # 错别词纠正
    for i in range(len(test_list)):
        test_list[i] = SpellChecker.correction(self=spell, word=test_list[i])
    mosttype, description = get_type(test_list)
    # 相邻列探查

    for i in range(len(datafr.columns)):
        if i != int(col):
            collection_words = Counter(list(datafr['col' + str(i)]))
            most_counterNum = collection_words.most_common(2)
            if len(most_counterNum) >= 2:
                if most_counterNum[0][1] != most_counterNum[1][1]:
                    for typep in mosttype:
                        if simi.levenshtein(typep[0][1], str(most_counterNum[0][0])) >= 0.6:
                            return typep[0][0], typep[0][1]
            else:
                for typep in mosttype:
                    if simi.levenshtein(typep[0][1], str(most_counterNum[0][0])) >= 0.6:
                        return typep[0][0], typep[0][1]
    # description探查
    type_counter_description = []
    for i in range(len(mosttype)):
        str1 = description
        str2 = mosttype[i][0][1]
        # 消除其它字符
        s = ''.join(filter(str.isalnum, str2))
        num = (len(description) - len(str1.replace(s, ""))) // len(s)
        type_counter_description.append(num)
    return mosttype[type_counter_description.index(max(type_counter_description))][0][0],
           # mosttype[type_counter_description.index(max(type_counter_description))][0][1]


p = pd.read_csv('../source/CTA_Round1_Targets.csv').head(10)
filelist = np.array(pd.read_csv('../source/CTA_Round1_Targets.csv', usecols=[0], header=None).head(100)).tolist()
collist = np.array(pd.read_csv('../source/CTA_Round1_Targets.csv', usecols=[1], header=None).head(100)).tolist()
anslist=np.array(pd.read_csv('../source/GT/CTA/CTA_Round1_gt.csv',usecols=[3],header=None).head(100)).tolist()
print(filelist)
total=0
precise=0

for i in range(100):
    total =total+1;
    if check(str(filelist[i][0]), str(collist[i][0]))==anslist[i]:
        precise = precise+1
        print("正确")
    else:
        print("错误")
print('precise:',precise/total)



