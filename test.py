# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/7/21 
# @function: test for searchmanage
# @version : V0.4.1
#

from searchmanage import SearchManage, Wikipedia, SparqlQuery, BingQuery, Tools, SpellCheck
search_m2 = SearchManage(key='ids', m_num=1000)
re1=search_m2.search_run(points=["Q100"],keys=["labels"])
print(re1)