import get_item
import similarity
from similarity import simi
from datetime import date
from spellchecker import SpellChecker
import numpy as np
spell = SpellChecker()
import torch
from transformers import BertModel, BertTokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
def is_valid_date(strdate):
    '''判断是否是一个有效的日期字符串'''
    try:
        if ":" in strdate:
            time.strptime(strdate, "%Y-%m-%d %H:%M:%S")
        else:
            time.strptime(strdate, "%Y-%m-%d")
        return True
    except:
        return False

def getsimi_base_on_bert(sentenceA,sentenceB):
    text_dictA = tokenizer.encode_plus(sentenceA, add_special_tokens=True, return_attention_mask=True)
    input_ids = torch.tensor(text_dictA['input_ids']).unsqueeze(0)
    token_type_ids = torch.tensor(text_dictA['token_type_ids']).unsqueeze(0)
    attention_mask = torch.tensor(text_dictA['attention_mask']).unsqueeze(0)
    resA = model(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
    afterA = resA[1].squeeze(0)
    text_dictB = tokenizer.encode_plus(sentenceB, add_special_tokens=True, return_attention_mask=True)
    input_ids = torch.tensor(text_dictB['input_ids']).unsqueeze(0)
    token_type_ids = torch.tensor(text_dictB['token_type_ids']).unsqueeze(0)
    attention_mask = torch.tensor(text_dictB['attention_mask']).unsqueeze(0)
    resB = model(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
    afterB = resB[1].squeeze(0)
    return torch.cosine_similarity(afterA, afterB, dim=0).data.item()
cell1=""
cell2=""
#对cell1与cell2进行cea查询，若能都出结果，则直接进行查询
def cpa_1(qid_1, qid_2):
    qid_1_claims = get_item.get_claims(qid_1);
    qid_2_claims=get_item.get_claims(qid_2)
    result={'ans':''}
    dic = {}
    for key in qid_1_claims:
        for candidate in qid_1_claims[key]:
            if candidate['mainsnak']['datatype'] == 'wikibase-item':
                if qid_2==candidate['mainsnak']['datavalue']['value']['id']:
                    result['ans']=candidate['mainsnak']['property']
    for key in qid_2_claims:
        for candidate in qid_2_claims[key]:
            if candidate['mainsnak']['datatype'] == 'wikibase-item':
                 if qid_1 == candidate['mainsnak']['datavalue']['value']['id']:
                     result['ans'] = candidate['mainsnak']['property']

    return  result
#其中一者出结果
def cpa_2(qid_1, item):
    qid_1_claims = get_item.get_claims(qid_1);
    #错别字纠正
    item=SpellChecker.correction(self=spell, word=item)
    result={'ans':''}
    dic = {}
    type=""
    mark=0
    tempmark=0
    for key in qid_1_claims:
        for candidate in qid_1_claims[key]:
            if candidate['mainsnak']['datatype']   != 'wikibase-item':
                type=candidate['mainsnak']['datavalue']['type']
                if type == 'string':
                    tempmark = getsimi_base_on_bert(item,candidate['mainsnak']['datavalue']['type'])
                    if tempmark >= 0.9 and tempmark > mark:
                        mark = tempmark
                        result['ans'] = candidate['mainsnak']['property']

                elif type=="quantity" and item.isdigit():
                    amount=candidate['mainsnak']['datavalue']['value']['amount']
                    tempmark = getsimi_base_on_bert(item, amount)
                    if tempmark >= 0.9 and tempmark > mark:
                        mark = tempmark
                        result['ans'] = candidate['mainsnak']['property']
                elif type=="time" and is_valid_date(item):
                    amount = candidate['mainsnak']['datavalue']['value']['time']
                    tempmark = getsimi_base_on_bert(item, amount)
                    if tempmark >= 0.9 and tempmark > mark:
                        mark = tempmark
                        result['ans'] = candidate['mainsnak']['property']


    return  result