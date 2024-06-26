

class OpenTimeChecker(object):

    def __init__(self, gpt_result_data: dict, opening_data: dict) -> None:
        self.gpt_result_data = gpt_result_data
        self.opening_data_dict = opening_data

    def check_open_time(self, start_idx, total_days):
        weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        choose_days = [weekdays[(start_idx-1+i) % len(weekdays)] for i in range(total_days)]
        vaild_poi = list()

        for att_idx, (value, weekday), in enumerate(zip(self.gpt_result_data.items(), choose_days)):
            for atts in self.gpt_result_data[value[0]]['Attractions'].keys():
                last_poi = None
                next_poi = None
                opening_data = self.opening_data_dict[atts]
                attraction_data = self.gpt_result_data[value[0]]['Attractions'][atts]
                # if 'poi' in self.gpt_result_data[value[0]]:
                find_index = self.gpt_result_data[value[0]]['pois'].index(atts)
                try:
                    if find_index-1 >= 0:
                        last_poi = self.gpt_result_data[value[0]]['pois'][find_index-1]
                    else:
                        last_poi = None
                except IndexError:
                    last_poi = None

                try:
                    next_poi = self.gpt_result_data[value[0]]['pois'][find_index+1]
                except IndexError:
                    next_poi = None

                if opening_data:
                    times = opening_data[weekday]
                    if len(times) > 1:
                        for time in times:
                            vaild_poi += OpenTimeChecker.check_time(attraction_data,
                                                                    time,
                                                                    atts,
                                                                    weekday,
                                                                    list(self.gpt_result_data.keys())[att_idx],
                                                                    last_poi,
                                                                    next_poi
                                                                    )
                    else:
                        vaild_poi += OpenTimeChecker.check_time(attraction_data,
                                                                times[0],
                                                                atts,
                                                                weekday,
                                                                list(self.gpt_result_data.keys())[att_idx],
                                                                last_poi,
                                                                next_poi)

        return vaild_poi

    @staticmethod
    def check_time(attraction_data,
                   time,
                   atts,
                   weekday,
                   day,
                   last_poi,
                   next_poi):
        vaild_poi = []
        # sart_time 跟 end_time 都不為0 代表有營業
        if time[0] == 0 and time[1] == 24:
            pass
        elif time[0] != 0 and time[1] != 0:
            if (attraction_data['Start_time'] < time[0]) or \
                    (attraction_data['End_time'] > time[1]):
                print(f'{atts}的開放時間有問題')
                vaild_poi.append({atts: {'GPTStart_time': attraction_data['Start_time'],
                                         'GPTEnd_time': attraction_data['End_time'],
                                         'FunlidayStart_time': time[0],
                                         'FunlidayEnd_time': time[1],
                                         'weekday': weekday,
                                         'day': day,
                                         'last_poi': last_poi,
                                         'next_poi': next_poi}})
        else:
            print(f'{atts}的開放時間有問題')
            vaild_poi.append({atts: {'GPTStart_time': attraction_data['Start_time'],
                                     'GPTEnd_time': attraction_data['End_time'],
                                     'FunlidayStart_time': time[0],
                                     'FunlidayEnd_time': time[1],
                                     'weekday': weekday,
                                     'day': day,
                                     'last_poi': last_poi,
                                     'next_poi': next_poi}})

        return vaild_poi
