import threading
from collections import Counter
import numpy as np
import csv
import pandas as pd
from spellchecker import SpellChecker
from searchmanage import SearchManage
from deal import get_item
import similarity.simi

spell = SpellChecker()

import torch
from transformers import BertModel, BertTokenizer

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
search_m2 = SearchManage(key='ids', m_num=1000)
search_m1 = SearchManage(key='search', m_num=1000)


def check(item):
    if item[0] == "Q" and item[1:len(item)].isdigit():
        return True
    else:
        return False


def is_number(s):
    try:

        float(s)

        return True

    except ValueError:

        pass

    try:

        import unicodedata

        unicodedata.numeric(s)

        return True

    except (TypeError, ValueError):

        pass

    return False


def getsimi_base_on_bert(sentenceA, sentenceB):
    text_dictA = tokenizer.encode_plus(sentenceA, add_special_tokens=True, return_attention_mask=True)
    input_ids = torch.tensor(text_dictA['input_ids']).unsqueeze(0)
    token_type_ids = torch.tensor(text_dictA['token_type_ids']).unsqueeze(0)
    attention_mask = torch.tensor(text_dictA['attention_mask']).unsqueeze(0)
    resA = model(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
    afterA = resA[1].squeeze(0)
    text_dictB = tokenizer.encode_plus(sentenceB, add_special_tokens=True, return_attention_mask=True)
    input_ids = torch.tensor(text_dictB['input_ids']).unsqueeze(0)
    token_type_ids = torch.tensor(text_dictB['token_type_ids']).unsqueeze(0)
    attention_mask = torch.tensor(text_dictB['attention_mask']).unsqueeze(0)
    resB = model(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
    afterB = resB[1].squeeze(0)
    return torch.cosine_similarity(afterA, afterB, dim=0).data.item()


def writetocsv(result):
    # python2可以用file替代open
    with open("test1.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # 先写入columns_name
        # 写入多行用writerows
        writer.writerow(result)


# 给定
word = SpellChecker.correction(self=spell, word="Gondolin Cdve")
print(word)
def start_search(points1, points2):
    search_1 = search_m1.search_run(points=points1, keys='id')
    re1=search_1["id"]
    re2 = search_m1.search_run(points=points2, keys='all')["id"]
    re3 = search_m2.search_run(points=re1,
                               keys=['claims/P/value'])['claims/P/value']
    return re1, re2, re3
def start_write(i,index,re2,re3,search2,filelist,collist_1,collist_2):
    result=[]
    result.append(filelist[index][0])
    result.append(collist_1[index][0])
    result.append(collist_2[index][0])
    text = []
    puretext = []
    value = re2[i]
    cont = re3[i]
    allans = []
    for k in range(len(value)):
        puretext.append(search2[i][k])
        if len(value[k]) == 0:
            id_list = []
            text.append(id_list)
        else:
            id_list = []
            for id in value[k]:
                id_list.append(id)
            text.append(id_list)
    for k in range(min(len(cont), len(value))):
        if len(cont[k]) == 0:
            continue
        else:
            ans = cont[k]
            for j in range(len(ans)):
                mark = 0
                tempmark = 0
                tempans = ""
                for key in ans[j]:
                    flag = False
                    for item in ans[j][key]:
                        if check(str(item)):
                            if str(item) in text[k]:
                                tempans = key
                                flag = True
                                break
                            else:
                                continue

                        if is_number(puretext[k]) and is_number(str(item)[1:len(str(item))]) and (
                                str(item)[0] == "+" or str(item)[0] == "-"):
                            num1 = float(puretext[k])
                            num2 = float(str(item))
                            if num2 != 0:
                                if abs((num1 - num2) / num2) < 0.2:
                                    tempans = key
                                    flag = True
                                    break
                                else:
                                    continue
                        if similarity.simi.levenshtein(str(item),puretext[k]) > 0.5 or similarity.simi.ratio_similarity(str(item),puretext[k]) > 0.5:
                            if str(item) == puretext[k]:
                                tempans = key
                                flag = True
                                break
                            tempmark = getsimi_base_on_bert(str(item), puretext[k])
                            if tempmark > 0.95 and tempmark > mark:
                                tempans = key
                                mark = tempmark
                    if flag:
                        break
                if tempans != "":
                    allans.append(tempans)
    collection_words = Counter(allans)
    most_counterNum = collection_words.most_common(3)
    if (len(most_counterNum) == 0):
        result.append("noans")
    elif most_counterNum[0][0] == "P31" and len(most_counterNum) >= 2:
        result.append("http://www.wikidata.org/prop/direct/" + most_counterNum[1][0])
        writetocsv(result)
    else:
        result.append("http://www.wikidata.org/prop/direct/" + most_counterNum[0][0])
        writetocsv(result)
def cpa_search(num,start,end):
    search1 = []
    search2 = []
    filelist = np.array(
        pd.read_csv('/content/mysrtp/deal/Valid/gt/cpa_gt.csv', usecols=[0], header=None).iloc[start:end]).tolist()
    collist_1 = np.array(
        pd.read_csv('/content/mysrtp/deal/Valid/gt/cpa_gt.csv', usecols=[1], header=None).iloc[start:end]).tolist()
    collist_2 = np.array(
        pd.read_csv('/content/mysrtp/deal/Valid/gt/cpa_gt.csv', usecols=[2], header=None).iloc[start:end]).tolist()
    for m in range(len(filelist)):
        file = "/content/mysrtp/deal/Valid/tables/" + filelist[m][0] + ".csv"
        # 对指定列前五行CEA查询
        filecollist_1 = np.array(pd.read_csv(file , usecols=[collist_1[m][0]], header=None).head(10)).tolist()
        filecollist_2 = np.array(pd.read_csv(file, usecols=[collist_2[m][0]], header=None).head(10)).tolist()
        points1 = []    
        points2 = []
        for i in range(min(len(filecollist_1),len(filecollist_2))):
            if i!=0 and not pd.isna(filecollist_1[i][0]) and not pd.isna(filecollist_2[i][0]):
                points1.append(filecollist_1[i][0])
                points2.append(filecollist_2[i][0])
        search1.append(points1)
        search2.append(points2)
        if (m +1 ) % num==0:
            re1, re2, re3 = start_search(search1, search2)
            for i in range(len(re2)):
                index = m - num + i + 1
                threading.Thread(target= start_write,args=(i,index,re2,re3,search2,filelist,collist_1,collist_2)).start()
            search1 = []
            search2 = []


cpa_search(319,0,319)

# 对cell1与cell2进行cea查询，若能都出结果，则直接进行查询
def cpa_1(qid_1, qid_2):
    qid_1_claims = get_item.get_claims(qid_1);
    qid_2_claims = get_item.get_claims(qid_2)
    result = {'ans': ''}
    dic = {}
    for key in qid_1_claims:
        for candidate in qid_1_claims[key]:
            if candidate['mainsnak']['datatype'] == 'wikibase-item':
                if qid_2 == candidate['mainsnak']['datavalue']['value']['id']:
                    result['ans'] = candidate['mainsnak']['property']
    return result


# 其中一者出结果
def cpa_2(qid_1, item):
    qid_1_claims = get_item.get_claims(qid_1);
    # 错别字纠正
    item = SpellChecker.correction(self=spell, word=item)
    result = {'ans': ''}
    mark = 0
    for key in qid_1_claims:
        for candidate in qid_1_claims[key]:
            if candidate['mainsnak']['datatype'] != 'wikibase-item':
                type = candidate['mainsnak']['datavalue']['type']
                if type == 'string':
                    tempmark = getsimi_base_on_bert(item, candidate['mainsnak']['datavalue']['type'])
                    if tempmark >= 0.9 and tempmark > mark:
                        mark = tempmark
                        result['ans'] = candidate['mainsnak']['property']
                elif type == "quantity" and item.isdigit():
                    amount = candidate['mainsnak']['datavalue']['value']['amount']
                    tempmark = getsimi_base_on_bert(item, amount)
                    if tempmark >= 0.9 and tempmark > mark:
                        mark = tempmark
                        result['ans'] = candidate['mainsnak']['property']
                elif type == "time":
                    amount = candidate['mainsnak']['datavalue']['value']['time']
                    tempmark = getsimi_base_on_bert(item, amount)
                    if tempmark >= 0.9 and tempmark > mark:
                        mark = tempmark
                        result['ans'] = candidate['mainsnak']['property']

    return result
