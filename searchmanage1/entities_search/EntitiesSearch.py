# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/6/6 
# @function: the script is used to do something.
# @version : V3.0
#

from searchmanage1.entities import Entities
from searchmanage1.tools.Tools import threads_allocation
from queue import Queue
from warnings import warn
from threading import Thread
from typing import Union, List
import time


# a queue of searching entities
class EntitiesSearch(object):

    def __init__(self, key: str = 'search'):
        self.search_queue = Queue()
        self.re_queue = Queue()
        self.re_list = list()
        self.entities_num = 0
        self.key = key

    def __set_search_entities(self, points: list):
        self.entities_num = len(points)
        for i in range(len(points)):
            entities = Entities()
            entities.set_entities(i, [points[i]])
            entities.init_params_entities(points[i], key='search')
            self.search_queue.put(entities)

    def __set_get_entities(self, points: list, m_num: int):
        if m_num > len(points):
            m_num = len(points)
        search_en, re_en = threads_allocation(points, m_num)
        self.entities_num = len(search_en)
        for i in range(len(search_en)):
            entities = Entities()
            entities.set_entities(i, re_en[i])
            entities.init_params_entities(search_en[i], key='ids')
            self.search_queue.put(entities)

    def init_entities_queue(self, points: list, m_num: int):
        while not self.search_queue.empty():
            self.search_queue.get()
        if self.key == 'search':
            self.__set_search_entities(points)
        elif self.key == 'ids':
            self.__set_get_entities(points, m_num)
        else:
            raise ValueError('class "EntitiesSearch".key does\'t have %s.' % self.key)

    def set_entities_params(self, **kwargs):
        if self.search_queue.empty():
            warn("Search queue is empty. Can not change parameters of entities.")
            return
        queue_t = Queue()
        while not self.search_queue.empty():
            entities: Entities = self.search_queue.get()
            entities.set_params(**kwargs)
            queue_t.put(entities)
        self.search_queue = queue_t

    def __wikidata_get(self, cache_: Queue, url: str, keys: Union[str, List[str]] = None,
                       timeout: float = 5):
        while not self.search_queue.empty():
            entities: Entities = self.search_queue.get()
            try:
                entities.entity_get_wiki(url=url, timeout=timeout)
                entities.wiki_json_analysis(key=self.key, keys=keys)
                self.re_queue.put(entities)
            except ValueError:
                cache_.put(entities)
        self.search_queue.task_done()

    def __re_queue_to_list(self):
        if len(self.re_list) != 0:
            self.re_list.clear()
        while not self.re_queue.empty():
            entities: Entities = self.re_queue.get()
            self.re_list.append(entities)

    def __sort_re_list(self):
        index_ = []
        da_: Entities
        for da_ in self.re_list:
            index_.append(da_.index)
        index_sort_ = sorted(range(len(index_)), key=lambda k: index_[k])
        re_list = []
        for in_ in index_sort_:
            re_list.append(self.re_list[in_])
        self.re_list = re_list

    def analysis_data_to_dict(self) -> dict:
        re_an = dict()
        if self.key == 'search':
            for key, value in self.re_list[0].re_.analysis.items():
                re_an[key] = [value]
            for da_ in self.re_list[1::]:
                for key, value in da_.re_.analysis.items():
                    re_an[key].append(value)
        elif self.key == 'ids':
            for key, value in self.re_list[0].re_.analysis[0].items():
                re_an[key] = [value]
            for da_t in self.re_list[0].re_.analysis[1::]:
                for key, value in da_t.items():
                    re_an[key].append(value)
            for da_ in self.re_list[1::]:
                for da_t in da_.re_.analysis:
                    for key, value in da_t.items():
                        re_an[key].append(value)
        return re_an

    def multithreading_get_wiki(self, url: str, m_num: int = 10, keys: Union[str, List[str]] = None,
                                timeout: float = 10.0, time_stop: float = 15.0, block_num: int = 10) -> dict:
        start = time.time()

        if self.search_queue.empty():
            warn("Search queue is empty.")
            return {}

        while not self.re_queue:
            self.re_queue.get()

        block_num_ = 0
        cache_ = Queue()
        while True:
            if m_num > self.search_queue.qsize():
                m_num = self.search_queue.qsize()

            threads = []
            for i in range(m_num):
                thread = Thread(target=self.__wikidata_get, args=(cache_, url, keys, timeout,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
            for t in threads:
                t.join()
            if cache_.qsize() == 0:
                print("querying successfully.")
                break

            end_t = time.time()
            print('Cost time:%.3fs.' % (end_t - start))
            print(f'Too many requests in short time.It is waiting {time_stop}s for next search.')
            print(f'Remained search failed Entities:{cache_.qsize()}.')
            self.search_queue = cache_
            cache_ = Queue()

            block_num_ += 1
            if block_num_ == block_num:
                raise RuntimeError('Time error. Please check Internet or search parameters.')

        self.__re_queue_to_list()
        self.__sort_re_list()
        end = time.time()
        print("Cost time:%.3fs.\n" % (end - start))
        return self.analysis_data_to_dict()

    def analysis_entities(self, keys: Union[str, List[str]] = None) -> dict:
        da_: Entities
        for da_ in self.re_list:
            da_.wiki_json_analysis(key=self.key, keys=keys)
        return self.analysis_data_to_dict()

    def analysis_json(self, function, *args, **kwargs) -> dict:
        da_: Entities
        for da_ in self.re_list:
            da_.json_analysis(key=self.key, function=function, *args, **kwargs)
        return self.analysis_data_to_dict()

    def get_re_(self):
        return self.re_list
