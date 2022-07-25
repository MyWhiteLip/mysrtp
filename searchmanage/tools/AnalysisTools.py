# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/6/12 
# @function: some tools of analysis
# @version : V1.0 
#
import re
from typing import Union, List

# Wikidata Data-type
data_type = {
    'commonsMedia': 'string',
    'globe-coordinate': 'globecoordinate',
    'wikibase-item': 'wikibase-entityid',
    'wikibase-property': 'wikibase-entityid',
    'string': 'string',
    'monolingualtext': 'monolingualtext',
    'external-id': 'string',
    'quantity': 'quantity',
    'time': 'time',
    'url': 'string',
    'math': 'string',
    'geo-shape': 'string',
    'musical-notation': 'string',
    'tabular-data': 'string',
    'wikibase-lexeme': 'wikibase-entityid',
    'wikibase-form': 'wikibase-entityid',
    'wikibase-sense': 'wikibase-entityid'
}

# Wikidata Value-type
value_type = {
    'wikibase-entityid': [1, 'id', 'entity-type', 'numeric-id'],
    'globecoordinate': [2, 'latitude', 'longitude', 'precision', 'globe'],
    'time': [1, 'time', 'precision', 'before', 'after', 'timezone'],
    'string': None,
    'monolingualtext': [2, 'text', 'language'],
    'quantity': [1, 'amount', 'lowerBound', 'upperBound']
}

# Regular expression
ree = re.compile("/")

# Analysis patten1
patten1 = ['labels', 'descriptions', 'aliases']


def search_analysis(json_: dict, keys: Union[str, list] = None) -> dict:
    if keys is None:
        raise KeyError("Please input keys you want to analysis.")
    try:
        if json_['success'] != 1:
            raise ValueError("Search filed.")
    except KeyError:
        raise ValueError("Search filed")

    id_ = []
    url_ = []
    label_ = []
    describe_ = []
    match_ = []

    for da_ in json_['search']:
        try:
            id_.append(da_['id'])
        except KeyError:
            id_.append(None)
        try:
            url_.append(da_['url'])
        except KeyError:
            url_.append(None)
        try:
            label_.append(da_['label'])
        except KeyError:
            label_.append(None)
        try:
            describe_.append(da_['description'])
        except KeyError:
            describe_.append(None)
        try:
            match_.append(da_['match']['type'])
        except KeyError:
            match_.append(None)

    re_dict = {'id': id_, 'url': url_, 'label': label_, 'description': describe_, 'match': match_}
    if keys == 'all' or type(keys) == list:
        return re_dict
    try:
        return {keys: re_dict[keys]}
    except KeyError:
        print(f'No keys:{keys}')
        return re_dict


def keys_regular(keys: List[str]) -> List[Union[dict, None]]:
    re_ = []
    for key in keys:
        re_dict = {
            'key': key,
            'correct': 1,
            'root': None,
            'identity': None,
            'patten': None,
            'error': None
        }
        kl = ree.split(key)
        # labels,description,aliases
        if kl[0] in patten1:
            re_dict['root'] = kl[0]
            if len(kl) == 1:
                re_dict['patten'] = 0
            elif len(kl) == 2:
                if kl[1] == '':
                    re_dict['patten'] = 0
                else:
                    re_dict['patten'] = 1
                    re_dict['identity'] = kl[1]
            elif len(kl) == 3:
                if kl[1] == '' and kl[2] == '':
                    re_dict['patten'] = 0
                else:
                    re_dict['error'] = 'format'
                    re_dict['correct'] = 0
            else:
                re_dict['error'] = 'tooLong'
                re_dict['correct'] = 0

        # claims
        elif kl[0] == 'claims':
            re_dict['root'] = kl[0]
            if len(kl) == 1:
                re_dict['patten'] = 0
            elif len(kl) == 2:
                if kl[1] == '':
                    re_dict['patten'] = 0
                elif (kl[1].lower())[0] == 'p':
                    re_dict['patten'] = 0
                    re_dict['identity'] = kl[1]
                else:
                    re_dict['error'] = 'format'
                    re_dict['correct'] = 0
            elif len(kl) == 3:
                if kl[1] == '' and kl[2] == '':
                    re_dict['patten'] = 0
                elif (kl[1].lower())[0] == 'p':
                    re_dict['identity'] = kl[1]
                    if kl[2] == '':
                        re_dict['patten'] = 0
                    elif kl[2] == 'value':
                        re_dict['patten'] = 1
                    elif kl[2] == 'qualifiers-order':
                        re_dict['patten'] = 2
                    elif kl[2] == 'qualifiers':
                        re_dict['patten'] = 3
                    elif kl[2] == 'references':
                        re_dict['patten'] = 4
                    else:
                        re_dict['error'] = 'format'
                        re_dict['correct'] = 0
                else:
                    re_dict['error'] = 'format'
                    re_dict['correct'] = 0
            elif len(kl) == 4:
                if (kl[1].lower())[0] == 'p':
                    re_dict['identity'] = kl[1]
                    if kl[2] == '' and kl[3] == '':
                        re_dict['patten'] = 0
                    elif kl[2] == 'qualifiers' and kl[3] == '':
                        re_dict['patten'] = 3
                    elif kl[2] == 'references' and kl[3] == '':
                        re_dict['patten'] = 4
                    else:
                        re_dict['error'] = 'format'
                        re_dict['correct'] = 0
                else:
                    re_dict['error'] = 'format'
                    re_dict['correct'] = 0
            elif len(kl) == 5:
                if (kl[1].lower())[0] == 'p':
                    re_dict['identity'] = kl[1]

                    if kl[2] == 'qualifiers' and kl[3] == '' and kl[4] == '':
                        re_dict['patten'] = 3
                    elif kl[2] == 'references' and kl[3] == '' and kl[4] == '':
                        re_dict['patten'] = 4
                    else:
                        re_dict['error'] = 'format'
                        re_dict['correct'] = 0
                else:
                    re_dict['error'] = 'format'
                    re_dict['correct'] = 0
            else:
                re_dict['error'] = 'tooLong'
                re_dict['correct'] = 0

        # sitelinks
        elif kl[0] == 'sitelinks':
            re_dict['root'] = kl[0]
            if len(kl) == 1:
                re_dict['patten'] = 0
            elif len(kl) == 2:
                if kl[1] == '':
                    re_dict['patten'] = 0
                else:
                    re_dict['error'] = 'format'
                    re_dict['correct'] = 0
            elif len(kl) == 3:
                if kl[1] == '' and kl[2] == '':
                    re_dict['patten'] = 0
                else:
                    re_dict['error'] = 'format'
                    re_dict['correct'] = 0
            else:
                re_dict['error'] = 'tooLong'
                re_dict['correct'] = 0
        else:
            re_dict['error'] = 'root'
            re_dict['correct'] = 0
        re_.append(re_dict)
    return re_


def value_analysis(da_: dict) -> Union[tuple, float, str, int, None]:
    try:
        da = da_['mainsnak']
        da_t = da['datatype']
        va_t = data_type[da_t]
        value_l = value_type[va_t]
    except KeyError:
        return None
    if va_t == 'string':
        try:
            return da['datavalue']['value']
        except KeyError:
            return None
    else:
        num = value_l[0]
        if num == 1:
            try:
                return da['datavalue']['value'][value_l[1]]
            except KeyError:
                return None
        else:
            tuple_l = []
            for i in range(num):
                try:
                    tuple_l.append(da['datavalue']['value'][value_l[i + 1]])
                except KeyError:
                    tuple_l.append(None)
            tuple_ = tuple(tuple_l)
            return tuple_


def patten1_analysis(json_: dict, key: dict) -> Union[list, str, dict, None]:
    if key['patten'] == 0:
        try:
            return json_[key['root']]
        except KeyError:
            return {}
    else:
        try:
            da_ = json_[key['root']][key['identity']]
        except KeyError:
            if key['root'] == 'aliases':
                return []
            else:
                return None
        if key['root'] == 'aliases':
            re_ = []
            for da in da_:
                try:
                    re_.append(da['value'])
                except KeyError:
                    re_.append(None)
            return re_
        else:
            try:
                return da_['value']
            except KeyError:
                return None


def claims_analysis(json_: dict, key: dict) -> Union[list, dict]:
    if key['patten'] == 0:
        if key['identity'] is None:
            try:
                return json_['claims']
            except KeyError:
                return {}
        elif key['identity'].lower() == 'p':
            re_ = []
            try:
                for k_, v_ in json_['claims'].items():
                    re_.append(k_)
            except KeyError:
                pass
            return re_
        else:
            try:
                return json_['claims'][key['identity']]
            except KeyError:
                return []

    elif key['patten'] == 1:
        if key['identity'].lower() == 'p':
            try:
                da__: dict = json_['claims']
            except KeyError:
                return {}
            re_ = dict()
            for k_, v__ in da__.items():
                re_[k_] = []
                for v_ in v__:
                    re_[k_].append(value_analysis(v_))
            return re_
        else:
            try:
                da_ = json_['claims'][key['identity']]
            except KeyError:
                return []
            re_ = []
            for da in da_:
                re_.append(value_analysis(da))
            return re_

    elif key['patten'] == 2:
        re_ = []
        try:
            for da_ in json_[key['root']][key['identity']]:
                try:
                    re_.append(da_['qualifiers-order'])
                except KeyError:
                    re_.append([])
        except KeyError:
            pass
        return re_
    elif key['patten'] == 3:
        re_ = []
        try:
            for da_ in json_[key['root']][key['identity']]:
                try:
                    re_.append(da_['qualifiers'])
                except KeyError:
                    re_.append({})
        except KeyError:
            pass
        return re_
    elif key['patten'] == 4:
        re_ = []
        try:
            for da_ in json_[key['root']][key['identity']]:
                try:
                    re_.append(da_['references'])
                except KeyError:
                    re_.append({})
        except KeyError:
            pass
        return re_


def sitelinks_analysis(json_: dict, key: dict) -> dict:
    try:
        return json_[key['root']]
    except KeyError:
        return {}


def entities_analysis(json_: dict, keys: Union[str, List[str]] = None) -> List[dict]:
    if keys is None:
        raise KeyError("Please input keys you want to analysis.")
    try:
        if json_['success'] != 1:
            raise ValueError("Search filed.")
    except KeyError:
        raise ValueError("Search filed")

    if type(keys) is str:
        keys = [keys]
    keys_dict = keys_regular(keys)

    re_list = []
    for key_, value_ in json_['entities'].items():
        re_dict = dict()

        for k in keys_dict:
            re_dict[k['key']] = None
            if k['correct'] == 1:
                if k['root'] in patten1:
                    re_dict[k['key']] = patten1_analysis(value_, k)
                elif k['root'] == 'claims':
                    re_dict[k['key']] = claims_analysis(value_, k)
                elif k['root'] == 'sitelinks':
                    re_dict[k['key']] = sitelinks_analysis(value_, k)

        re_list.append(re_dict)
    return re_list
