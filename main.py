# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/
import random
import sys

import requests
import wikipedia
from SPARQLWrapper import SPARQLWrapper, JSON
from bs4 import BeautifulSoup
from fake_useragent import UserAgent



proxies={
    "http":"172.23.208.1:7890","https":"172.23.208.1:7890",
}
import cloudscraper
scraper = cloudscraper.create_scraper()
ua = UserAgent()
print(ua.random)
import gl
import similarity.simi
from searchmanage import SearchManage
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

def duckgo(word):
    timeout = 30
    params = {
        "q":word
    }
    result = requests.get("https://ask.com/", params=params, timeout=timeout,
                          headers={'User-Agent': ua.random})
    page_text = result.text
    soup = BeautifulSoup(page_text, "html.parser")
    if soup.find('a', class_='js-spelling-suggestion-link'):
        return soup.find('a', class_='js-spelling-suggestion-link').a.text  # 如果爬取成功，返回正确的字符串
    return None  # 否则返回None
def check(item):
    if item[0] == "Q" and item[1:len(item)].isdigit():
        return True
    else:
        return False
def brave_search(word):
    timeout = 30

    params = {
        "q":word+" site:wikidata.org",
        "o":0,
        "l":"dir",
        "qo":"serpSearchTopBox",
        "rtb":20000
    }
    result = scraper.request(url="https://ask.com/web", method="get",params=params, timeout=timeout
                          ,proxies=proxies)
    page_text = result.text
    print(page_text)
    soup = BeautifulSoup(page_text, "html.parser")
    if soup.findAll('div', class_='PartialSearchResults-item-url'):
        resu_list=[]
        resu=soup.findAll('div', class_='PartialSearchResults-item-url')
        for item in resu:
            if check(item.text.replace("www.wikidata.org/wiki/","")):
                resu_list.append(item.text.replace("www.wikidata.org/wiki/",""))
        if len(resu_list)!=0:
            return  resu_list
        else:
            return None
    return None  # 否则返回None'
print(brave_search("* Leadbelly"))