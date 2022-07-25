# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/6/6 
# @function: class of SearchManage
# @version : V3.0
#

from typing import Union, List
from searchmanage.entities_search import EntitiesSearch
from searchmanage.tools.Tools import list_level, list_back
from warnings import warn


# class of searching manage
class SearchManage(EntitiesSearch):

    def __init__(self, url_api: str = "https://www.wikidata.org/w/api.php", key: str = 'search', m_num: int = 10):
        super().__init__(key=key)
        self.__url = url_api
        self.__m_num = m_num
        self.__data_1d = None
        self.__index_ = None

    def set_thread_num(self, m_num: int):
        self.__m_num = m_num

    def init_data(self, points: list):
        self.__data_1d, self.__index_ = list_level(points)

    def search_run_(self, keys: Union[str, List[str]] = None, timeout: float = 5.0, time_stop: float = 5.0,
                    block_num: int = 10) -> dict:
        if self.__data_1d is None or self.__index_ is None:
            warn('No search entities data.Please call function: \'init_data(points)\' firstly.')
            return {}
        if self.key == 'search':
            print(f'Entities:{len(self.__data_1d)}(type:text).Threading number:{self.__m_num}.')
        else:
            print(f'Entities:{len(self.__data_1d)}(type:wiki\'s entities id).Threading number:{self.__m_num}.')

        self.init_entities_queue(self.__data_1d, m_num=self.__m_num)
        try:
            dict_t = self.multithreading_get_wiki(self.__url, self.__m_num, keys=keys, timeout=timeout,
                                                  time_stop=time_stop, block_num=block_num)
        except RuntimeError:
            warn("Run time error.")
            return {}

        for k_, v_ in dict_t.items():
            dict_t[k_] = list_back(v_, self.__index_)
        return dict_t

    def search_run(self, points: list, keys: Union[str, List[str]] = None, timeout: float = 15.0, time_stop: float = 15.0,
                   block_num: int = 10) -> dict:
        self.init_data(points)
        return self.search_run_(keys, timeout, time_stop, block_num)

    def json_da_analysis(self, keys: Union[str, List[str]] = None) -> dict:
        dict_t = self.analysis_entities(keys=keys)
        for key, value in dict_t.items():
            dict_t[key] = list_back(value, self.__index_)
        return dict_t

    def return_data_1d(self) -> list:
        """Return 1D list after expanding from N-dimensional list."""
        return self.__data_1d

    def return_index_list(self) -> Union[int, list]:
        """Return location index getting from N-dimensional list expanse."""
        return self.__index_
