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

search_m2 = SearchManage(key='ids', m_num=40000)
search_m1 = SearchManage(key='search', m_num=1000)


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

def writetocsv_other(result):
    with open("test/test_other.csv", "a", newline="") as csvfile:
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
        return similarity.simi.levenshtein(A, B)


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


def start_write(thisword, re1, text_col, result, col):
    result_1 = result
    tempmark = 0
    ans = ""
    if str(col) != "0":
        key = str(result_1[0]) + " " + str(result_1[1])
        if key in gl.result:
            QID = gl.result[key]
            if QID in gl.idmap:
                for id in re1:
                    if id in gl.idmap[QID]:
                        ans = id
                        break
    if str(col) != "0" and ans == "":
        key = str(result_1[0]) + " " + str(result_1[1])
        if key in gl.result:
            QID = gl.result[key]
            if QID in gl.keymap:
                claim_list = gl.keymap[QID]
                label_score = 0
                for id in re1:
                    label_mark = 0
                    if id in gl.labelmap:
                        for claim in claim_list:
                            label_mark = max(label_mark, similarity.simi.ratio_similarity(gl.labelmap[id], claim))
                    if label_mark > label_score:
                        label_score = label_mark
                        ans = id
                if label_score < 0.7:
                    ans = ""
    if str(col) != "0" and ans == "":
        item_mark = 0
        for id in re1:
            if id in gl.labelmap:
                tempscore = similarity.simi.ratio_similarity(thisword, gl.labelmap[id])
                if tempscore > item_mark:
                    ans = id
                    item_mark = tempscore
        if item_mark < 0.7:
            ans = ""
    if ans == "":
        if len(re1) == 1:
            ans=re1[0]
        else:
            for i in range(len(re1)):
                if re1[i] in gl.keymap:
                    claim_mark = 0
                    if re1[i] in gl.labelmap:
                        claim_mark = similarity.simi.ratio_similarity(gl.labelmap[re1[i]], thisword)
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
                    elif claim_mark == tempmark and re1[i] in gl.labelmap and ans in gl.labelmap:
                        score1 = similarity.simi.ratio_similarity(gl.labelmap[re1[i]], thisword)
                        score2 = similarity.simi.ratio_similarity(gl.labelmap[ans], thisword)
                        if score2 < score1:
                            ans = re1[i]

    if ans != "":
        result_1.append(ans)
        writetocsv(result_1)
        if str(col) == "0":
            gl.result[str(result_1[0]) + " " + str(result_1[1])] = result_1[3]
    else:
        writetocsv_other(result)




valid_path = "DataSets/ToughTablesR2-WD/Valid/gt/cea_gt.csv"
test_path = "DataSets/ToughTablesR2-WD/Test/target/cea_target.csv"
points = []
text = []
file_temp = {}


def startserach(start, end, freq, path=""):
    global points, text
    filelist = np.array(
        pd.read_csv(path + valid_path, usecols=[0], header=None).iloc[start:end]).tolist()
    rowlist_1 = np.array(
        pd.read_csv(path + valid_path, usecols=[1], header=None).iloc[start:end]).tolist()
    collist_1 = np.array(
        pd.read_csv(path + valid_path, usecols=[2], header=None).iloc[start:end]).tolist()
    for m in range(len(filelist)):
        df = None
        if filelist[m][0] not in file_temp:
            file = path + "DataSets/ToughTablesR2-WD/Valid/tables/" + filelist[m][0] + ".csv"
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
                if "," in points[i] and " " in points[i]:
                    word = points[i]
                    word = word.replace(",", "")
                    word = word.replace(" ", "")
                    word = get_correct_id(word)
                    if word is not None:
                        re1[i] = [word]
                if len(re1[i]) != 0:
                    start_write(points[i], re1[i], text[i], result, collist_1[index][0])
            points = []
            text = []


startserach(3623,3624,1)

