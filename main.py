# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

import gl
import similarity.simi
from searchmanage import SearchManage

search_m1 = SearchManage(key='search', m_num=1000)
a=search_m1.search_run(points=["Newberry"],keys="id")
print(gl.keymap)
print(a)