from collections import Counter
import numpy as np
import csv
import pandas as pd
from spellchecker import SpellChecker
from searchmanage import SearchManage
from deal import get_item
import similarity.simi
spell = SpellChecker()

import torch
from transformers import BertModel, BertTokenizer



search_m2 = SearchManage(key='ids', m_num=1000)
search_m1 = SearchManage(key='search', m_num=1000)
re3 = search_m2.search_run(points=["Q30"],
                           keys=['claims/P/value'])['claims/P/value']
print(re3)
