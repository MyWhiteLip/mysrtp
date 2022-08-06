# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/7/21 
# @function: test for searchmanage
# @version : V0.4.1
#
import requests

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

import gl


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
    if QID in gl.keymap:
        return
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
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    text = ""
    for result in results["results"]["bindings"]:
        if "ps_Label" in result:
            if not is_number(result["ps_Label"]["value"]):
                text += result["ps_Label"]["value"]
                text += " "
    gl.keymap[QID]=text
