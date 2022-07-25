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
search_m2 = SearchManage(key='ids', m_num=10)
search_m1 = SearchManage(key='search', m_num=10)


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
filelist = np.array(
    pd.read_csv('D:/mysrtp/deal/Test/target/cpa_target.csv', usecols=[0], header=None).iloc[580:1000]).tolist()
collist_1 = np.array(
    pd.read_csv('D:/mysrtp/deal/Test/target/cpa_target.csv', usecols=[1], header=None).iloc[580:1000]).tolist()
collist_2 = np.array(
    pd.read_csv('D:/mysrtp/deal/Test/target/cpa_target.csv', usecols=[2], header=None).iloc[580:1000]).tolist()
print(filelist)

search1 = []
search2 = []


def start_search(points1, points2):


for m in range(len(filelist)):
    result = []
    file = "D:/mysrtp/deal/Test/tables/" + filelist[m][0] + ".csv"
    result.append(filelist[m][0])
    result.append(collist_1[m][0])
    result.append(collist_2[m][0])
    # 对指定列前五行CEA查询
    filecollist_1 = np.array(pd.read_csv(file, usecols=[collist_1[m][0]], header=None).head(7)).tolist()
    filecollist_2 = np.array(pd.read_csv(file, usecols=[collist_2[m][0]], header=None).head(7)).tolist()
    points1 = []
    points2 = []
    for cell1 in filecollist_1:
        if cell1[0] != "col0":
            word = SpellChecker.correction(self=spell, word=cell1[0])
            points1.append(word)
    print(points1)
    re1 = search_m1.search_run(points=points1, keys='all')
    for cell2 in filecollist_2:
        if cell2[0] != "col" + str(collist_2[m][0]):
            word = SpellChecker.correction(self=spell, word=cell2[0])
            points2.append(word)
    re2 = search_m1.search_run(points=points2, keys='all')
    cont = re1['id']
    value = re2['id']
    text = []
    puretext = []
    for i in range(len(value)):
        puretext.append(filecollist_2[i + 1][0])
        if len(value[i]) == 0:
            id_list = []
            text.append(id_list)
        else:
            id_list = []
            for id in value[i]:
                id_list.append(id)
            text.append(id_list)
    # 对于cea若查到返回id，若查不到返回字符串
    print(text)
    print(cont)
    allans = []
    for i in range(len(cont)):
        if len(cont[i]) == 0:
            continue
        else:
            re2 = search_m2.search_run(points=cont[i],
                                       keys=['claims/P/value'])
            ans = re2["claims/P/value"]
            for j in range(len(ans)):
                mark = 0
                tempmark = 0
                tempans = ""
                for key in ans[j]:
                    flag = False
                    for item in ans[j][key]:
                        if is_number(puretext[i]) and is_number(str(item)[1:len(str(item))]) and (
                                str(item)[0] == "+" or str(item)[0] == "-"):
                            num1 = float(puretext[i])
                            num2 = float(str(item))
                            if num2 != 0:
                                if abs((num1 - num2) / num2) < 0.15:
                                    tempans = key
                                    flag = True
                                    break
                        if similarity.simi.levenshtein(str(item), puretext[i]) > 0.3 or str(item) in text[
                            i] or similarity.simi.ratio_similarity(str(item), puretext[i]) > 0.5:
                            if str(item) in text[i] or str(item) == puretext[i]:
                                tempans = key
                                flag = True
                                break
                            if check(str(item)):
                                continue
                            tempmark = getsimi_base_on_bert(str(item), puretext[i])
                            if tempmark > 0.94 and tempmark > mark:
                                tempans = key
                                mark = tempmark
                                print(tempmark)
                    if flag:
                        break
                if tempans != "":
                    allans.append(tempans)
    collection_words = Counter(allans)
    most_counterNum = collection_words.most_common(3)
    if (len(most_counterNum) == 0):
        result.append("noans")
    elif most_counterNum[0][0] == "P31":
        result.append("http://www.wikidata.org/prop/direct/" + most_counterNum[1][0])
    else:
        result.append("http://www.wikidata.org/prop/direct/" + most_counterNum[0][0])
    writetocsv(result)


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
    dic = {}
    type = ""
    mark = 0
    tempmark = 0
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
