from server.tour_generator.prompt_design import Japan_travel_itinerary_generation
from server.tour_generator.description_writer import Description_Writer
from server.poi_labeling.poi_query import QueryPOI

# input
area = "東京都"
days = 5
season = '秋天'
user_input = {
    "poi_each_day": 3,
    "days": days,
    "city": area,
    "labels": [
        "購物",
        "主題樂園",
        "自然生態",
        "歷史古蹟"
    ]
}

# Retrieve Data
query_poi = QueryPOI()
poi_query = query_poi.main(user_input) 
# Generate itinerary
itinerary_generation = Japan_travel_itinerary_generation(ref_data = poi_query[0], area=area, days=days, season=season)
itinerary = itinerary_generation.main()
# Write description
itin_with_des = Description_Writer().write(itinerary=itinerary, poi_query_description=poi_query[1])
print(itin_with_des)