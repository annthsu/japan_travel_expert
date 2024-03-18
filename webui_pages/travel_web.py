
from server.tour_generator.prompt_design import Japan_travel_itinerary_generation
from server.tour_generator.description_writer import Description_Writer
from server.poi_labeling.poi_query import QueryPOI
import gradio as gr
import pandas as pd


def get_data(travel_days, travel_compactness, city, attraction_preferences, season):
    # query_poi = QueryPOI()
    print(season)
    print(travel_days)
    print(travel_compactness)
    print(city)
    print(attraction_preferences)
    user_input = {
        "poi_each_day": int(travel_days),
        "days": int(travel_compactness),
        "city": city,
        "labels": attraction_preferences
    }
    print(user_input)
    # poi_query = query_poi.main(user_input) 
    # # Generate itinerary
    # itinerary_generation = Japan_travel_itinerary_generation(ref_data = poi_query[0], area=city, days=int(travel_compactness), season=season)
    # itinerary = itinerary_generation.main()
    # # Write description
    # itin_with_des = Description_Writer().write(itinerary=itinerary, poi_query_description=poi_query[1])
    # print(itin_with_des)

    result_dict = {
  "DAY 1": {
    "Attractions": {
      "UNIQLO 銀座店": {
        "Start_time": "11:00",
        "End_time": "12:00",
        "Stay_time": 1.0
      },
      "日本橋": {
        "Start_time": "12:30",
        "End_time": "13:30",
        "Stay_time": 1.0
      },
      "東京站一番街": {
        "Start_time": "14:00",
        "End_time": "15:00",
        "Stay_time": 1.0
      },
      "東京動漫人物街": {
        "Start_time": "15:30",
        "End_time": "16:30",
        "Stay_time": 1.0
      }
    },
    "cost_time": 5.5,
    "Title": "銀座之旅",
    "Description": "第一天的行程將帶您遊覽東京的銀座區。早上11點，您可以前往位於銀座六丁目的UNIQLO全球旗艦店「UNIQLO 銀座店」。這家店在2021年進行了全新改裝，以展現日常服「LifeWear」的真實美感。在這裡，您可以購物、休憩，享受購物與美食的樂趣。\n\n接著，下午12點半，您可以前往日本橋，這是江戶時代德川家康建設的全國道路網計劃「五街道」的基點。現在的日本橋是第19代，於1911年興建的石造二連拱橋。這座橋被日本政府列為國家重要文化財，是一個具有歷史價值的地標。\n\n下午2點，您可以前往東京站一番街，這是一個位於東京站內的主題樂園，可以讓您深入體驗日本文化。這裡有東京動漫人物街、東京拉麵街、東京甜點樂園等各種店舖，讓您盡情享受購物和美食的樂趣。\n\n最後，在下午3點半，您可以前往東京動漫人物街，這個位於東京站一番街的商店匯集了國內外擁有超高人氣的動漫人物商品。在這裡，您可以找到寶可夢、蠟筆小新、Precure、角落小夥伴等各種動漫人物的商品。"
  },
  "DAY 2": {
    "Attractions": {
      "SHIBUYA SKY": {
        "Start_time": "10:00",
        "End_time": "11:00",
        "Stay_time": 1.0
      },
      "西澤荘": {
        "Start_time": "11:30",
        "End_time": "12:30",
        "Stay_time": 1.0
      },
      "明治神宮": {
        "Start_time": "13:00",
        "End_time": "14:00",
        "Stay_time": 1.0
      }
    },
    "cost_time": 4.0,
    "Title": "澀谷與明治神宮",
    "Description": "第二天的行程將帶您遊覽澀谷和明治神宮。早上10點，您可以前往澀谷SKY，這是一個可以欣賞東京369度夜景的夜景景點。您可以在這裡欣賞到壯麗的夜景，並在附近的商場逛逛，或者在可以欣賞夜景的地方喝一杯調酒。\n\n接著，上午11點半，您可以前往西澤荘。西澤荘是一個具有懷舊風情的地方，讓您感受到東京下町的魅力。\n\n下午1點，您可以前往明治神宮。明治神宮是一個具有百年歷史的公園，是日本第一座皇室賜贈的公園。在這裡，您可以參拜，欣賞到美麗的樹木，感受到日本人世世代代的堅持和祈福的力量。"
  },
  "DAY 3": {
    "Attractions": {
      "東京晴空塔": {
        "Start_time": "10:00",
        "End_time": "11:30",
        "Stay_time": 1.5
      },
      "御臺場": {
        "Start_time": "12:00",
        "End_time": "14:00",
        "Stay_time": 2.0
      },
      "御台場": {
        "Start_time": "14:30",
        "End_time": "15:30",
        "Stay_time": 1.0
      }
    },
    "cost_time": 5.5,
    "Title": "晴空塔與御臺場",
    "Description": "第三天的行程將帶您遊覽東京晴空塔和御臺場。早上10點，您可以前往位於押上站的晴空塔，這是東京的新地標。在晴空塔底下的solamachi商場，您可以享受購物的樂趣。\n\n接著，中午12點，您可以前往御臺場，這個地方的名稱源自於江戶時代的砲台。御臺場是一座以填海造陸方式打造的巨大人工島，是一個既具有美麗景色又是許多企業總部所在地的地方。\n\n下午2點半，您可以繼續在御臺場逛逛，欣賞這個地方的美景。"
  },
  "DAY 4": {
    "Attractions": {
      "上野": {
        "Start_time": "10:00",
        "End_time": "11:00",
        "Stay_time": 1.0
      },
      "上野恩賜公園": {
        "Start_time": "11:30",
        "End_time": "12:00",
        "Stay_time": 0.5
      },
      "小網神社": {
        "Start_time": "12:30",
        "End_time": "12:50",
        "Stay_time": 0.333
      }
    },
    "cost_time": 2.833,
    "Title": "上野之旅",
    "Description": "第四天的行程將帶您遊覽上野區。早上10點，您可以前往上野站，這是一個重要的交通樞紐，連接北關東和東京都內各線電車。在上野站西口，您可以前往上野恩賜公園，這是日本第一座被指定為公園的地方。\n\n接著，上午11點半，您可以在上野恩賜公園漫步，欣賞這個具有百年歷史的公園。\n\n最後，在中午12點半，您可以前往小網神社，這是一個具有神秘感的神社，被認為有「增運除厄」的神力。"
  },
  "DAY 5": {
    "Attractions": {
      "井之頭恩賜公園": {
        "Start_time": "10:00",
        "End_time": "11:00",
        "Stay_time": 1.0
      },
      "sunshinecity": {
        "Start_time": "11:30",
        "End_time": "15:30",
        "Stay_time": 4.0
      }
    },
    "cost_time": 5.5,
    "Title": "井之頭恩賜公園與sunshinecity",
    "Description": "第五天的行程將帶您遊覽井之頭恩賜公園和sunshinecity。早上10點，您可以前往井之頭恩賜公園，這是日本第一座皇室賜贈的公園，擁有百年歷史。在這裡，您可以欣賞到美麗的自然景色。\n\n接著，上午11點半，您可以前往sunshinecity，這是一個位於池袋的複合式商業設施，包含購物中心、旅館、辦公室、水族館、主題樂園等各種設施。在這裡，您可以盡情享受購物和娛樂的樂趣。"
  }
}

    return result_dict


def get_all_travel(travel_days, travel_compactness, city, attraction_preferences, season):
    result_dict = get_data(travel_days, travel_compactness,
                           city, attraction_preferences, season)
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
            <h3 style="font-weight: bold;">{day}</h3>
            <h3>{route1}</h3>
            <h3><a href={url} style="color: #0072E3;">路線圖</a></h3>
            </body>'''
        result.append(t)
    print(result)
    all_travel = ''.join(result)

    return all_travel


def get_map(travel_days, travel_compactness, city, attraction_preferences, current_day, season):
    result_dict = get_data(travel_days, travel_compactness,
                           city, attraction_preferences, season)
    result = list()
    for day, info in result_dict.items():
        attractions = info['Attractions']
        a_list = list()
        for attraction, details in attractions.items():
            a_list.append(attraction)
        if len(a_list) > 0:
            begin = 'origin=' + a_list[0]
            del a_list[0]
        else:
            begin = ''
        if len(a_list) > 0:
            final = '&destination=' + a_list[-1]
            del a_list[-1]
        else:
            final = '&destination='+'日本機場'
        if len(a_list) > 0:
            medium = '&waypoints='+'|'.join(a_list)
        else:
            medium = ''
        map_result = f'''
        <iframe width="600" height="450" style="border:0" loading="lazy" allowfullscreen src="https://www.google.com/maps/embed/v1/directions?{begin}{medium}{final}&key=AIzaSyCZwayq0JV3PCkeuk20XFbKCuX_o8snE6o"></iframe>
        '''
        result.append(map_result)

    if int(current_day) <= int(travel_days):
        map_info = result[int(current_day)-1]
    else:
        map_info = '<h3 style="font-weight: bold;">無資料</h3>'

    return map_info


def get_result_df(travel_compactness, city, attraction_preferences, season):
    result = list()
    result_dict = {}
    result_dict['旅遊城市'] = city
    result_dict['旅遊季節'] = season
    if attraction_preferences != []:
        result_dict['行程主題'] = '+'.join(attraction_preferences)
    else:
        result_dict['行程主題'] = '無指定'
    # for i in range(int(travel_compactness)):

    result_dict['行程緊湊度'] = int(travel_compactness)*'🍜'
    result.append(result_dict)
    df = pd.DataFrame(result)
    return df


def get_route_df(travel_days, travel_compactness, city, attraction_preferences, current_day, season):

    result_dict = get_data(travel_days, travel_compactness,
                           city, attraction_preferences, season)
    all_result = list()
    for day, info in result_dict.items():
        result = list()
        attractions = info['Attractions']
        for attraction, details in attractions.items():
            day_dict = {}
            day_dict['景點名稱'] = attraction
            stay_time = details['Start_time'] + '~' + details['End_time'] + \
                ' (' + str(round(details['Stay_time'], 1)
                           ).replace('.0', '') + '小時)'
            day_dict['預計停留時間'] = stay_time
            result.append(day_dict)
        all_result.append(result)
    if int(current_day) <= int(travel_days):
        df = pd.DataFrame(all_result[int(current_day)-1])
    else:
        df = pd.DataFrame(columns=['景點名稱', '預計停留時間'])
#   df = pd.DataFrame(all_result[0])

    return df

def get_day_description(travel_days, travel_compactness, city, attraction_preferences, current_day, season):
    result_dict = get_data(travel_days, travel_compactness,
                           city, attraction_preferences, season)
    result = list()
    for day, info in result_dict.items():
        attractions = info['Attractions']
        description = info['Description']
        title = info['Title']

        a_list = list()
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


def get_day_travel(travel_days, travel_compactness, city, attraction_preferences, current_day, season):
    result_dict = get_data(travel_days, travel_compactness,
                           city, attraction_preferences, season)
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
          <h3 style="text-align: center;">{route1}</h3>
          <h3 style="text-align: center;"><a href={url} style="color: #0072E3;">路線圖</a></h3>
          <h3 style="text-align: center;">總花費時間: {cost_time} 小時</h3>
          </body>'''
        result.append(t)
    if int(current_day) <= int(travel_days):
        current_travel = result[int(current_day)-1]
    else:
        current_travel = '<h3 style="font-weight: bold;">無資料</h3>'

    return current_travel

title = "日本旅遊規劃"
with gr.Blocks(theme='finlaymacklon/smooth_slate',title=title) as demo:

    with gr.Row():
        gr.HTML(f"<div style=\"text-align: center;\">\n<h1>{title}</h1>\n</div>")

    with gr.Row():
        with gr.Column():
            travel_days = gr.Dropdown(["1", "2", "3", "4", "5", "6", "7"], value='5', label="天數", info="請選擇總天數")
            travel_compactness = gr.Dropdown(["1", "2", "3", "4", "5"], value='3', label="行程緊湊度", info="請選擇一天想安排多少個景點")
            season = gr.Radio(['春天','夏天','秋天','冬天'], value='夏天', label="旅行季節", info="請選擇旅行季節")
        with gr.Column():
            city = gr.Dropdown(["東京都"], value='東京都', label="城市", info="請選擇想去的城市")
            attraction_preferences = gr.CheckboxGroup(["購物", "親子", "藝文", "自然生態", "歷史古蹟", "戶外活動", "宗教", "動漫、二次元", "溫泉", "水上活動", "主題樂園"],
                                                      label="行程主題", info="請選擇想要的主題類型")
    with gr.Row():
        result_but = gr.Button("結果!!!!")
    with gr.Tabs():
        gr.HTML(f"<div style=\"text-align: center;\">\n<h2>🎐 行程總覽</h2>\n<h2></h2></div>")
        with gr.Row():
            with gr.Column():
                all_travel = gr.HTML()
            with gr.Column():
                current_day = gr.Dropdown(
                    ["1", "2", "3", "4", "5", "6", "7"], value='1', label="詳細行程", info="選擇第幾天行程")
                day_but = gr.Button("查看結果")
                map_output = gr.HTML()
                result_df_output = gr.Dataframe(interactive=True, wrap=True)
    with gr.Tabs():
        gr.HTML(f"<div style=\"text-align: center;\">\n<h2>🎐 詳細行程內容</h2>\n<h2></h2></div>")
        day_travel = gr.HTML()
        with gr.Row():
            with gr.Column():
                # day_travel = gr.HTML()
                day_description = gr.HTML()
            with gr.Column():
                gr.HTML('<h3 style="text-align: center; font-weight: bold;">行程規劃</h3>')
                df_output = gr.Dataframe(interactive=True, wrap=True)

        day_but.click(get_map, inputs=[travel_days, travel_compactness,city, attraction_preferences, current_day, season], outputs=map_output)
        day_but.click(get_route_df, inputs=[travel_days, travel_compactness, city, attraction_preferences, current_day, season], outputs=df_output)
        day_but.click(get_day_travel, inputs=[travel_days, travel_compactness, city, attraction_preferences, current_day, season], outputs=day_travel)
        day_but.click(get_day_description, inputs=[travel_days, travel_compactness, city, attraction_preferences, current_day, season], outputs=day_description)
        result_but.click(get_all_travel, inputs=[travel_days, travel_compactness, city, attraction_preferences, season], outputs=all_travel)
        result_but.click(get_result_df, inputs=[travel_compactness, city, attraction_preferences, season], outputs=result_df_output)


demo.launch(share=True)
