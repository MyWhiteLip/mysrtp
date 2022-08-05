# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/7/23 
# @function: the class of Sparql querying using multithread
# @version : V0.4.0
#

import re
import sys
from queue import Queue
from warnings import warn
from typing import Union, List
from searchmanage.entities import Entities
from searchmanage.entities_search import EntitiesSearch
from searchmanage.tools import Tools, AnalysisTools
from SPARQLWrapper import SPARQLWrapper

SPARQL_ = """
SELECT ?item ?itemLabel 
WHERE 
{
?item wdt:P31 wd:%s.
SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
"""

URL_ = "https://query.wikidata.org/sparql"

AGENT_ = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])


class SparqlQuery(EntitiesSearch):

    def __init__(self, m_num: int = 10, format_: str = 'json', url_: str = URL_, sparql_: str = SPARQL_):
        super().__init__(key='sparql', m_num=m_num)
        self.__returnFormat = format_
        self.__url_ = url_
        self.__sparql_ = sparql_
        self.__index_ = None

    def init_queue(self, points: list, **kwargs):
        while not self.search_queue.empty():
            self.search_queue.get()
        data_1d, self.__index_ = Tools.list_level(points)
        self.entities_num = len(data_1d)
        for i in range(self.entities_num):
            entities = Entities()
            entities.set_entities(i, None)
            entities.set_params(self.__sparql_ % data_1d[i])
            self.search_queue.put(entities)
        if kwargs is not None:
            pass

    def set_keys(self):
        reg = re.compile("SELECT.*?WHERE")
        k_ = reg.search(self.__sparql_.replace("\n", "").replace(" ", ""))
        if k_ is None:
            raise ValueError("Sparql Error")
        keys = k_.group().replace("SELECT", "").replace("WHERE", "")
        self.keys = keys[1::].split("?")

    def __function__(self, cache_: Queue, url: str = None, keys: Union[str, List[str]] = None, timeout: float = 5,
                     function_=None, args: tuple = None):
        sparql = SPARQLWrapper(endpoint=self.__url_, agent=AGENT_)
        sparql.setReturnFormat(self.__returnFormat)
        sparql.setTimeout(int(timeout))
        while not self.search_queue.empty():
            entities: Entities = self.search_queue.get()
            try:
                sparql.setQuery(entities.get_params)
                entities.set_json(sparql.query().convert())
            except Exception as e:
                print(e)
                cache_.put(entities)
                continue
            try:
                if function_ is None:
                    entities.set_analysis(AnalysisTools.sparql_analysis(entities.get_json))
                else:
                    entities.run_analysis(function=function_, *args)
            except Exception as e:
                print(e)
            self.re_queue.put(entities)
        self.search_queue.task_done()

    def analysis_to_dict(self) -> dict:
        re_an = dict()
        for k in self.keys:
            re_an[k] = []
        da_: Entities
        for da_ in self.re_list:
            for key, value in da_.get_analysis.items():
                re_an[key].append(value)
        return re_an

    def search_run(self, points: list, timeout: float = 30.0, time_stop: float = 30.0,
                   block_num: int = 10, function_=None, args: tuple = None, **kwargs) -> dict:
        self.init_queue(points, **kwargs)
        self.set_keys()
        print(f'Entities:{self.entities_num}(type:sparql).Threading number:{self.m_num}.')
        try:
            self.multithread_get_(timeout=timeout, time_stop=time_stop, block_num=block_num,
                                  url=None, keys=None, function_=function_, args=args)
        except RuntimeError:
            warn("Run time error.")
            return {}

        dict_t = dict()
        for k_, v_ in self.analysis_to_dict().items():
            dict_t[k_] = Tools.list_back(v_, self.__index_)
        return dict_t

    @property
    def json_list(self):
        return Tools.list_back(super().json_list, self.__index_)

    @property
    def analysis_list(self):
        return Tools.list_back(super().analysis_list, self.__index_)
