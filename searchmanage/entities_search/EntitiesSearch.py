# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/7/20 
# @function: the class for querying the set of entities using multithread
# @version : V0.4.0
#

from searchmanage.tools import Tools
from searchmanage.entities import Entities
from queue import Queue
from warnings import warn
from typing import Union, List
import time
from concurrent.futures import ThreadPoolExecutor


class EntitiesSearch(object):
    """Class of a set of querying entities(<class, 'Entities'>).

    Put multiple querying entities(<class,'Entities'>) in a queue. When
    we use multithread to get data for improving requests speed,
    we can conveniently call this queue.

    Note:
        You can inherit this class, and override the methods:
        `init_queue` and `__function__`. Then call the method:
        `multithread_get_` to run you own querying using
        multithread.

    :ivar entities_num(int):
        the number of querying entities
    :ivar key(string):
        a string reflecting its feature
    :ivar keys(Union[list, str, None]):
        a list or a string reflecting its keywords
    :ivar m_num(int):
        the number of thread in querying
    :ivar search_queue(Queue):
        consumer queue for init multiple entities(<class,'Entities'>)
    :ivar re_queue(Queue):
        producer queue for storing results of multiple entities(<class,'Entities'>)
    :ivar re_list(list):
        list of results of multiple entities(<class,'Entities'>)after querying
        for conveniently getting entities(<class,'Entities'>)

    :param key:
        a string reflecting its feature. Default: 'search'
    :param m_num:
        the number of thread in querying. Default: 10

    """

    def __init__(self, key: str = 'search', m_num: int = 10):
        self.entities_num = 0
        self.key = key
        self.keys = None
        self.m_num = m_num
        self.search_queue = Queue()
        self.re_queue = Queue()
        self.re_list = list()

    def __set_search_entities(self, points: list, **kwargs):
        """Init search entities when key is 'search'.

        :param points: a 1D list of searching text
        :return: None

        See also:
            - Entities.set_entities
            - Entities.init_params
        """
        self.entities_num = len(points)
        for i in range(len(points)):
            entities = Entities()
            entities.set_entities(i, [points[i]])
            entities.init_params(points[i], key='search', **kwargs)
            self.search_queue.put(entities)

    def __set_get_entities(self, points: list, **kwargs):
        """Init search entities when key is 'ids'.

        :param points: a 1D list of searching text
        :return: None

        See also:
            - Entities.set_entities
            - Entities.init_params
            - Tools.threads_allocation

        """
        m_num = self.m_num
        if m_num > len(points):
            m_num = len(points)
        search_en, re_en = Tools.threads_allocation(points, m_num)
        self.entities_num = len(search_en)
        for i in range(len(search_en)):
            entities = Entities()
            entities.set_entities(i, re_en[i])
            entities.init_params(search_en[i], key='ids', **kwargs)
            self.search_queue.put(entities)

    def init_queue(self, points: list, **kwargs):
        """Init queue of search entities.

        :param points:
            a 1D list of querying entities txt or ids
        :param kwargs:
            for function expansion
        :return: None
        """
        while not self.search_queue.empty():
            self.search_queue.get()
        if self.key == 'search':
            self.__set_search_entities(points, **kwargs)
        elif self.key == 'ids':
            self.__set_get_entities(points, **kwargs)
        else:
            raise ValueError('class "EntitiesSearch".key does\'t have %s.' % self.key)

    def set_entities_params(self, **kwargs):
        """Reset the queue of parameters in searching except entities text or ids.

        :param kwargs:
            set query parameters you want, you can see more details
            in ReadMe.md which explains different keywords you can
            reset in two different key.
        :return: None

        See more details:
            - https://www.wikidata.org/w/api.php?action=help&modules=wbsearchentities
            - https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities

        See also:
            - Entities.set_search_params
        """
        if self.search_queue.empty():
            warn("Search queue is empty. Can not change parameters of entities.")
            return
        queue_t = Queue()
        while not self.search_queue.empty():
            entities: Entities = self.search_queue.get()
            entities.set_search_params(**kwargs)
            queue_t.put(entities)
        self.search_queue = queue_t

    def set_thread_num(self, m_num: int):
        """Reset the number of thread in querying.

        :param m_num: the number of thread you want to set. Default: 10
        :return: None
        """
        self.m_num = m_num

    def __function__(self, cache_: Queue, url: str = None, keys: Union[str, List[str]] = None,
                     timeout: float = 5, function_=None, args: tuple = None):
        """It solves a single entities in querying which will be call
        in `multithread_get_`.

        Nots:
            Override this function and then call `multithread_get_`
            to run you own querying using multithread.

        :param cache_: cache entities that run incorrectly
        :param url: required domain name address. Default: None
        :param keys: keywords you may need. Default: None
        :param timeout: time flag you may need. Default: 5.0
        :param function_: a function you may need. Default: None
        :param args: a tuple of parameters in you own function. Default: None
        :return: None
        """
        while not self.search_queue.empty():
            entities: Entities = self.search_queue.get()
            try:
                entities.entity_get_wiki(url=url, timeout=timeout)
            except ValueError:
                cache_.put(entities)
                continue
            try:
                if function_ is None:
                    if keys is not None:
                        entities.wiki_json_analysis(key=self.key, keys=keys)
                else:
                    entities.run_analysis(function=function_, *args)
            except Exception as e:
                print(e)
            self.re_queue.put(entities)
        self.search_queue.task_done()

    def __queue_to_list_sort__(self):
        """Sort the correct location according to entities.__index_
         after multithreading and then put entities from queue to list."""
        if len(self.re_list) != 0:
            self.re_list.clear()
        index_ = []
        while not self.re_queue.empty():
            entities: Entities = self.re_queue.get()
            index_.append(entities.get_index)
            self.re_list.append(entities)
        index_sort_ = sorted(range(len(index_)), key=lambda k: index_[k])
        re_list = []
        for in_ in index_sort_:
            re_list.append(self.re_list[in_])
        self.re_list = re_list

    def multithread_get_(self, time_stop: float = 30, block_num: int = 10, url: str = None,
                         keys: Union[str, List[str]] = None, timeout: float = 30,
                         function_=None, args: tuple = None):
        """Run method: `__function__` using multithread.

        When some entities in queue raise exception, the system
        will Run these entities again after *time_stop* second
        waiting until run successfully or run time over
        *block_num*.

        :param time_stop: blocking time when entities in queue raise exception. Default: 30.0
        :param block_num: maximum number of repeated running. Default: 10
        :param url: parameter in method: __function__. Default: None
        :param keys: parameter in method: __function__. Default: None
        :param timeout: parameter in method: __function__. Default: 30.0
        :param function_: parameter in method: __function__. Default: None
        :param args: parameter in method: __function__. Default: None
        :return: None

        See also:
            - __function__
        """
        start = time.time()

        if keys is not None:
            if type(keys) != list:
                self.keys = [keys]
            else:
                self.keys = keys

        if self.search_queue.empty():
            warn("Search queue is empty.")
            return

        while not self.re_queue:
            self.re_queue.get()

        block_num_ = 0
        while block_num_ < block_num:
            cache_ = Queue()
            m_num = self.m_num
            if m_num > self.search_queue.qsize():
                m_num = self.search_queue.qsize()

            with ThreadPoolExecutor(max_workers=m_num) as pool:
                for i in range(m_num):
                    pool.submit(self.__function__, cache_, url,
                                keys, timeout, function_, args)

            if cache_.qsize() == 0:
                print("Querying successfully.")
                break

            end_t = time.time()
            print('Cost time:%.3fs.' % (end_t - start))
            print(f'Too many requests in short time.It is waiting {time_stop}s for next search.')
            print(f'Remained search failed Entities:{cache_.qsize()}.')

            self.search_queue = cache_
            block_num_ += 1
            time.sleep(time_stop)

        if not self.search_queue.empty():
            warn("Remained %s entities querying failed. Please to check." % str(self.search_queue.qsize()))
            while not self.search_queue.empty():
                entities: Entities = self.search_queue.get()
                entities.set_json(None)
                self.re_queue.put(entities)

        self.__queue_to_list_sort__()
        end = time.time()
        print("Cost time:%.3fs.\n" % (end - start))

    def analysis_to_dict(self) -> dict:
        """Turn result list of analysis from list[dict] into dict[list].

        Note:
            When analysis your own entities, you need
            to override this method which is used for
            analysis result from Wikidata API.

        :return: data of dict[list] from list[dict]
        """
        re_an = dict()
        if self.key == 'search':
            for key, value in self.re_list[0].get_analysis.items():
                re_an[key] = [value]
            da_: Entities
            for da_ in self.re_list[1::]:
                for key, value in da_.get_analysis.items():
                    re_an[key].append(value)
        elif self.key == 'ids':
            for k in self.keys:
                re_an[k] = []
            da_: Entities
            for da_ in self.re_list:
                for da_t in da_.get_analysis:
                    for key, value in da_t.items():
                        re_an[key].append(value)
        return re_an

    def analysis_entities(self, keys: Union[str, List[str]] = None) -> dict:
        """Analysis the list of entities' json data.

        :param keys:
            analysis keys, more details seeing in ReadMe.md
        :return:
            If key is 'search', it will return a dict like
            {'ids': ['Q3551770', 'Q4430597']}. If key is 'ids',
            it will return a list[dict] like [{'P31':['Q206439
            55']}, { 'P31': ['Q5']}].

        See also:
            - Entities.wiki_json_analysis
            - analysis_to_dict
        """
        da_: Entities
        for da_ in self.re_list:
            da_.wiki_json_analysis(key=self.key, keys=keys)
        return self.analysis_to_dict()

    def analysis_json(self, function_, *args, **kwargs) -> dict:
        """Analysis json data in the list of entities using your own function.

        :param function_: your own analysis function
        :param args: your own analysis function
        :param kwargs: your own function's parameters which format is dict
        :return: analysis result

        See also:
            - Entities.json_analysis
            - analysis_to_dict
        """
        da_: Entities
        for da_ in self.re_list:
            da_.json_analysis(key=self.key, function=function_, *args, **kwargs)
        return self.analysis_to_dict()

    @property
    def json_list(self) -> list:
        """Get a list of entities' json data."""
        l_ = []
        entities: Entities
        for entities in self.re_list:
            l_.append(entities.get_json)
        return l_

    @property
    def analysis_list(self) -> list:
        """Get a list of entities' analysis result."""
        l_ = []
        entities: Entities
        for entities in self.re_list:
            l_.append(entities.get_analysis)
        return l_
