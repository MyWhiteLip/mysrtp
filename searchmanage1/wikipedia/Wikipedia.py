# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/7/20 
# @function: the class for using multithread in libray <wikipedia> API
# @version : V0.4.0
#

from queue import Queue
from typing import Union, List
from searchmanage.entities_search import EntitiesSearch
from searchmanage.entities import Entities
import wikipedia
from searchmanage.tools import Tools
from warnings import warn


class Wikipedia(EntitiesSearch):

    def __init__(self, m_num=10):
        super().__init__(key='wikipedia', m_num=m_num)
        self.__index_ = None

    def init_queue(self, points: list, **kwargs):
        while not self.search_queue.empty():
            self.search_queue.get()
        data_1d, self.__index_ = Tools.list_level(points)
        self.entities_num = len(data_1d)
        for i in range(self.entities_num):
            entities = Entities()
            entities.set_entities(i, None)
            entities.set_params(data_1d[i])
            self.search_queue.put(entities)
        if kwargs is not None:
            pass

    def __function__(self, cache_: Queue, url: str = None, keys: Union[str, List[str]] = None, timeout: float = 5,
                     function_=None, args: tuple = None):
        while not self.search_queue.empty():
            entities: Entities = self.search_queue.get()
            try:
                if entities.get_params == "" or entities.get_params is None:
                    entities.set_json(None)
                else:
                    if function_ is None:
                        entities.set_json(wikipedia.suggest(entities.get_params))
                    else:
                        entities.set_json(function_(entities.get_params, *args))
                self.re_queue.put(entities)
            except Exception as e:
                print(e)
                cache_.put(entities)
        self.search_queue.task_done()

    def search_run(self, points: list, time_stop: float = 30.0, block_num: int = 10,
                   function_=None, args: tuple = None, **kwargs) -> list:
        self.init_queue(points, **kwargs)
        print(f'Entities:{self.entities_num}(type:wikipedia).Threading number:{self.m_num}.')

        try:
            self.multithread_get_(timeout=30.0, time_stop=time_stop, block_num=block_num,
                                  url=None, keys=None, function_=function_, args=args)
        except RuntimeError:
            warn("Run time error.")
            return []

        return self.json_list

    @property
    def json_list(self):
        return Tools.list_back(super().json_list, self.__index_)

    @property
    def analysis_list(self):
        return Tools.list_back(super().analysis_list, self.__index_)
