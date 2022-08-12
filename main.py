# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys

import wikipedia
from SPARQLWrapper import SPARQLWrapper, JSON
from fake_useragent import UserAgent

ua = UserAgent()
print(ua.random)
import gl
import similarity.simi
from searchmanage import SearchManage

print(wikipedia.suggest("Zooey Daechanel"))
search_m1 = SearchManage(key='search', m_num=1000)
a = search_m1.search_run(points=["Abbevile"], keys="id")
print(gl.keymap)
print(a)
