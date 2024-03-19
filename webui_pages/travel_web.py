
from server.tour_generator.prompt_design import Japan_travel_itinerary_generation
from server.tour_generator.description_writer import Description_Writer
from server.poi_labeling.poi_query import QueryPOI
import gradio as gr
import pandas as pd
import random

re_list = []

def show_all_output(travel_days, travel_compactness, city, attraction_preferences, season):
    query_poi = QueryPOI()
    print(season)
    print(travel_days)
    print(travel_compactness)
    print(city)
    print(attraction_preferences)
    if travel_compactness =='鬆散':
        poi_each_day = 2
        level = 1
    
    elif travel_compactness =='普通':
        poi_each_day = random.choice([3, 4])
        level = 2

    else:
        poi_each_day = 5
        level = 3

    user_input = {
        "poi_each_day": poi_each_day,
        "days": int(travel_days),
        "city": city,
        "labels": attraction_preferences
    }
    print(user_input)
    poi_query = query_poi.main(user_input)

    print('poi')
    print(poi_query)
    new_poi_query = tuple(replace_quotes(item) for item in poi_query)
    itinerary_generation = Japan_travel_itinerary_generation(ref_data = new_poi_query[0], area=city, days=int(travel_days), season=season)
    itinerary = itinerary_generation.main()
    # Write description
    result_dict = Description_Writer().write(itinerary=itinerary, poi_query_description=new_poi_query[1])
    print(result_dict)
    re_list.append(result_dict)
    # all travel
    result = list()
    for day, info in result_dict.items():
        attractions = info['Attractions']
        a_list = list()
        for attraction, details in attractions.items():
            a_list.append(attraction)
        route1 = ' -> '.join(a_list)
        url_formet = '/'.join(a_list)
        url = f'https://www.google.com/maps/dir/{url_formet}'.replace(' ','')
        t = f'''<body>
            <h3 style="text-align: center; font-weight: bold;">{day}</h3>
            <h3 style="text-align: center; font-weight: bold;">{route1}</h3>
            <h3 style="text-align: center;"><a href={url} style="color: #0072E3;">google map</a></h3>
            </body>'''
        result.append(t)
    print(result)
    all_travel = ''.join(result)

    #df
    result = list()
    r_dict = {}
    r_dict['旅遊城市'] = city
    r_dict['旅遊季節'] = season
    if attraction_preferences != []:
        r_dict['行程主題'] = '+'.join(attraction_preferences)
    else:
        r_dict['行程主題'] = '無指定'

    r_dict['行程緊湊度'] = level*'🍜'
    result.append(r_dict)
    df = pd.DataFrame(result)

    print(df)

    return df, all_travel
    # return result_dict

def show_one_day_output(current_day, travel_days):
    map_info = get_map(current_day, travel_days)
    route_df = get_route_df(current_day, travel_days)
    day_description = get_day_description(current_day, travel_days)
    day_travel = get_day_travel(current_day, travel_days)

    return map_info, route_df, day_description, day_travel


def replace_quotes(obj):
    if isinstance(obj, dict):
        return {replace_quotes(key): replace_quotes(value) for key, value in obj.items()}
    elif isinstance(obj, str):
        return obj.replace("「", "*").replace("」", "*").replace("【", "*").replace("】", "*").replace("『", "*").replace("』", "*").replace("《", "*").replace("》","*").replace("'", "*").replace("\"", "*")
    else:
        return obj

def get_map(current_day, travel_days):
    result_dict = re_list[0]
    result = list()
    for day, info in result_dict.items():
        attractions = info['Attractions']
        a_list = list()
        for attraction, details in attractions.items():
            a_list.append(attraction)
        if len(a_list) > 0:
            begin = 'origin=日本' + a_list[0]
            del a_list[0]
        else:
            begin = ''
        if len(a_list) > 0:
            final = '&destination=日本' + a_list[-1]
            del a_list[-1]
        else:
            final = '&destination='+'日本機場'
        if len(a_list) > 0:
            medium = '&waypoints=日本'+'|日本'.join(a_list)
        else:
            medium = ''
        map_result = f'''
        <iframe width="600" height="450" style="border:0" loading="lazy" allowfullscreen src="https://www.google.com/maps/embed/v1/directions?{begin}{medium}{final}&mode=transit&key={key}"></iframe>
        '''
        print(map_result)
        result.append(map_result)

    if int(current_day) <= int(travel_days):
        map_info = result[int(current_day)-1]
    else:
        map_info = '<h3 style="font-weight: bold;">無資料</h3>'

    return map_info


def get_route_df(current_day, travel_days):

    result_dict = re_list[0]
    all_result = list()
    for day, info in result_dict.items():
        result = list()
        attractions = info['Attractions']
        for attraction, details in attractions.items():
            day_dict = {}
            day_dict['景點名稱'] = attraction
            print(details['Stay_time'])
            stay_time = details['Start_time'] + '~'+ details['End_time'] +' (' + details['Stay_time'] +')'
            day_dict['預計停留時間'] = stay_time
            result.append(day_dict)
        all_result.append(result)
    if int(current_day) <= int(travel_days):
        df = pd.DataFrame(all_result[int(current_day)-1])
    else:
        df = pd.DataFrame(columns=['景點名稱', '預計停留時間'])

    return df

def get_day_description(current_day, travel_days):
    result_dict = re_list[0]
    result = list()
    for day, info in result_dict.items():
        description = info['Description']
        title = info['Title']

        t = f'''<body>
          <h3></h3>
          <h3 style="text-align: center; font-weight: bold;">行程介紹:{title}</h3>
          <h3 style="text-align: center;">{description}</h3>
          </body>'''

        result.append(t)
    if int(current_day) <= int(travel_days):
        current_travel = result[int(current_day)-1]
        print(current_travel)
    else:
        current_travel = '<h3 style="font-weight: bold;">無資料</h3>'

    return current_travel


def get_day_travel(current_day, travel_days):
    result_dict = re_list[0]
    result = list()
    for day, info in result_dict.items():
        cost_time = round(info['cost_time'], 1)
        attractions = info['Attractions']

        a_list = list()
        for attraction, details in attractions.items():
            a_list.append(attraction)
        route1 = ' -> '.join(a_list)
        url_formet = '/'.join(a_list)
        url = f'https://www.google.com/maps/dir/{url_formet}'.replace(' ','')
        t = f'''<body>
          <h3 style="text-align: center; font-weight: bold;">{day}</h3>
          <h3 style="text-align: center; font-weight: bold;">{route1}</h3>
          <h3 style="text-align: center; font-weight: bold;">總花費時間: {cost_time} 小時</h3>
          <h3 style="text-align: center;"><a href={url} style="color: #0072E3;">google map</a></h3>
          <h3></h3>
          </body>'''
        result.append(t)
    if int(current_day) <= int(travel_days):
        current_travel = result[int(current_day)-1]
    else:
        current_travel = '<h3 style="font-weight: bold;">無資料</h3>'

    return current_travel

with gr.Blocks(theme='finlaymacklon/smooth_slate',title="日本旅遊規劃") as demo:

    with gr.Row():
        gr.HTML(f"<div style=\"text-align: center;\">\n<h1>🧫 日本旅遊規劃 🧫</h1>\n</div>")

    with gr.Row():
        with gr.Column():
            travel_days = gr.Dropdown(["1", "2", "3", "4", "5", "6", "7"], value='5', label="天數", info="請選擇總天數")
            travel_compactness = gr.Dropdown(["鬆散", "普通", "緊湊"], value='普通', label="行程緊湊度", info="請選擇一天想安排多少個景點")
            season = gr.Radio(['春天','夏天','秋天','冬天'], value='春天', label="旅行季節", info="請選擇旅行季節")
        with gr.Column():
            city = gr.Dropdown(["東京都"], value='東京都', label="城市", info="請選擇想去的城市")
            attraction_preferences = gr.CheckboxGroup(["購物", "親子", "藝文", "自然生態", "歷史古蹟", "戶外活動", "宗教", "動漫、二次元", "溫泉", "水上活動", "主題樂園"],label="行程主題", info="請選擇想要的主題類型")
    with gr.Row():
        result_but = gr.Button("結果!!!!")
    with gr.Tabs():
        gr.HTML(f"<div style=\"text-align: center;\">\n<h2>🎐 行程總覽</h2>\n<h2></h2></div>")
        with gr.Row():
            with gr.Column(variant="panel"):
                all_travel = gr.HTML()
                result_df_output = gr.Dataframe(interactive=False, wrap=False)
            with gr.Column(variant="panel"):
                current_day = gr.Dropdown(
                    ["1", "2", "3", "4", "5", "6", "7"], value='1', label="詳細行程", info="選擇第幾天行程")
                day_but = gr.Button("查看結果")
                map_output = gr.HTML()
                # result_df_output = gr.Dataframe(interactive=True, wrap=True)
    with gr.Tabs():
        gr.HTML(f"<div style=\"text-align: center;\">\n<h2>🎐 詳細行程內容</h2>\n<h2></h2></div>")
        day_travel = gr.HTML()
        with gr.Row():
            with gr.Column(variant="panel"):
                day_description = gr.HTML()
            with gr.Column(variant="panel"):
                gr.HTML('<h3></h3><h3 style="text-align: center; font-weight: bold;">行程規劃</h3>')
                df_output = gr.Dataframe(interactive=False, wrap=False)

    day_but.click(show_one_day_output, inputs=[current_day, travel_days], outputs=[map_output, df_output, day_description, day_travel])
    result_but.click(show_all_output, inputs=[travel_days, travel_compactness, city, attraction_preferences, season], outputs=[result_df_output, all_travel])

demo.launch(share=True)
