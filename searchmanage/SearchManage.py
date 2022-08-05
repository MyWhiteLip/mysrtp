# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/7/20 
# @function: the class of using API
# @version : V0.4.0
#

from typing import Union, List
from warnings import warn
from searchmanage.entities_search import EntitiesSearch
from searchmanage.tools import Tools


class SearchManage(EntitiesSearch):
    """Class of querying with Wikidata API using multithread.

    In this class, you can set the number of threading for querying.
    And you can put N-dimensional list of entities' text or ids in
    it, so you can query a number of entity in one time. What's more,
    each entity can get results at right position and right dimension
    in the list.


    Example
    -------
        >>> search_m1 = SearchManage(key='search', m_num=10)
        >>> points1 = [['SEU'], ['computer', 'game', 'computer games'], ['paper', 'comic', 'comic books']]
        >>> print(points1)
        [['SEU'], ['computer', 'game', 'computer games'], ['paper', 'comic', 'comic books']]

        >>> re1 = search_m1.search_run(points=points1, keys='id')
        Entities:7.Threading number:10.
        Querying successfully.
        Cost time:0.889532s.

        >>> print(re1)
        {'id': [[['Q3551770', 'Q4430597', 'Q1476733', 'Q405915', 'Q7455033', 'Q69513094', 'Q37481985',
        'Q29834566', 'Q98770548', 'Q23665157']], [['Q68', 'Q5157408', 'Q11202952', 'Q74058411', 'Q444
        195', 'Q7397', 'Q7889', 'Q21198', 'Q250', 'Q32566'], ['Q7889', 'Q11410', 'Q13406554', 'Q223930'
        , 'Q189936', 'Q16510064', 'Q723187', 'Q55524865', 'Q1493033', 'Q19862498'], ['Q4485157', 'Q2990
        909', 'Q5157439', 'Q44377201', 'Q57549504', 'Q868628', 'Q52199645', 'Q39736420', 'Q72344998',
        'Q47931363']], [['Q11472', 'Q13442814', 'Q1747211', 'Q410088', 'Q7132584', 'Q1402686', 'Q375703
        64', 'Q7132583', 'Q106499074', 'Q3894714'], ['Q245068', 'Q58209506', 'Q1004', 'Q3684337', 'Q772
        6945', 'Q108434880', 'Q838795', 'Q725377', 'Q1760610', 'Q715301'], ['Q43414701', 'Q30331748', '
        Q58572832', 'Q58572652', 'Q61938130', 'Q58572642', 'Q58446169', 'Q58447417', 'Q39870027', 'Q584
        99624']]]}

        >>> search_m2 = SearchManage(key='ids', m_num=10)
        >>> points2 = re1['id'][1]
        >>> print(points2)
        [['Q68', 'Q5157408', 'Q11202952', 'Q74058411', 'Q444195', 'Q7397', 'Q7889', 'Q21198', 'Q250', '
        Q32566'], ['Q7889', 'Q11410', 'Q13406554', 'Q223930', 'Q189936', 'Q16510064', 'Q723187', 'Q55524
        865', 'Q1493033', 'Q19862498'], ['Q4485157', 'Q2990909', 'Q5157439', 'Q44377201', 'Q57549504', '
        Q868628', 'Q52199645', 'Q39736420', 'Q72344998', 'Q47931363']]

        >>> re2 = search_m2.search_run(points=points2, keys=['claims/P31/value', 'labels/en'])
        Entities:30.Threading number:10.
        Querying successfully.
        Cost time:1.420619s.

        >>> print(re2)
        {'claims/P31/value': [[[], ['Q5633421'], ['Q28640', 'Q11488158', 'Q4164871'], [], ['Q4167410'], [],
        ['Q56055944'], ['Q11862829', 'Q4671286'], [], ['Q55215251']], [['Q56055944'], [], [],[], ['Q5'], [],
        ['Q11424'], ['Q431603', 'Q2178147'], ['Q4167410'], []], [[], ['Q482994'], ['Q134556'], ['Q4167410'],
        ['Q13442814'], ['Q41298'], ['Q13442814'], ['Q13442814'], ['Q13442814'], ['Q13442814']]],
        'labels/en': [['computer', 'Computer', 'human computer', 'computer voice', 'Computer', 'software', 'video
        game', 'computer science', 'computer keyboard', 'computed tomography'], ['video game', 'game', 'sports
        competition', 'game', 'The Game', 'sporting event', 'The Game', 'game', 'Game', 'game meat'], ['PC game',
        'Computer Games', 'Computer Games', 'Computer Games','Computer Games', 'Computer Games Magazine', 'Computer
        games and information-processing skills.','Computer games to teach hygiene: an evaluation of the e-Bug
        junior game.', 'Computer games as a means of movement rehabilitation', 'Computer games supporting cognitive
        behaviour therapy in children.']]}

    :ivar __url:
        a sting of domain name address
    :ivar __index_:
        location index getting from expanse of N-dimensional list
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

    :param url_api: a sting of domain name address. Default: "https://www.wikidata.org/w/api.php"
    :param key: a string of query patten. 'search' or 'ids'. Default: "search"
    :param m_num: the number of thread in querying. Default: 10

    """

    def __init__(self, url_api: str = "https://www.wikidata.org/w/api.php", key: str = 'search', m_num: int = 10):
        super().__init__(key=key, m_num=m_num)
        self.__url = url_api
        self.__index_ = None

    def search_run(self, points: list, keys: Union[str, List[str]] = None,
                   timeout: float = 30.0, time_stop: float = 30.0, block_num: int = 10,
                   function_=None, args: tuple = None, **kwargs) -> dict:
        """Run querying using multithread.

        :param points: N-dimensional list of entities' text or ids
        :param keys:
        :param timeout:
        :param time_stop:
        :param block_num:
        :param function_:
        :param args:
        :param kwargs:
        :return:
        """
        data_1d, self.__index_ = Tools.list_level(points)
        self.init_queue(data_1d, **kwargs)

        if self.key == 'search':
            print(f'Entities:{self.entities_num}(type:text).Threading number:{self.m_num}.')
        else:
            print(f'Entities:{self.entities_num}(type:wiki\'s entities id).Threading number:{self.m_num}.')

        try:
            self.multithread_get_(timeout=timeout, time_stop=time_stop, block_num=block_num,
                                  url=self.__url, keys=keys, function_=function_, args=args)
        except RuntimeError:
            warn("Run time error.")
            return {}

        dict_t = dict()
        for k_, v_ in self.analysis_to_dict().items():
            dict_t[k_] = Tools.list_back(v_, self.__index_)
        return dict_t

    def analysis_entities(self, keys: Union[str, List[str]] = None) -> dict:
        dict_ = dict()
        for k_, v_ in super().analysis_entities(keys).items():
            dict_[k_] = Tools.list_back(v_, self.__index_)
        return dict_

    def analysis_json(self, function_, *args, **kwargs) -> dict:
        dict_ = dict()
        for k_, v_ in super().analysis_json(function_, *args, **kwargs).items():
            dict_[k_] = Tools.list_back(v_, self.__index_)
        return dict_

    @property
    def json_list(self):
        return Tools.list_back(super().json_list, self.__index_)

    @property
    def analysis_list(self):
        return Tools.list_back(super().analysis_list, self.__index_)
