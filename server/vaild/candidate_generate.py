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


def generate_poi_candidates(candidate_dict,
                            opening_data,
                            funliday_stop_time_dict,
                            label_list,
                            day,
                            start_time,
                            end_time,
                            num_results):
    pass_poi_list = list()
    for doc in candidate_dict:
        for time in doc['OPENING_TIME_DICT_FLOAT'][day]:
            if time[0] < start_time and time[1] > end_time:
                match_label = set(label_list) & set(doc['labels'])
                if match_label:
                    if doc['FUNLIDAY_ATTRACTION'] not in pass_poi_list:
                        pass_poi_list.append([doc['FUNLIDAY_ATTRACTION'], doc['COUNT'], len(match_label)])
                        break

    pass_open_list = list()
    pass_stop_list = list()
    for _ in pass_poi_list:
        if _[0] in opening_data:
            for times in opening_data[_[0]][day]:
                if times[0] < start_time and times[1] > end_time:
                    pass_open_list.append(_[0])
                elif times[0] == 0 and times[1] == 24:
                    pass_open_list.append(_[0])
                else:
                    pass_poi_list.remove(_)
        else:
            pass_poi_list.remove(_)

        if _[0] in funliday_stop_time_dict:
            if funliday_stop_time_dict[_[0]] <= (end_time - start_time):
                pass_stop_list.append(_[0])
                time_diff = abs((end_time - start_time) - funliday_stop_time_dict[_[0]])
                _.append(time_diff)
            else:
                pass_poi_list.remove(_)
        else:
            pass_poi_list.remove(_)

    pass_poi_list = sorted(pass_poi_list, key=lambda x: x[-1])

    return pass_poi_list[:num_results]


if __name__ == '__main__':
    from server.vaild.infodata_loader import DataPreprocess
    from server.vaild.cost_time_check import TimeCostChecker
    from server.vaild.opentime_check import OpenTimeChecker

    with open('/home/annhsu/Test/reading_project/test_data.json', 'r') as f:
        test_data = json.load(f)

    start = time.time()
    dp = DataPreprocess()
    route_data = dp.get_route_data()
    use_stop_time_dict = dp.get_raw_stop_time()
    opening_data_dict = dp.get_raw_opening_time()
    candidate_dict = dp.get_candidate_poi()

    time_checker = TimeCostChecker(gpt_result_data=test_data, use_stop_time_dict=use_stop_time_dict, route_data=route_data)
    allday_overtime_vaild_days, stop_vaild_poi, gpt_result_data = time_checker.main()

    opening_checker = OpenTimeChecker(gpt_result_data=gpt_result_data, opening_data=opening_data_dict)
    open_vaild_poi = opening_checker.check_open_time(5, 3)

    print(open_vaild_poi)

    generate_poi_candidates(candidate_dict,
                            opening_data_dict,
                            use_stop_time_dict,
                            ['親子', '藝文'],
                            '星期五',
                            14,
                            20.5,
                            5)
    print(time.time()-start)
