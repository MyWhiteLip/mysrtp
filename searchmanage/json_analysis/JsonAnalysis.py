# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/7/20 
# @function: the class for json data of analysis
# @version : V0.4.0
#

from typing import Union


class JsonAnalysis(object):
    """class of json data or a string and its analysis data.

    Use you own analysis function to analysis json data. Of course, you can
    use some simple function to analysis json data from wikidata API in
    searchmanage.tools.AnalysisTools.

    :ivar __json(Union[dict, str, None]): json data
    :ivar __ready_(bool): record whether json data is ready
    :ivar __analysis(Union[dict, list, str,None]): result of analysis for json data
    """

    def __init__(self):
        self.__json = None
        self.__ready_ = False
        self.__analysis = None

    def set_json(self, json_: Union[dict, str, None] = None):
        """Set json data. And if it's set successfully, then turn ready_ True.

        :param json_: json data you want to set
        :return: None
        """
        if json_ is not None:
            self.__ready_ = True
        self.__json = json_

    def set_analysis(self, analysis_: Union[None, dict, list]):
        """Set analysis data you get.

        :param analysis_: analysis data you want to set
        :return: None
        """
        self.__analysis = analysis_

    def run_analysis(self, function, *args, **kwargs) -> Union[list, dict, None]:
        """Analysis the json data or a str using your own function.

        :param function: your own analysis function
        :param args: you own function's parameters which format is tuple
        :param kwargs: you own function's parameters which format is dict
        :return: result of analysis json data or a string
        """
        if self.__ready_ is not True:
            raise ValueError("Json data is not ready.")
        if self.__analysis is not None:
            self.__analysis = None
        try:
            self.__analysis = function(self.__json, *args, **kwargs)
        except Exception as e:
            print(e)
        return self.__analysis

    @property
    def get_json(self) -> Union[dict, str, None]:
        """Get json data or a string.

        :return: json data or a string
        """
        return self.__json

    @property
    def get_analysis(self) -> Union[None, list, dict]:
        """Get analysis result.

        :return: analysis result
        """
        return self.__analysis

    @property
    def ready(self) -> bool:
        """Get whether json data is ready.

        :return: whether json data is ready
        """
        return self.__ready_

    def clear(self):
        """Init the object of this class.

        :return: None
        """
        self.__json = None
        self.__analysis = None
        self.__ready_ = False
