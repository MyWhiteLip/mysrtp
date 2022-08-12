# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

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

def brave_search(word):
    timeout = 30
    params = {
        "q":word
    }
    result = scraper.request(url="https://ask.com/web", method="get",params=params, timeout=timeout
                          ,proxies=proxies)
    page_text = result.text
    print(page_text)
    soup = BeautifulSoup(page_text, "html.parser")
    if soup.find('a', class_='PartialSpellCheck-link'):
        return soup.find('a', class_='PartialSpellCheck-link').text  # 如果爬取成功，返回正确的字符串
    return None  # 否则返回None'
for i in range(1000):
    print(brave_search("Martin Lewisss"))