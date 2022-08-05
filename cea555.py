# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/7/2 
# @function: CEA
# @version : V1.0 
#


import numpy as np
from preprocess.searchmanage.tools import Tools
import time
import re
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
from fuzzywuzzy import fuzz
from searchmanage import SearchManage, SparqlQuery, BingQuery

endpoint_url = "https://query.wikidata.org/sparql"

def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

# 转为词向量
def word_to_vector(word):
    # 全部转为小写
    word = word.lower()
    # 生成1×27的零向量
    result_arr = np.zeros((1, 27))
    if word == '' or word is None:
        return result_arr
    for w in word:
        index_w = ord(w) - 97
        if 0 <= index_w <= 25:
            result_arr[0][index_w] += 1
        else:
            result_arr[0][26] += 1
    # 归一标准化处理
    result_arr = result_arr / np.max(result_arr)
    return result_arr


# 计算欧式距离
def euclidean_compute(x1, x2):
    x1 = np.array(x1)
    x2 = np.array(x2)
    return np.sqrt(np.sum((x1 - x2) ** 2))


# 找出最短的点
def find_points(labels, label_):
    """
    :param labels: 待匹配标签列表
    :param label_: 匹配标签
    :return: 最相似标签的索引，得匹配标签中是否存在与匹配标签完全相等的点
    """
    label_vector = word_to_vector(label_)
    labels_euclidean = []
    # 计算最短距离
    for label in labels:
        labels_vector = word_to_vector(label)
        labels_euclidean.append(euclidean_compute(label_vector, labels_vector))
    labels_euclidean_sort_index = sorted(range(len(labels_euclidean)), key=lambda k: labels_euclidean[k])
    labels_euclidean_sort = sorted(labels_euclidean)
    result_index = None
    if labels_euclidean_sort[0] == 0.0:
        result_index = []
        for num in range(len(labels_euclidean_sort)):
            if labels_euclidean_sort[num] == 0.0 or labels_euclidean_sort[num] < 1e-8:
                result_index.append(labels_euclidean_sort_index[num])
            else:
                break
    else:
        if len(labels_euclidean_sort) >= 5:
            result_index = labels_euclidean_sort_index[:5]
        else:
            result_index = labels_euclidean_sort_index
    return result_index

if __name__ == "__main__":
    start = time.time()
   
    cea_gt = "cea_target.csv"
    csv_path = "tables/"
    cache_path = "cea111111.csv"
    cccache_path = "cea111112.csv"
    cta_cache = "cta copy.csv"

    s1 = SearchManage(key='search', m_num=100)
    s2 = SearchManage(key='ids', m_num=50)
    b1 = BingQuery(m_num=50)
    sql1 = SparqlQuery(m_num=500, format_='json')

    cta_da, cta_t = Tools.read_csv(cta_cache, is_header=False, out_data_t=True)
    gt_data = Tools.read_csv(cea_gt, is_header=False, out_data_t=False)
    sum_num = len(gt_data)
    # print(sum_data)
    # print(sum_data)
    num_1 = 0
    num_2 = 0
    right_num = 0
    print(f'Cache path:{cache_path}.')
    try:
        cache_data = Tools.read_csv(cache_path, is_header=False, out_data_t=False)
        while num_1 < len(cache_data) and num_2 < len(gt_data):
            if cache_data[num_1][0] == gt_data[num_2][0] and cache_data[num_1][1] == gt_data[num_2][1] and \
                    cache_data[num_1][2] == gt_data[num_2][2]:
                
                if cache_data[num_1][3] !='http://www.wikidata.org/entity/':
                    right_num += 1
                
                num_1 += 1
                num_2 += 1
            else:
                num_1 += 1
        print(f'Accuracy Rate:{(right_num / len(cache_data)) * 100}%')
    except Exception as e:
        print(e)
        num_2 = 0
        cache_data = []
    print(f'CEA Result Num:{len(cache_data)}')
    print(f'Entities Remaining Num:{len(gt_data) - len(cache_data)},Next Search Index:{num_2}')
    c = input('Continue to Run CEA?(y/n):')
    # 运行CEA
    if c.lower() == 'y':
        start = time.time()
        file_name_list = gt_data[num_2:]
        sum_n = 100
        start_ = 0
        n = 0
        while start_ + num_2 < sum_num:
            write_data = []
            need_da = []
            for paths in file_name_list[start_: start_ + sum_n]:
                write_data.append([paths[0], paths[1], paths[2], None])
                da_temp, da_temp_t = Tools.read_csv(csv_path + paths[0] + '.csv', is_print=False)
                need_da.append(da_temp[int(paths[1]) - 1][int(paths[2])])
            start_ += sum_n

            # print(index1)
            re1 = s1.search_run(need_da, keys='all')
            # print(re1)
            # print(re2['P31'])
            re1_ = re1['id']
            re1__ = re1['label']
            

            for i in range(len(need_da)):
                _s_ = 0
                m = 0
                llll=0
                result = 'None'
                for c in range(len(cta_da)):
                    if cta_t[0][c] == write_data[i][0] and cta_t[1][c] == write_data[i][2]:
                        if cta_t[2][c] != "http://www.wikidata.org/entity/None":
                            _s_ = 1
                            if not cta_t[3][c]:
                                _s_ = 2
                        else:
                            _s_ = 3
                        m = c
                        break
                try:
                    if _s_ == 1:
                        cta_index = cta_da[c][3]
                        if cta_index!="[]":
                            lll=cta_index.split('), (')
                            number = re.findall("\d+",lll[int(write_data[i][1])-1])
                            if len(number) == 2:
                                result = 'http://www.wikidata.org/entity/Q'+str(number[0])
                            else:
                                _s_=2

                    if _s_ == 2:
                            p1="None"
                            p2="None"
                            p3="None"
                            p4="None"
                            p5="None"
                            query = """#山羊
                            SELECT ?item ?itemLabel 
                            WHERE 
                            {
                            ?item wdt:P31 wd:"""
                            p = str((cta_t[2][c].split('/')).pop())  
                            if p!='Q5'and p!='Q4167836'and p!='Q101352'and p!='Q16521'and p!='Q4022'and p!='Q79007'and p!='Q3305213'and p!='Q35657'and p!='Q8502'and p!='Q13442814'and p!='Q7187'and p!='Q4167410'and p!='Q7725634'and p!='Q13406463'and p!='Q11266439'and p!='Q55488'and p!='Q13433827'and p!='Q4830453':                 
                                q=""".
                                SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
                                }"""
                                query=query+p+q
                                rs = get_results(endpoint_url, query)

                                for rt in rs["results"]["bindings"]:
                                    if fuzz.ratio(rt['itemLabel']['value'], need_da[i]) >= 80:
                                        p1=(rt['item']['value'].split('/')).pop()
                                        
                                    if fuzz.ratio(rt['itemLabel']['value'], need_da[i]) >= 85:
                                        p2=(rt['item']['value'].split('/')).pop()
                                        
                                    if fuzz.ratio(rt['itemLabel']['value'], need_da[i]) >= 90:
                                        p3=(rt['item']['value'].split('/')).pop()
                                        
                                    if fuzz.ratio(rt['itemLabel']['value'], need_da[i]) >= 95:
                                        p4=(rt['item']['value'].split('/')).pop()
                                        
                                    if fuzz.ratio(rt['itemLabel']['value'], need_da[i]) >= 100:
                                        p5=(rt['item']['value'].split('/')).pop()

                                if p5 != "None":
                                    result = 'http://www.wikidata.org/entity/'+str(p5)
                                elif p4 != "None":
                                    result = 'http://www.wikidata.org/entity/'+str(p4)
                                elif p3 != "None":
                                    result = 'http://www.wikidata.org/entity/'+str(p3)
                                elif p2 != "None":
                                    result = 'http://www.wikidata.org/entity/'+str(p2)
                                elif p1 != "None":
                                    result = 'http://www.wikidata.org/entity/'+str(p1)

                            if result =="None":
                                _s_=3

                    if _s_==3:
                        for c in range(len(re1_[i])):
                            if re1_[i][c]:
                                if fuzz.ratio(re1__[i][c], need_da[i]) >= 80:
                                    result = 'http://www.wikidata.org/entity/'+str(re1_[i][c])
                                    break
                                else:
                                    c=c+1

                    if result =="None":
                        llll=1
                        

                   
                except Exception as e:
                    print(e)
                print(result)
                write_data[i][3] = result
            Tools.data_write_to_csv(cache_path, write_data)
            if llll==1:
                wwrite_data=[]
                wwrite_data.append([paths[0], paths[1], paths[2], need_da[i]])
                Tools.data_write_to_csv(cccache_path, wwrite_data)
            
    end = time.time()
    print(f'Cost time:{end - start}s')
