from liontk.enum.azure_openai import AzureGPT
from liontk.openai.nlp.azure_gpt_client import AzureGPTClient
import arrow
import json
import time
import re
from utils.log_tool import Log
from config import basic
log = Log(basic.LOG_PATH)
logger = log.setup_logger('logger', 'travel_itinerary_generation.log')


class Japan_travel_itinerary_generation:
    def __init__(self, ref_data, area, days, season) -> None:
        self.system_prompt = "You are a Japan travel expert with at least 30 years of experience in Japan. Planning your Japan travel itinerary is a breeze for you."
        self.user_prompt_template = '''Understand Japan {AREA} travel and plan a suitable itinerary,\
            The number of days of travel is {DAYS} and the departure season is {SEASON},\
            Continue to refer to the following json file {DATA} for information about some attractions,\
            Information covers 3 types and their respective reference points:
            1. Resident time: Time spent at attractions. \
            2. Business hours: Approximate business hours of the attraction (may be empty). \
            3. Latitude and longitude: The location of the attraction on the map. \
            These three pieces of information can be used to arrange the order of attractions.\
            
            Your task is to create a travel itinerary based on the above information and your existing knowledge of {AREA} travel,\
              step1: Thoroughly understand the attractions and the reference information provided. \
              step2: After thinking, prioritize the attractions with similar longitude and latitude on the same day of the itinerary, and then sort them according to business hours.
              step3: Use the ideas from steps 1 and 2 to create an itinerary for {AREA} {DAYS} days.
              step4: Think about how to arrange your daily schedule more smoothly, and make final reconstruction. \
              step5: Finally output in json format. \
                
            You need to pay attention to the following 5 points in this task:\
              1. Plan the itinerary based on your own understanding of the scenic spots and the relative distance calculated from the time and latitude and longitude of the scenic spot reference information. \
              2. The sequence of scenic spots is arranged reasonably and smoothly. For nearby attractions, try to arrange them on the same day, and consider the transportation time between attractions. \
              3. Please distribute the scenic spots evenly in the daily itinerary to avoid duplicating scenic spots in the itinerary. \
              4. The output must be in Traditional Chinese.
              5. Make sure the output follows the json format below and has no other text output. {JSON_PARSER}. \
            '''
        self.json_parser = {
            "DAY 1": {
                "Attractions": {
                    "attraction 1": {
                        "Start_time": "Start time",
                        "End_time": "End time",
                        "Stay_time": "Stay time"
                    },
                    "attraction 2": {
                        "Start_time": "Start time",
                        "End_time": "End time",
                        "Stay_time": "Stay time"
                    }
                }
            },
            "DAY 2": {
                "Attractions": {
                    "attraction 3": {
                        "Start_time": "Start time",
                        "End_time": "End time",
                        "Stay_time": "Stay time"
                    },
                    "attraction 4": {
                        "Start_time": "Start time",
                        "End_time": "End time",
                        "Stay_time": "Stay time"
                    }
                }
            }
        }
        self.user_prompt = self.user_prompt_template.format(AREA=area,
                                                            DATA=ref_data,
                                                            DAYS=days,
                                                            SEASON=season,
                                                            JSON_PARSER=self.json_parser)
        self.client = AzureGPTClient.get_client(env_enum=AzureGPT.DSOPENAI2,
                                                api_version='2024-02-15-preview')
        self.client.set_encoding(encoding_name=AzureGPT.CL100K_BASE)

    def caculate_time(self, output):

        for key, value in output.items():
            time1 = arrow.get(list(value['Attractions'].values())[
                              0]['Start_time'], 'HH:mm')
            time2 = arrow.get(
                list(value['Attractions'].values())[-1]['End_time'], 'HH:mm')

            time_diff = time2 - time1

            output[key]['cost_time'] = round(time_diff.total_seconds() / 3600, 3)

        return output

    @staticmethod
    def translate_time(stay_time):
        if ("hour" in stay_time) and ("minute" in stay_time):
            x = re.findall(r'\d+', stay_time)
            return round(int(x[0]) + int(x[1])/60, 3)
        elif ("hour" in stay_time):
            return float(re.findall(r'\d+', stay_time)[0])
        else:
            return round(int(re.findall(r'\d+', stay_time)[0])/60, 3)

    def main(self):

        conversation = [
            {"role": "system",
             "content": self.system_prompt},
            {"role": "user",
             "content": self.user_prompt}
        ]

        # response = self.client.chat(
        #     model_name=AzureGPT.DSOPENAI2_GPT_4_32K,
        #     temperature=0.5,
        #     messages=conversation,
        #     max_tokens=16384 -
        #     self.client.compute_tokens(str(conversation))
        # )

        count = 0
        while count < 3:
            try:
                start = time.time()

                response = self.client.chat(
                    model_name=AzureGPT.DSOPENAI2_GPT_4_8K,
                    temperature=0.5,
                    messages=conversation,
                    max_tokens=8192 -
                    self.client.compute_tokens(str(conversation)),
                    timeout=100
                )

                end = time.time()
                print("執行時間：%f 秒" % (end - start))
                print("-"*100)

                break
            except:
                count += 1
                print('This is {} times failed'.format(count))
                # time.sjapan_travel/prompt_design.pyleep(30)

                if count == 3:
                    raise

                continue

        print(response)

        output = eval(response.choices[0].message.content[response.choices[0].message.content.find(
            "{"):response.choices[0].message.content.rfind("}")+1])

        # print(output)

        final_itinerary = self.caculate_time(output)

        for key in final_itinerary.keys():
            for attr in final_itinerary[key]['Attractions']:
                final_itinerary[key]['Attractions'][attr]['Stay_time'] = self.translate_time(final_itinerary[key]['Attractions'][attr]['Stay_time'])

        with open("test.json", "w", encoding="utf-8") as file:
            json.dump(final_itinerary, file)

        print(final_itinerary)


if __name__ == "__main__":

    # with open('tokyo_test_data2.json',encoding="utf-8") as jsonfile:
    #     json_data = json.load(jsonfile)

    # reference_data={}
    # for key in json_data.keys():
    #     reference_data.update(json_data[key])

    # for key,value in reference_data.items():
    #     del reference_data[key]['Description']

    # reference_data = dict(list(reference_data.items())[:8])

    with open('tokyo_av.json', encoding="utf-8") as jsonfile:
        reference_data = json.load(jsonfile)

    area = "東京"
    days = "5"
    season = "秋天"

    itinerary_generation = Japan_travel_itinerary_generation(
        reference_data, area, days, season)
    itinerary_generation.main()
