# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/6/6 
# @function: the script is used to do something.
# @version : V3.0
#
import random
from warnings import warn
import requests
from bs4 import BeautifulSoup
from requests.exceptions import ReadTimeout
from typing import List, Union

from searchmanage1.tools.AnalysisTools import entities_analysis, search_analysis
from searchmanage1.tools.Tools import agents, repeat_entities

from searchmanage1.json_analysis import JsonAnalysis
from similarity import simi


def Bing(word):
    timeout = 30
    params = {
        "q": word,
        "ensearch": 1  # Bing国际版
    }
    agent = random.choice(agents)
    result = requests.get("https://www.bing.com/search", params=params, timeout=timeout,
                          headers={'User-Agent': random.choice(agents)})
    page_text = result.text
    soup = BeautifulSoup(page_text, "html.parser")
    if soup.find('div', id='sp_requery'):
        return soup.find('div', id='sp_requery').a.text  # 如果爬取成功，返回正确的字符串
    return None  # 否则返回None


example = {
    "id": "Q214096",
    "title": "Q214096",
    "pageid": 209498,
    "display": {
        "label": {
            "value": "Menura",
            "language": "en"
        },
        "description": {
            "value": "genus of birds",
            "language": "en"
        }
    },
    "repository": "wikidata",
    "url": "//www.wikidata.org/wiki/Q214096",
    "concepturi": "http://www.wikidata.org/entity/Q214096",
    "label": "Menura",
    "description": "genus of birds",
    "match": {
        "type": "alias",
        "language": "en",
        "text": "lyrebird"
    },
    "aliases": [
        "lyrebird"
    ]
}


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


# class of a single entity
class Entities(object):

    def __init__(self):
        self.index = 0
        self.entities = None
        self.search_params = None
        self.re_ = JsonAnalysis()

    def set_entities(self, index: int, entities: list):
        self.index = index
        self.entities = entities

    def init_params_entities(self, search_entities: str, key: str, **kwargs):
        if key == 'search':
            self.search_params = {
                'search': search_entities,
                'action': 'wbsearchentities',
                'format': 'json',
                'language': 'en',
                'type': 'item',
                'limit': 20,
                'strictlanguage': None,
                'continue': None,
                'props': None
            }
        elif key == 'ids':
            self.search_params = {
                'ids': search_entities,
                'action': 'wbgetentities',
                'format': 'json',
                'languages': 'en',
                'redirects': None,
                'sites': None,
                'title': None,
                'props': None,
                'languagefallback': None,
                'normalize': None,
                'sitefilter': None
            }
        else:
            raise ValueError("No key = %s" % key)

        if kwargs is not None:
            for k_, v_ in kwargs.items():
                try:
                    self.search_params[k_] = v_
                except KeyError:
                    warn("Search params has not key = %s" % k_)

    def set_params(self, **kwargs):
        for k_, v_ in kwargs.items():
            try:
                self.search_params[k_] = v_
            except KeyError:
                warn("Search params has not key = %s" % k_)

    def entity_get_wiki(self, url: str, timeout: float = 10):
        self.re_.clear()

        try:
            get_ = requests.get(url=url,
                                params=self.search_params,
                                headers={'User-Agent': random.choice(agents)},
                                timeout=timeout)
            json_ = get_.json()
            tempword = ""

            if self.search_params["action"] == "wbsearchentities":
                tempword = self.search_params["search"]
            if self.search_params["action"] == "wbsearchentities":
                if len(json_['search']) == 0 and not is_number(self.search_params["search"]):
                    word = Bing(self.search_params["search"])
                    count = 0
                    while word is None and count <= 1:
                        word = Bing(self.search_params["search"])
                        count += 1
                    if word is not None and word != "":
                        self.search_params["search"] = word
                        get_ = requests.get(url=url,
                                            params=self.search_params,
                                            headers={'User-Agent': random.choice(agents)},
                                            timeout=timeout)
                        json_ = get_.json()
            # BING纠正
            # if self.search_params["action"] == "wbsearchentities":
            #     if len(json_['search']) == 0 and not is_number(self.search_params["search"]):
            #         word = self.search_params["search"]
            #         word = wikipedia.suggest(word)
            #         if word is not None and word != "":
            #             self.search_params["search"] = word
            #             get_ = requests.get(url=url,
            #                                 params=self.search_params,
            #                                 headers={'User-Agent': random.choice(agents)},
            #                                 timeout=timeout)
            #             json_ = get_.json()
            # # wikipedia辅助
            if self.search_params["action"] == "wbsearchentities":
                if not is_number(self.search_params["search"]):
                    count = 0
                    while len(json_['search']) == 0 and count <= 2:
                        count = count + 1
                        params = {
                            "q": tempword + " site:wikidata.org",
                            "setlang": "en-us",
                            "form": "QBLH",
                            "go": "search"
                        }
                        result = str(requests.get("https://www.bing.com/search", params=params, timeout=timeout,
                                                  headers={'User-Agent': random.choice(agents)}
                                                 ).content)
                        res = [i for i in range(len(result)) if result.startswith("https://www.wikidata.org/wiki/", i)]
                        count1 = 0
                        search_list = []
                        for start in res:
                            if count1 >= 15:
                                break
                            index = start + len("https://www.wikidata.org/wiki/")
                            ans = "Q"
                            for i in range(10):
                                if is_number(result[i + index]):
                                    ans += result[i + index]
                            if ans != "Q":
                                json_["search"].append({"id": ans})
                                search_list.append(ans)
                            count1 += 1
                        # 对id列表查询
                        if len(json_["search"]) != 0:
                            search_params = {
                                'ids': search_list,
                                'action': 'wbgetentities',
                                'format': 'json',
                                'languages': 'en',
                                'redirects': None,
                                'sites': None,
                                'title': None,
                                'props': None,
                                'languagefallback': None,
                                'normalize': None,
                                'sitefilter': None
                            }
                            res = requests.get(url=url, params=search_params, timeout=timeout,
                                               headers={'User-Agent': random.choice(agents)}).json()[
                                "entities"]
                            for entity in json_["search"]:
                                if entity["id"] in res and "en" in res[entity["id"]]["labels"]:
                                    if simi.levenshtein(self.search_params["search"],
                                                        res[entity["id"]]["labels"]["en"]["value"]) <= 0.6:
                                        json_["search"].remove(entity)
            # bing查询

            if self.search_params["action"] == "wbsearchentities":
                for entity in json_["search"]:
                    if "lable" in entity:
                        if simi.levenshtein(self.search_params["search"], entity["label"]) <= 0.6:
                            json_["search"].remove(entity)
        except ReadTimeout:
            raise ValueError("Request time is over %fs." % timeout)
        except ValueError:
            raise ValueError("Search too many times.")
        except Exception as e:
            print(e)
            raise ValueError

        self.re_.set_data(json_)

    def correct_id_repeat(self):
        if not self.re_.ready():
            warn("Search data is not ready")
        index = repeat_entities(self.entities)
        if len(index) == 0:
            return
        self.re_.correct_repeat(index)

    def wiki_json_analysis(self, key: str, keys: Union[str, List[str], None]) -> Union[list, dict, None]:
        if not self.re_.ready():
            return None
        if key == 'search':
            self.re_.run_analysis(function=search_analysis, keys=keys)
        elif key == 'ids':
            self.re_.run_analysis(function=entities_analysis, keys=keys)
            self.correct_id_repeat()
        else:
            warn("No action:%s" % key)
        return self.re_.get_analysis()

    def json_analysis(self, key: str, function, *args, **kwargs):
        if not self.re_.ready():
            return None
        if key == 'search':
            self.re_.run_analysis(function=function, *args, **kwargs)
        elif key == 'ids':
            self.re_.run_analysis(function=function, *args, **kwargs)
            self.correct_id_repeat()
        else:
            warn("No action:%s" % key)
        return self.re_.get_analysis()
