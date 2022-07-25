import time
import numpy as np
import requests
import csv


# 查询管理器
class SearchManage:
    # 构造函数
    def __init__(self, action_str='wbsearchentities', format_str='json', language='en', type_str='item',
                 limit_num=5):
        """
        :param action_str: 功能选择
        :param format_str: 返回格式，默认为json
        :param language: 语言选择，默认为英文
        :param type_str: 查找类别，实体：‘item’，属性：‘property’等，默认为‘item’
        :param limit_num:查找返回个数
        """
        self.url_api = "https://www.wikidata.org/w/api.php"
        self.action_str = action_str
        self.data_json = None
        if action_str == 'wbsearchentities':
            self.params = {
                'search': None,
                'action': action_str,
                'format': format_str,
                'language': language,
                'type': type_str,
                'limit': limit_num
            }
        elif self.action_str == 'wbgetentities':
            self.params = {
                'ids': None,
                'action': action_str,
                'format': format_str,
                'languages': language
            }
        else:
            print('param:action_str Error!')
            return

    # 开始运行查找
    def search_run(self, point_str):
        start_time = time.time()
        search_time = 0
        keys = None
        for key, value in self.params.items():
            keys = key
            break
        if type(point_str) == list:
            self.data_json = []
            if type(point_str[0]) == list:
                for i_t in point_str:
                    result_t = []
                    for i in i_t:
                        self.params[keys] = i
                        try:
                            result = requests.get(self.url_api, params=self.params)
                            search_time += 1
                        except Exception as e:
                            print(e)
                            return
                        result_t.append(result.json())
                    self.data_json.append(result_t)
            else:
                for i in point_str:
                    self.params[keys] = i
                    try:
                        result = requests.get(self.url_api, params=self.params)
                        search_time += 1
                    except Exception as e:
                        print(e)
                        return
                    self.data_json.append(result.json())
        else:
            self.params[keys] = point_str
            try:
                result = requests.get(self.url_api, params=self.params)
                search_time += 1
            except Exception as e:
                print(e)
                return
            self.data_json = result.json()
        end_time = time.time()
        print(f'Search {search_time} entities Time Cost:%3fs' % (end_time - start_time))
        return self.data_json

    # 返回json结果
    def json_return(self):
        return self.data_json

    # 解析json数据
    def json_analysis(self):
        """
        :return: type为字典，keys:'ids','label','url','describe'
        """
        if self.action_str == 'wbsearchentities':
            id_ = []
            url_ = []
            label_ = []
            describe_ = []
            if type(self.data_json) == list:
                if type(self.data_json[0]) == list:
                    for data_t1 in self.data_json:
                        id_t1 = []
                        url_t1 = []
                        label_t1 = []
                        describe_t1 = []
                        for data in data_t1:
                            id_t = []
                            url_t = []
                            label_t = []
                            describe_t = []
                            if data['success'] == 1:
                                for data_t in data['search']:
                                    try:
                                        id_t.append(data_t['id'])
                                    except Exception as e:
                                        print(e)
                                        id_t.append(None)
                                    try:
                                        url_t.append(data_t['concepturi'])
                                    except Exception as e:
                                        print(e)
                                        url_t.append(None)
                                    try:
                                        label_t.append(data_t['label'])
                                    except Exception as e:
                                        print(e)
                                        label_t.append(None)
                                    try:
                                        describe_t.append(data_t['description'])
                                    except Exception as e:
                                        print(e)
                                        describe_t.append(None)
                            else:
                                print(f'Search:{data["searchinfo"]["search"]},Come to Noting!')
                            id_t1.append(id_t)
                            label_t1.append(label_t)
                            url_t1.append(url_t)
                            describe_t1.append(describe_t)
                        id_.append(id_t1)
                        label_.append(label_t1)
                        url_.append(url_t1)
                        describe_.append(describe_t1)
                else:
                    for data in self.data_json:
                        id_t = []
                        url_t = []
                        label_t = []
                        describe_t = []
                        if data['success'] == 1:
                            for data_t in data['search']:
                                try:
                                    id_t.append(data_t['id'])
                                except Exception as e:
                                    print(e)
                                    id_t.append(None)
                                try:
                                    url_t.append(data_t['concepturi'])
                                except Exception as e:
                                    print(e)
                                    url_t.append(None)
                                try:
                                    label_t.append(data_t['label'])
                                except Exception as e:
                                    print(e)
                                    label_t.append(None)
                                try:
                                    describe_t.append(data_t['description'])
                                except Exception as e:
                                    print(e)
                                    describe_t.append(None)
                        else:
                            print(f'Search:{data["searchinfo"]["search"]},Come to Noting!')
                        id_.append(id_t)
                        url_.append(url_t)
                        label_.append(label_t)
                        describe_.append(describe_t)
            else:
                if self.data_json['success'] == 1:
                    for data_t in self.data_json['search']:
                        try:
                            id_.append(data_t['id'])
                        except Exception as e:
                            print(e)
                            id_.append(None)
                        try:
                            url_.append(data_t['concepturi'])
                        except Exception as e:
                            print(e)
                            url_.append(None)
                        try:
                            label_.append(data_t['label'])
                        except Exception as e:
                            print(e)
                            label_.append(None)
                        try:
                            describe_.append(data_t['description'])
                        except Exception as e:
                            print(e)
                            describe_.append(None)
                    else:
                        print(f'Search:{self.data_json["searchinfo"]["search"]},Come to Noting!')
            return {'ids': id_, 'label': label_, 'url': url_, 'describe': describe_}
        elif self.action_str == 'wbgetentities':
            pass

    # 打印管理器属性
    def manage_describe(self):
        print('-----------------------------------------------')
        print(f'Url:{self.url_api}\nAction:{self.action_str}\n'
              f'Params:{self.params}\nHave Run Searched?:{self.data_json is not None}')


# 读取csv文件
def read_csv(filename):
    data_list = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # 跳过表头
            next(f)
            for data in reader:
                data_list.append(data)
    except Exception as e:
        print(e)
        return
    print(f'File:{filename} Read Successfully!')
    # 将结果列表转置
    data_arr = np.array(data_list)
    data_list_t = (data_arr.transpose()).tolist()
    # 2×2表与转置后的表
    return data_list, data_list_t


# 层次结构
def hierarchical_structure(temp_other, hie_level=0, max_level=None):
    type_temp = type(temp_other)
    level_num = hie_level
    print('\t' * level_num, level_num, type_temp)
    # 是否指定最大搜索深度
    if max_level is not None:
        if hie_level == max_level:
            return
    if type_temp == dict:
        print('\t' * level_num, f'Length:{len(temp_other)}')
        if len(temp_other) == 0:
            print('\t' * level_num, 'None')
        else:
            num = 1
            for keys, values in temp_other.items():
                print('\t' * level_num, f'{level_num}.{num}', keys)
                num += 1
                hierarchical_structure(values, hie_level=level_num + 1, max_level=max_level)
    elif type_temp == list:
        print('\t' * level_num, f'Length:{len(temp_other)}')
        if len(temp_other) == 0:
            print('\t' * level_num, 'None')
        else:
            hierarchical_structure(temp_other[0], hie_level=level_num + 1, max_level=max_level)


if __name__ == '__main__':
    # csv文件路径
    file_path = 'data\\SemTab2020_Table_GT_Target\\Round1\\tables\\0007GMF5.csv'
    data_temp, data_temp_t = read_csv(file_path)
    # 建立搜索管理器
    action1 = SearchManage(action_str='wbsearchentities')
    # 运行查找
    action1.search_run(data_temp_t)
    # 解析查找结果
    result_temp1 = action1.json_analysis()
    print(result_temp1)
    # 建立搜索管理器
    action2 = SearchManage(action_str='wbgetentities')
    # 运行查找
    result_temp2 = action2.search_run(result_temp1['ids'][0])
    print(result_temp2)
    hierarchical_structure(result_temp2)
