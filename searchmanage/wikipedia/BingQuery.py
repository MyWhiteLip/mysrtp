# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/7/25 
# @function: the class of querying Bing data using multithread.
# @version : V0.1.0
#
from typing import Union, List
import requests
import random
from searchmanage.entities_search import EntitiesSearch
from searchmanage.entities import Entities
from searchmanage.tools import Tools
from warnings import warn
from queue import Queue
import re

URL_ = "https://www.bing.com/search"


class BingQuery(EntitiesSearch):

    def __init__(self, url_: str = URL_, m_num: int = 10):
        super().__init__(key="bing", m_num=m_num)
        self.__url_ = url_
        self.__index_ = None

    def init_queue(self, points: list, **kwargs):
        while not self.search_queue.empty():
            self.search_queue.get()
        data_1d, self.__index_ = Tools.list_level(points)
        self.entities_num = len(data_1d)
        for i in range(self.entities_num):
            entities = Entities()
            entities.set_entities(i, None)
            params = {
                "q": data_1d[i] + " site:wikidata.org",
                "setlang": "en-us"
            }
            entities.set_params(params)
            self.search_queue.put(entities)
        if kwargs is not None:
            pass

    def __function__(self, cache_: Queue, url: str = None, keys: Union[str, List[str]] = None,
                     timeout: float = 5, function_=None, args: tuple = None):
        reg_ = re.compile(r"https://www.wikidata.org/wiki/Q\d+")
        while not self.search_queue.empty():
            entities: Entities = self.search_queue.get()
            try:
                result = str(requests.get(url=url,
                                          params=entities.get_params,
                                          headers={'User-Agent': random.choice(AGENTS_)},
                                          timeout=timeout).content)
                entities.set_json(result)
            except Exception as e:
                print(e)
                cache_.put(entities)
                continue
            try:
                if function_ is None:
                    entities.set_analysis(reg_.findall(result))
                else:
                    entities.run_analysis(function=function_, args=args)
            except Exception as e:
                print(e)
            self.re_queue.put(entities)
        self.search_queue.task_done()

    def search_run(self, points: list, timeout: float = 30.0, time_stop: float = 30.0,
                   block_num: int = 10, function_=None, args: tuple = None, **kwargs) -> list:
        self.init_queue(points, **kwargs)
        print(f'Entities:{self.entities_num}(type:bingQuery).Threading number:{self.m_num}.')
        try:
            self.multithread_get_(timeout=timeout, time_stop=time_stop, block_num=block_num,
                                  url=self.__url_, keys=None, function_=function_, args=args)
        except RuntimeError:
            warn("Run time error.")
            return []

        return self.analysis_list

    @property
    def json_list(self):
        return Tools.list_back(super().json_list, self.__index_)

    @property
    def analysis_list(self):
        return Tools.list_back(super().analysis_list, self.__index_)
