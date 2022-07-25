# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/6/6 
# @function: Example of SearchManage.
# @version : V1.00
import random
import types

import kwargs as kwargs
import pandas as pd
from google.cloud.talent_v4beta1 import types
from spellchecker import SpellChecker
from searchmanage import SearchManage
from deal import get_item
import similarity.simi
import  requests
import wikipedia

from searchmanage.tools.Tools import agents

"hynochetos jubatus"
df=pd.read_csv("test1.csv")
df.drop_duplicates(inplace=True)
df.to_csv("aa.csv",index=False)