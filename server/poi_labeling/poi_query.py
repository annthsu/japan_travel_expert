import json
import statistics
from copy import deepcopy
from pprint import pprint
from time import time

import numpy as np
import pandas as pd
from geopy.distance import geodesic
from loguru import logger


class QueryPOI:
    def __init__(
        self,
        poi_file_path: str = "./data/pois_data.csv",
        labels_file_path: str = "./data/labels_shot.json",
    ) -> None:
        poi_df = pd.read_csv(poi_file_path)
        poi_df['labels'] = poi_df['labels'].fillna('[]').apply(eval)
        poi_df['exclude_types'] = poi_df['exclude_types'].apply(eval)
        poi_df['STOP_TIME'] = poi_df['STOP_TIME'].fillna('[]').apply(eval)
        poi_df['OPENING_TIME_DICT'] = poi_df['OPENING_TIME_DICT'].fillna(r'{}').apply(eval)
        poi_df['labeling_introduction'] = poi_df['labeling_introduction'].fillna('')
        self.poi_data = poi_df
        self.poi_labels = poi_df['labels']
        self.type_filter = poi_df['exclude_types'].str.len()==0
        self.poi_point_list = poi_df[['LONG', 'LAT']].values
        with open(labels_file_path, 'r') as reader:
            self.label_shots = json.load(reader)

    @staticmethod
    def _process_stop_time(stop_times: list, default_result: str = "Not Sure"):
        result = default_result
        if stop_times:
            stop_times = [
                eval(text.replace('小時', '*3600').replace('分', '*60').replace('秒', '').strip().replace(' ', '+'))
                for text in stop_times
            ]
            stop_times = sorted([s for s in stop_times if s])

            time = sorted(
                stop_times,
                key=lambda x: (stop_times.count(x)*-1, abs(statistics.mean(stop_times) - x)))
            if time:
                time = time[0]
                hours = time // 3600
                minutes = (time - 3600*hours) // 60
                seconds = time - (3600 * hours + 60 * minutes)
                final_text = []
                for digit, unit in zip([hours, minutes, seconds], ['hour', 'minute', 'second']):
                    if digit:
                        if digit > 1:
                            unit += 's'
                        final_text.append(f"{digit} {unit}")
                result = " and ".join(final_text)
        return result

    @staticmethod
    def _process_business_hours(opening_times: dict, default_result: str = "Not Sure"):
        result = default_result
        for value in opening_times.values():
            if value == '休息':
                continue
            elif value == '24 小時營業':
                result = '24 hours'
                break
            else:
                result = value.replace(' ', '')
                break
        return result

    @staticmethod
    def _overlap_coefficient(x, y):
        intersection = len(set(x) & set(y))
        # min_size = min(len(x), len(y))
        min_size = len(x)
        return intersection / min_size if min_size != 0 else 0

    @staticmethod
    def _jaccard_sim(x, y):
        intersection = np.sum(np.logical_and(x, y))
        union = np.sum(np.logical_or(x, y))
        jaccard_index = intersection / union
        return jaccard_index

    def add_poi_by_distance(self, sorted_poi, max_poi_count, max_distance: int = 5):
        logger.info(f"Now: {len(sorted_poi)}, max_poi_count: {max_poi_count}, max_distance: {max_distance}")
        used_indexs = [poi[0] for poi in sorted_poi]
        candidate_pois_indexs = self.poi_data[self.type_filter & ~(self.poi_data.index.isin(used_indexs)) & (self.poi_data['LONG'].notnull()) & (self.poi_data['LAT'].notnull())].sort_values(
            by=['COUNT'], ascending=False).index
        final_result = deepcopy(sorted_poi)

        run_times = 0
        max_times = len(sorted_poi) * len(candidate_pois_indexs)
        logger.info(f"Max Times: {max_times}")
        while run_times < max_times and len(final_result) < max_poi_count:
            for poi in sorted_poi:
                use_idx = poi[0]
                if len(final_result) >= max_poi_count:
                    break
                use_point = self.poi_point_list[use_idx]
                for candidate_idx in candidate_pois_indexs:
                    run_times += 1
                    if len(final_result) >= max_poi_count:
                        break
                    elif candidate_idx not in used_indexs:
                        candidate_point = self.poi_point_list[candidate_idx]
                        dist = geodesic(use_point[::-1], candidate_point[::-1]).km
                        if dist <= max_distance:
                            name = self.poi_data.iloc[candidate_idx]['ATTRACTION']
                            final_result.append((candidate_idx, name, dist))
                            used_indexs.append(candidate_idx)
                            break
        logger.info(f"Run Times: {run_times}")
        return final_result

    def preprocess_for_prompt(self, poi_indexs: list):
        tour_result = dict()
        desc_result = dict()

        for idx in poi_indexs:
            poi_data = self.poi_data.iloc[idx]
            name = poi_data['ATTRACTION']
            tmp_dict = tour_result.setdefault(name, dict())

            desc_result[name] = poi_data['labeling_introduction']
            tmp_dict['Latitude and longitude'] = f"({poi_data['LAT']:.3f}, {poi_data['LONG']:.3f})"
            tmp_dict['Business_hours'] = self._process_business_hours(poi_data['OPENING_TIME_DICT'])
            tmp_dict['Resident_time'] = self._process_stop_time(poi_data['STOP_TIME'])
        
        return tour_result, desc_result

    def query_poi(self, user_input: dict):
        max_poi_count = user_input['days'] * user_input['poi_each_day']
        labels_index = {label: idx for idx, label in enumerate(self.label_shots.keys())}
        user_array = np.zeros(len(labels_index))
        user_label = user_input['labels']
        for label in user_label:
            if label in labels_index:
                user_array[labels_index[label]] = 1

        city_filter = self.poi_data['G_CITY']==user_input['city']
        candidate_pois = self.poi_data[city_filter & self.type_filter]
        
        sim_results = []
        for index, candidate in zip(
            candidate_pois.index,
            candidate_pois.to_dict(orient='records')
        ):
            poi_label = candidate['labels']
            used_count = candidate['COUNT']
            name = candidate['ATTRACTION']

            poi_array = np.zeros(len(labels_index))
            for label in poi_label:
                if label in labels_index:
                    poi_array[labels_index[label]] = 1

            value = self._jaccard_sim(user_array, poi_array) + self._overlap_coefficient(user_label, poi_label)
            if value > 0:
                sim_results.append((index, value, used_count, poi_label, name))

        sorted_poi = sorted(sim_results, key=lambda x: (x[1], x[2]), reverse=True)[:max_poi_count]
        if len(sorted_poi) < max_poi_count:
            sorted_poi = self.add_poi_by_distance(sorted_poi, max_poi_count)
        
        logger.info(f"Query Result:\n{sorted_poi}")
        index_result = [poi[0] for poi in sorted_poi]
        return index_result
    
    def main(self, user_input: dict):
        logger.info(f"User Input: {user_input}")

        st = time()
        query_res = self.query_poi(user_input)
        tour_result, desc_result = self.preprocess_for_prompt(query_res)

        logger.info(f"Get {len(tour_result)} pois.")
        logger.info(f"Cost time: {time() - st: .1f} s")
        return tour_result, desc_result


if __name__ == "__main__":
    query_poi = QueryPOI()

    user_input = {
        "poi_each_day": 3,
        "days": 4,
        "city": "東京都",
        "labels": [
            "購物",
            "主題樂園"
        ]
    }

    result = query_poi.main(user_input)
    with open('./data/test_query_output.json', 'w') as writer:
        json.dump(result, writer, indent=4, ensure_ascii=False)
    pprint(result)

# python server/poi_labeling/poi_query.py
