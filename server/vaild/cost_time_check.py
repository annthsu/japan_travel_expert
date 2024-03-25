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


class TimeCostChecker:
    def __init__(self, gpt_result_data: dict, use_stop_time_dict: dict, route_data: dict) -> None:
        self.gpt_result_data = gpt_result_data
        self.funliday_stop_time = use_stop_time_dict
        self.route_data = route_data

    def count_stop_time(self):
        """ 計算停留時間， gpt用gpt的result中的停留時間，funliday用自己的停留時間

        Args:
            gpt_result (dict): _description_
            funliday_stop_time (dict): _description_

        Returns:
            _type_: _description_
        """

        # 停留時間
        gpt_time_reccord = [list(value['Attractions'][atts]['Stay_time'] for atts in value['Attractions'].keys()) for key, value in self.gpt_result_data.items()]
        path_reccord = [list(atts for atts in value['Attractions'].keys()) for key, value in self.gpt_result_data.items()]
        funliday_stop_time_mapping_list = [list(self.funliday_stop_time[atts] for atts in value['Attractions'].keys()) for key, value in self.gpt_result_data.items()]
        cost_time_per_day = list(value['cost_time'] for key, value in self.gpt_result_data.items())

        # print('cost_time_per_day',cost_time_per_day)

        for key, value in self.gpt_result_data.items():
            value['pois'] = list(value['Attractions'].keys())

        self.gpt_result_data['cost_time_per_day'] = cost_time_per_day

        return gpt_time_reccord, path_reccord, funliday_stop_time_mapping_list

    def count_traffic_time(self, path_reccord: dict):
        # OSRM交通時間
        traffic_time = list()
        for day in tqdm(path_reccord):
            day_tmp_rec = list()
            for idx1, att1 in enumerate(day[:-1]):
                # print(f'{att1}--->{day[idx1+1]}--->{route_data[att1][day[idx1+1]]}')
                day_tmp_rec.append(self.route_data[att1][day[idx1+1]]['duration'])
            traffic_time.append(day_tmp_rec)
            # print('-------------------')

        print('traffic_time', traffic_time)
        return traffic_time

    @staticmethod
    def sum_time(traffic_time, gpt_time_reccord, funliday_stop_time_mapping_list):

        def combine_times(data_source_list: list):
            tmp_rec = list()
            for day, (travel, time) in enumerate(zip(traffic_time, data_source_list)):
                print(day, (travel, time))
                travel.extend(time)

                # tmp_rec.extend(travel)
                tmp_rec.append(sum(travel))
                print(sum(tmp_rec))

                # print('-------------------')

            return tmp_rec

        result = dict()
        for idx, (content, name) in enumerate(zip([gpt_time_reccord, funliday_stop_time_mapping_list], ['gpt', 'funliday'])):
            combine_result = combine_times(content)
            result[name] = combine_result

            print('combine_result', combine_result)
            print('='*20)

        return result

    def check_all_day_overtime(self, sum_time_dict):

        def check_overtime_by_type(keyname, threshold=0.5):
            record_dict = dict()
            record_dict.setdefault(keyname, dict())

            for idx, (gpt_cost_time, sum_time) in enumerate(zip(self.gpt_result_data['cost_time_per_day'], sum_time_dict[keyname]), start=1):
                if gpt_cost_time+threshold < sum_time:
                    print(f'{idx}超時了')
                    if 'over_time_days' not in record_dict[keyname]:
                        record_dict[keyname]['over_time_days'] = []
                    record_dict[keyname]['over_time_days'].append(idx)
                    record_dict[keyname][idx] = {'gpt_cost_time': gpt_cost_time, 'cal_time': sum_time}
                else:
                    print(f'{idx}沒超時')
            print('='*20)
            return record_dict

        result_dict = dict()
        for _ in sum_time_dict.keys():
            record_dict = check_overtime_by_type(_)
            result_dict.update(record_dict)
            # print(record_dict)

        return result_dict

    def check_vaild_stop_time(self):
        result_list = list()
        for idx, value in enumerate(self.gpt_result_data.values()):
            tmp_dict = dict()
            tmp_list = list()
            if 'pois' in value:
                for att_idx, atts in enumerate(value['pois']):
                    funliday_stop_time = self.funliday_stop_time[atts]
                    gpt_stop_time = value['Attractions'][atts]['Stay_time']
                    if not funliday_stop_time-1 <= gpt_stop_time <= funliday_stop_time+1:
                        if 'vaild_poi' not in tmp_dict:
                            tmp_dict['vaild_poi'] = dict()
                            tmp_dict['vaild_poi']['pois'] = list()
                        if atts not in tmp_dict['vaild_poi']:
                            tmp_dict['vaild_poi'][atts] = dict()

                        tmp_dict['vaild_poi']['pois'].append(atts)

                        tmp_dict['vaild_poi'][atts]['day'] = list(self.gpt_result_data.keys())[idx]
                        tmp_dict['vaild_poi'][atts]['funliday_stop_time'] = funliday_stop_time
                        tmp_dict['vaild_poi'][atts]['gpt_stop_time'] = gpt_stop_time

                        try:
                            if att_idx-1 >= 0:
                                tmp_dict['vaild_poi'][atts]['last_poi'] = value['pois'][att_idx-1]
                            else:
                                tmp_dict['vaild_poi'][atts]['last_poi'] = None
                        except IndexError:
                            tmp_dict['vaild_poi'][atts]['last_poi'] = None

                        try:
                            # if att_idx+1 < len(value['pois']):
                            tmp_dict['vaild_poi'][atts]['next_poi'] = value['pois'][att_idx+1]
                        except IndexError:
                            tmp_dict['vaild_poi'][atts]['next_poi'] = None

                if tmp_dict:
                    tmp_dict['day'] = list(self.gpt_result_data.keys())[idx]
                    result_list.append(tmp_dict)

                    #     print(f'{atts}的停留時間有問題')
                    # else:
                    #     print(f'{atts}的停留時間正常')
            # if tmp_list:
            #     result_list.append(tmp_list)
        return result_list

    def main(self):
        gpt_time_reccord, path_reccord, funliday_stop_time_mapping_list = self.count_stop_time()
        traffic_time = self.count_traffic_time(path_reccord)
        result = TimeCostChecker.sum_time(traffic_time, gpt_time_reccord, funliday_stop_time_mapping_list)

        # print('gpt_result',gpt_result)
        all_time_vaild_dict = self.check_all_day_overtime(result)
        op_time_vaild_dict = self.check_vaild_stop_time()

        return all_time_vaild_dict, op_time_vaild_dict, self.gpt_result_data


if __name__ == '__main__':
    from server.vaild.infodata_loader import DataPreprocess
    dp = DataPreprocess()
    route_data = dp.get_route_data()

    with open('/home/annhsu/Test/reading_project/test_data.json', 'r') as f:
        test_data = json.load(f)
    use_stop_time_dict = dp.get_raw_stop_time()
    opening_data_dict = dp.get_raw_opening_time()

    time_checker = TimeCostChecker(gpt_result_data=test_data, use_stop_time_dict=use_stop_time_dict, route_data=route_data)
    allday_overtime_vaild_days, stop_vaild_poi, gpt_result_data = time_checker.main()

    print('stop_vaild_poi', stop_vaild_poi)
