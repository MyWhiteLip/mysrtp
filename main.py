# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys

import requests
import wikipedia
from SPARQLWrapper import SPARQLWrapper, JSON
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


ua = UserAgent()
print(ua.random)
import gl
import similarity.simi
from searchmanage import SearchManage
def Bing(word):
    timeout = 30
    params = {
        "search": word,
        "ns0": 1  # Bing国际版
    }
    result = requests.get("https://en.wikipedia.org/w/index.php", params=params, timeout=timeout,
                          headers={'User-Agent': ua.random})
    page_text = result.text
    soup = BeautifulSoup(page_text, "html.parser")
    if soup.find('a', id='mw-search-DYM-rewritten'):
        return soup.find('a', id='mw-search-DYM-rewritten').text  # 如果爬取成功，返回正确的字符串
    return None  # 否则返回None
for i in range(1000):
    print(Bing("Ricky Wilsoonn"))