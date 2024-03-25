import pandas as pd
import pandarallel
from tqdm.notebook import tqdm
import json
import time
import re
from liontk.mongo.mongo import MongoMgr
from liontk.enum.mongo import Mongo
from collections import OrderedDict
from collections import defaultdict
from collections import Counter
import re
import statistics
import math


class DataPreprocess:

    def __init__(self) -> None:
        self.raw_data = pd.read_csv('/home/annhsu/Test/reading_project/0312_poi_data.csv')
        # self.sum_dict = json.load(open('/home/annhsu/Test/reading_project/travel_edge_dict_tokyo.json', 'r'))
        # self.total_poi_lst = json.load(open('/home/annhsu/Test/reading_project/total_poi.json', 'r'))
        self.route_data = json.load(open('/home/annhsu/Test/reading_project/tokyo_poi_distance_driving.json', 'r'))
        # self.funliday_stop_time_dict = json.load(open('/home/annhsu/Test/reading_project/tokydf_time.json', 'r'))
        self.use_stop_time_dict = json.load(open('/home/annhsu/Test/reading_project/0319_funliday_stop_time_dict.json', 'r'))

        opening_data = self.raw_data[['FUNLIDAY_ATTRACTION', 'OPENING_TIME_DICT_FLOAT']].to_dict('records')
        self.opening_data_dict = dict()
        for doc in opening_data:
            doc['OPENING_TIME_DICT_FLOAT'] = eval(doc['OPENING_TIME_DICT_FLOAT'])
            self.opening_data_dict[doc['FUNLIDAY_ATTRACTION']] = doc['OPENING_TIME_DICT_FLOAT']

        poi_cand_df = self.raw_data[(self.raw_data['exclude_types'] == '[]') & (self.raw_data['OPENING_TIME_DICT_FLOAT'] != f'{{}}')]
        self.candidate_dict = poi_cand_df.to_dict('records')
        for doc in self.candidate_dict:
            doc['labels'] = eval(doc['labels'])
            doc['OPENING_TIME_DICT_FLOAT'] = eval(doc['OPENING_TIME_DICT_FLOAT'])

    def get_route_data(self):
        return self.route_data

    def get_raw_stop_time(self):
        return self.use_stop_time_dict

    def get_raw_opening_time(self):
        return self.opening_data_dict

    def get_candidate_poi(self):
        return self.candidate_dict


if __name__ == '__main__':
    dp = DataPreprocess()
    dp.get_route_data()
