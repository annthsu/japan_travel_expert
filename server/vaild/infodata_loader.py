import pandas as pd
import json


class DataPreprocess:

    def __init__(self) -> None:
        self.raw_data = pd.read_csv('/data/0312_poi_data.csv')
        self.route_data = json.load(open('/data/tokyo_poi_distance_driving.json', 'r'))
        self.use_stop_time_dict = json.load(open('/data/0319_funliday_stop_time_dict.json', 'r'))

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
