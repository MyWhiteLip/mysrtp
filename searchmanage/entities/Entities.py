# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/7/20 
# @function: the class of single entity for querying
# @version : V0.4.0
#
import random
import threading
from warnings import warn
from typing import Union, List
import requests
import wikipedia
from bs4 import BeautifulSoup
from requests import ReadTimeout
import gl
from searchmanage.tools.Tools import AGENTS_
from searchmanage.json_analysis import JsonAnalysis
from searchmanage.tools import AnalysisTools
from searchmanage.tools import Tools
from similarity import simi
from test import get_results
from test import get_correct_id

agents = AGENTS_


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


class Entities(JsonAnalysis):
    """Class of a single entity as an element in next querying using multithread.

    Store entity's based information like its index, entities text or ids in
    searching, and  search parameters.

    :ivar __index(int):
        store entity's index for restoring the
        correct location after multithreading
    :ivar __entities(list):
        entities text or ids into searching
    :ivar __params(Union[dict, str]):
        search parameters in querying
    :ivar __json(Union[dict, str, None]):
        json data
    :ivar __ready_(bool):
        record whether json data is ready
    :ivar __analysis(Union[dict, list, str,None]):
        result of analysis for json data
    """

    def __init__(self):
        super().__init__()
        self.__index = 0
        self.__entities = None
        self.__params = None

    def set_entities(self, index: int, entities: Union[list, None]):
        """Set entity's index and entities.

        :param index: entity's index
        :param entities: a list of entities text or ids in querying
        :return: None
        """
        self.__index = index
        self.__entities = entities

    def init_params(self, search_entities: str, key: str, **kwargs):
        """Init parameters in searching according to Wikimedia API format.

        :param search_entities: a string of entities text or ids
        :param key:
            a string of using 'search' in querying entities
            text, or 'ids' in querying entities ids
        :param kwargs:
            set query parameters you want, you can see more
            details in ReadMe.md which explains different
            keywords you can reset in two different key.
        :return: None

        See more details at:
            - https://www.wikidata.org/w/api.php?action=help&modules=wbsearchentities
            - https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities
        """
        if key == 'search':
            self.__params = {
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
            self.__params = {
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
                    self.__params[k_] = v_
                except KeyError:
                    warn("Search __params has not key = %s" % k_)

    def set_params(self, params: Union[dict, str]):
        """Set any querying parameters you want.

        You can use it when overriding method.

        :param params: a parameter you want
        :return: None
        """
        self.__params = params

    def set___params(self, **kwargs):
        """Reset parameters in searching according to Wikimedia API format.

        :param kwargs:
            set query parameters you want, you can see more
            details in ReadMe.md which explains different
            keywords you can reset in two different key.
        :return: None

        See more details at:
            - https://www.wikidata.org/w/api.php?action=help&modules=wbsearchentities
            - https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities
        """
        for k_, v_ in kwargs.items():
            try:
                self.__params[k_] = v_
            except KeyError:
                warn("Search params has not key = %s" % k_)

    def entity_get_wiki(self, url: str, timeout: float):
        """Sent request to url gave for **json** data.

        :param url:
            a string of url for sending request
        :param timeout:
            when request is (timeout) seconds overtime, it will raise ValueError
        :return: None
        :raise ValueError: any exception
        """
        self.clear()

        try:

            tempword = ""
            if self.__params["action"] == "wbsearchentities":
                tempword = self.__params["search"]

            get_ = requests.get(url=url,
                                params=self.__params,
                                headers={'User-Agent': random.choice(agents)},
                                timeout=timeout)
            json_ = get_.json()
            # if self.__params["action"] == "wbsearchentities":
            #     if len(json_['search']) == 0 and not is_number(self.__params["search"]):
            #         word = self.__params["search"]
            #         word = wikipedia.suggest(word)
            #         if word is not None and word != "":
            #             self.__params["search"] = word
            #             get_ = requests.get(url=url,
            #                                 params=self.__params,
            #                                 headers={'User-Agent': random.choice(agents)},
            #                                 timeout=timeout)
            #             json_ = get_.json()
            #             self.__params["search"] = tempword
            # wikipedia辅助
            if self.__params["action"] == "wbsearchentities":
                if len(json_['search']) == 0 and not is_number(self.__params["search"]):
                    word = Bing(self.__params["search"])
                    count = 0
                    while word is None and count <= 5:
                        word = Bing(self.__params["search"])
                        count += 1
                    if word is not None and word != "":
                        self.__params["search"] = word
                        get_ = requests.get(url=url,
                                            params=self.__params,
                                            headers={'User-Agent': random.choice(agents)},
                                            timeout=timeout)
                        json_ = get_.json()
            # bing纠正
            if self.__params["action"] == "wbsearchentities":
                for entity in json_["search"]:
                    if "lable" in entity:
                        if simi.levenshtein(self.__params["search"], entity["label"]) <= 0.65:
                            json_["search"].remove(entity)
                        else:
                            gl.labelmap[entity["id"]] = entity["label"]
            # bing查询
            if self.__params["action"] == "wbsearchentities":
                if not is_number(self.__params["search"]):
                    count = 0
                    while len(json_['search']) == 0 and count <= 3:
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
                        res = [i for i in range(len(result)) if
                               result.startswith("https://www.wikidata.org/wiki/", i)]
                        count1 = 0
                        search_list = []
                        for start in res:
                            if count1 >= 10:
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
                        if len(json_["search"]) != 0 and len(search_list) != 0:
                            __params = {
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
                            res = requests.get(url=url, params=__params, timeout=timeout,
                                               headers={'User-Agent': random.choice(agents)}).json()["entities"]
                            for entity in json_["search"]:
                                if entity["id"] in res and "labels" in res[entity["id"]] and "en" in \
                                        res[entity["id"]][
                                            "labels"]:
                                    if simi.levenshtein(self.__params["search"],
                                                        res[entity["id"]]["labels"]["en"]["value"]) <= 0.65:
                                        json_["search"].remove(entity)
                                    else:
                                        gl.labelmap[entity["id"]] = res[entity["id"]]["labels"]["en"]["value"]

            if self.__params["action"] == "wbsearchentities":
                thread_list = []
                for item in json_["search"]:
                    thread = threading.Thread(target=get_results,
                                              args=[item["id"]])
                    thread.start()
                    thread_list.append(thread)
                for item in thread_list:
                    item.join()



        except ReadTimeout:
            raise ValueError("Request time is over %fs." % timeout)
        except ValueError:
            raise ValueError("Search too many times.")
        except Exception as e:
            print(e)
            raise ValueError

        self.set_json(json_)

    def correct_id_repeat(self):
        """Correct duplicate entity errors.

        Notes:
            It was used after analysis.

        See also:
            - Tools.repeat_entities: Record repeating entities in list.
            - Tools.repeat_entities_back: Restore duplicate entity mapping.

        :return: None
        """
        if not self.ready:
            warn("Search data is not ready")
        index = Tools.repeat_entities(self.__entities)
        if len(index) == 0 or self.get_analysis is None:
            return
        self.set_analysis(Tools.repeat_entities_back(self.get_analysis, index))

    def wiki_json_analysis(self, key: str, keys: Union[str, List[str], None]) -> Union[list, dict, None]:
        """Analysis json data from Wikidata API.

        :param key: 'search' or 'ids'
        :param keys: analysis keys, more details seeing in ReadMe.md
        :return:
            If key is 'search', it will return a dict like {'ids':
            ['Q3551770', 'Q4430597']}. If key is 'ids', it will
            return a list[dict] like [{'P31':['Q20643955']}, {
            'P31': ['Q5']}].

        See also:
            - AnalysisTools.search_analysis
            - AnalysisTools.entities_analysis
            - correct_id_repeat
        """
        if not self.ready:
            return None
        if key == 'search':
            self.run_analysis(function=AnalysisTools.search_analysis, keys=keys)
        elif key == 'ids':
            self.run_analysis(function=AnalysisTools.entities_analysis, keys=keys)
            self.correct_id_repeat()

        else:
            warn("No action:%s" % key)
        return self.get_analysis

    def json_analysis(self, key: str, function, *args, **kwargs):
        """Analysis json data from Wikidata API using your own function.

        :param key: 'search' or 'ids'
        :param function: your own analysis function
        :param args: you own function's parameters which format is tuple
        :param kwargs: you own function's parameters which format is dict
        :return: analysis result

        See also:
            - JsonAnalysis().run_analysis
            - correct_id_repeat
        """
        if not self.ready:
            return None
        if key == 'search':
            self.run_analysis(function=function, *args, **kwargs)
        elif key == 'ids':
            self.run_analysis(function=function, *args, **kwargs)
            self.correct_id_repeat()
        else:
            warn("No action:%s" % key)
        return self.get_analysis

    @property
    def get_index(self) -> int:
        """Get entity's index."""
        return self.__index

    @property
    def get_entities(self) -> Union[list, None]:
        """Get entity's list of test or ids."""
        return self.__entities

    @property
    def get_params(self) -> Union[dict, str, None]:
        """Get entity's querying parameter."""
        return self.__params
