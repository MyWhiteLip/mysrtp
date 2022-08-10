import threading
import numpy as np
import csv
import pandas as pd
from spellchecker import SpellChecker
import gl
import searchmanage.entities.Entities
import similarity.simi
from searchmanage import SearchManage
from test import get_correct_id
spell = SpellChecker()

import torch
from transformers import BertModel, BertTokenizer

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
search_m2 = SearchManage(key='ids', m_num=1000)
search_m1 = SearchManage(key='search', m_num=1000)
print("yest")


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


def writetocsv(result):
    # python2可以用file替代open
    with open("test/test.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # 先写入columns_name
        # 写入多行用writerows
        writer.writerow(result)


def check(item):
    if item[0] == "Q" and item[1:len(item)].isdigit():
        return True
    else:
        return False


def getmark(A, B):
    if is_number(A) and is_number(B):
        if float(B) != 0:
            return 1 - abs((float(A) - float(B)) / float(B))
    else:
        return similarity.simi.ratio_similarity(A, B)


def start_search(points1):
    search_1 = search_m1.search_run(points=points1, keys='id')
    re1 = search_1["id"]
    # re2 = search_m2.search_run(points=re1,
    #                            keys=['claims/P/value'])['claims/P/value']
    # points2 = []
    # text2 = []
    # for i in range(len(re2)):
    #     templist1 = []
    #     textlist1 = []
    #     for item in re2[i]:
    #         textlist2 = ""
    #         templist2 = []
    #         for key in item:
    #             for claim in item[key]:
    #                 if claim[0]=="wikibase-entityid":
    #                     templist2.append(claim[1])
    #                 elif claim[0]!="quantity" :
    #                     textlist2 += str(claim[1])
    #         textlist1.append(textlist2)
    #         templist1.append(templist2)
    #     text2.append(textlist1)
    #     points2.append(templist1)
    # re3 = search_m2.search_run(points=points2, keys=['labels'])['labels']
    # list1 = []
    # for i in range(len(re3)):
    #     list2 = []
    #     for j in range(len(re3[i])):
    #         temptext = ""
    #         for item3 in re3[i][j]:
    #             for key in item3:
    #                 temptext += item3[key]["value"]
    #         temptext += text2[i][j]
    #         list2.append(temptext)
    #     list1.append(list2)
    return re1


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


def start_write(index, re1, text_col, result):
    result_1 = result
    tempmark = 0
    ans = ""
    for i in range(len(re1)):
        if re1[i] in gl.keymap:
            claim_mark = 0
            for item in text_col:
                mark_item = 0
                for claim in gl.keymap[re1[i]]:
                    tempmark_item = getmark(item, claim)
                    if tempmark_item > mark_item:
                        mark_item = tempmark_item
                claim_mark += mark_item
            if claim_mark > tempmark:
                ans = re1[i]
                tempmark = claim_mark
    if ans != "":
        result_1.append(ans)
        writetocsv(result_1)

valid_path="DataSets/ToughTablesR2-WD/Valid/gt/cea_gt.csv"
test_path="DataSets/ToughTablesR2-WD/Test/target/cea_target.csv"
points = []
text = []
file_temp = {}


def startserach(start, end, freq,path=""):
    global points, text
    filelist = np.array(
        pd.read_csv(path+valid_path, usecols=[0], header=None).iloc[start:end]).tolist()
    rowlist_1 = np.array(
        pd.read_csv(path+valid_path, usecols=[1], header=None).iloc[start:end]).tolist()
    collist_1 = np.array(
        pd.read_csv(path+valid_path, usecols=[2], header=None).iloc[start:end]).tolist()
    for m in range(len(filelist)):
        df = None
        if filelist[m][0] not in file_temp:
            file = path+"DataSets/ToughTablesR2-WD/Valid/tables/" + filelist[m][0] + ".csv"
            df = pd.read_csv(file, header=None)
            file_temp[filelist[m][0]] = df
        else:
            df = file_temp.get(filelist[m][0])
        length = df.shape[1]
        col_text = []
        for i in range(length):
            if not pd.isna(df.iloc[rowlist_1[m][0], i]) and i != collist_1[m][0]:
                col_text.append(df.iloc[rowlist_1[m][0], i])
        keyword = df.iloc[rowlist_1[m][0], collist_1[m][0]]
        points.append(keyword)
        text.append(col_text)
        if (m + 1) % freq == 0:
            re1 = start_search(points)
            for i in range(len(re1)):
                index = m - freq + i + 1
                result = []
                result.append(filelist[index][0])
                result.append(rowlist_1[index][0])
                result.append(collist_1[index][0])
                if len(re1[i]) != 0:
                    threading.Thread(target=start_write,
                                     args=(i, re1[i], text[i], result)).start()
            points = []
            text = []


startserach(2638, 3638, 1000)
