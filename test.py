# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/7/21 
# @function: test for searchmanage
# @version : V0.4.1
#
import csv
import random
import numpy as np
import pandas as pd
import requests
import wikipedia
from bs4 import BeautifulSoup

import similarity.simi
from searchmanage.tools.Tools import AGENTS_
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
from  gl import state_map
import gl
from searchmanage1.tools.Tools import agents


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


def get_results(QID):
    flag = True
    count = 0
    if QID in gl.keymap:
        return
    while flag:
        count += 1
        endpoint_url = "https://query.wikidata.org/sparql"
        query = """SELECT ?wdLabel ?ps_Label ?wdpqLabel ?pq_Label { 
            VALUES (?company) {(wd:""" + QID + """)} 
    
            ?company ?p ?statement . 
            ?statement ?ps ?ps_ . 
    
            ?wd wikibase:claim ?p. 
            ?wd wikibase:statementProperty ?ps. 
    
            OPTIONAL { 
            ?statement ?pq ?pq_ . 
            ?wdpq wikibase:qualifier ?pq . 
            } 
    
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en" } 
        } ORDER BY ?wd ?statement ?ps_ """
        user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        # TODO adjust user agent; see https://w.wiki/CX6
        sparql = SPARQLWrapper(endpoint_url, agent=random.choice(AGENTS_))
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        text = []
        for result in results["results"]["bindings"]:
            if "ps_Label" in result:
                if not is_number(result["ps_Label"]["value"]):
                    text.append(result["ps_Label"]["value"])
        if len(text) != 0 or count >= 2:
            if len(text) != 0:
                gl.keymap[QID] = text
            flag = False
def get_correct_id(item):
    mark=0
    res_key=""
    for key in state_map:
        tempmark=similarity.simi.ratio_similarity(item,key)
        if tempmark>mark:
            mark=tempmark
            res_key=state_map[key]
    if res_key!="" and mark>0.7:
        return  res_key
    else:
        return None




