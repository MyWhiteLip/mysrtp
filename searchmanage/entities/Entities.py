# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/6/6 
# @function: the script is used to do something.
# @version : V3.0
#
import datetime
import json
import random
import threading
import time
from warnings import warn
import requests
import wikipedia
from requests.exceptions import ReadTimeout
from typing import List, Union
from searchmanage.tools.Tools import agents, repeat_entities
from searchmanage.tools.AnalysisTools import search_analysis, entities_analysis
from searchmanage.json_analysis import JsonAnalysis
from similarity import simi

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
                'limit': 15,
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
                    word = self.search_params["search"]
                    word = wikipedia.suggest(word)
                    if word is not None and word != "":
                        self.search_params["search"] = word
                        get_ = requests.get(url=url,
                                            params=self.search_params,
                                            headers={'User-Agent': random.choice(agents)},
                                            timeout=timeout)
                        json_ = get_.json()
            # wikipedia辅助

            if self.search_params["action"] == "wbsearchentities":
                if not is_number(self.search_params["search"]):
                    count = 0
                    while len(json_['search']) == 0 and count <= 8:
                        count = count + 1
                        params = {
                            "q": self.search_params["search"] + " site:wikidata.org",
                            "setlang": "en-us"
                        }
                        result = str(requests.get("https://www.bing.com/search", params=params, timeout=timeout,
                                                  headers={'User-Agent': random.choice(agents)}).content)
                        res = [i for i in range(len(result)) if result.startswith("https://www.wikidata.org/wiki/", i)]
                        count1 = 0
                        for start in res:
                            if count1 >= 3:
                                break
                            index = start + len("https://www.wikidata.org/wiki/")
                            ans = "Q"
                            for i in range(10):
                                if is_number(result[i + index]):
                                    ans += result[i + index]
                            if ans != "Q":
                                json_["search"].append({"id": ans})
                            count1 += 1
            # bing查询

            if self.search_params["action"] == "wbsearchentities":
                for entity in json_["search"]:
                    if "lable" in entity:
                        if simi.levenshtein(self.search_params["search"], entity["label"]) <= 0.5:
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
