import time
import wikipedia
import requests
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener
import textdistance
import similarity.simi
import sys
from SPARQLWrapper import SPARQLWrapper, JSON


def get_claims(qid):
    api_endpoint = "https://www.wikidata.org/w/api.php"
    params = {
        'action': 'wbgetclaims',
        'format': 'json',
        'entity': qid
    }
    r = requests.get(api_endpoint, params=params)
    print(type(r))
    # print(r.json())
    re_json = r.json()['claims']
    return  re_json


def get_item(title_re):
    api_endpoint = "https://www.wikidata.org/w/api.php"
    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'language': 'en',
        'type': 'item',
        'limit': 5,
        'search': title_re
    }
    r = requests.get(api_endpoint, params=params)
    # print(r.json())
    re_json = r.json()
    re_list = re_json['search']
    # print(re_list)
    id_list = []
    text = '';
    for re_item in re_list:
        if similarity.simi.ratio_similarity(re_item['label'], title_re) >= 0.8:
            id_list.append(re_item['id'])
            # 消除其它字符
            if 'description' in re_item:
                text += ''.join(filter(str.isalnum, re_item['description']))
    return id_list, text


def get_label(qid):
    endpoint_url = "https://query.wikidata.org/sparql"

    query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX wd: <http://www.wikidata.org/entity/> 
    SELECT  *
    WHERE {
            wd:""" + qid + """ rdfs:label ?label .
            FILTER (langMatches( lang(?label), "EN" ) )
          } """

    def get_results(endpoint_url, query):
        user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        # TODO adjust user agent; see https://w.wiki/CX6
        sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()

    results = get_results(endpoint_url, query)
    return results["results"]["bindings"][0]['label']['value']

