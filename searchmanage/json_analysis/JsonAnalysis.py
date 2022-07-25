# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/6/12 
# @function: class of analysis of json data
# @version : V1.0 
#

from typing import Union
from searchmanage.tools.Tools import repeat_entities_back


class JsonAnalysis(object):

    def __init__(self):
        self.json = None
        self.ready_ = False
        self.analysis = None

    def set_data(self, json_: Union[dict, None] = None):
        if json_ is not None:
            self.ready_ = True
            self.json = json_

    def reset_analysis(self, analysis_: Union[None, dict, list]):
        self.analysis = analysis_

    def run_analysis(self, function, *args, **kwargs) -> Union[list, dict, None]:
        if self.ready_ is not True:
            raise ValueError("Json data is not ready.")
        if self.analysis is not None:
            self.analysis = None
        try:
            self.analysis = function(self.json, *args, **kwargs)
        except Exception as e:
            print(e)
        return self.analysis

    def correct_repeat(self, index: list):
        if self.analysis is None:
            return
        self.analysis = repeat_entities_back(self.analysis, index)

    def get_json(self) -> dict:
        return self.json

    def get_analysis(self) -> Union[list, dict, None]:
        return self.analysis

    def ready(self) -> bool:
        return self.ready_

    def clear(self):
        self.json = None
        self.analysis = None
        self.ready_ = False
