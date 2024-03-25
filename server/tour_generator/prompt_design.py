from config import basic
from utils.log_tool import Log
from openai import AzureOpenAI
import tiktoken

import re
import json_repair
import time
import arrow

import os
from dotenv import load_dotenv
load_dotenv()

log = Log(basic.LOG_PATH)
logger = log.setup_logger('logger', 'generate.log')

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
              5. Please be absolutely sure that the output follows the json format below and has no other text output. {JSON_PARSER}. \
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
        self.api_version = '2024-02-15-preview'
        self.model_name = "gpt-4-8k"
        self.client = AzureOpenAI(api_key=os.getenv("Azure_Openai_API_KEY"),
                                  api_version=self.api_version,
                                  azure_endpoint=os.getenv("Azure_Openai_endpoint"))

        # self.client = AzureGPTClient.get_client(env_enum=AzureGPT.DSOPENAI2,
        #                                         api_version='2024-02-15-preview')
        # self.client.set_encoding(encoding_name=AzureGPT.CL100K_BASE)

    def num_tokens_from_string(self, string: str, encoding_name: str) -> int:
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def caculate_time(self, output:dict) -> dict:

        for key, value in output.items():
            time1 = arrow.get(list(value['Attractions'].values())[
                              0]['Start_time'], 'HH:mm')
            time2 = arrow.get(
                list(value['Attractions'].values())[-1]['End_time'], 'HH:mm')

            time_diff = time2 - time1

            output[key]['cost_time'] = round(
                time_diff.total_seconds() / 3600, 3)

        return output

    @staticmethod
    def translate_time(stay_time:str) -> float:
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

        count = 0
        start = time.time()
        logger.info('Start executing the gpt api')
        while count < 5:
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    temperature=0.5,
                    messages=conversation,
                    max_tokens=8192 -
                    self.num_tokens_from_string(string=str(
                        conversation), encoding_name="cl100k_base"),
                    timeout=100
                )

                output = json_repair.loads(
                    response.choices[0].message.content[response.choices[0].message.content.find("{"):])

                final_itinerary = self.caculate_time(output)


                end = time.time()
                logger.info('Execution time: {} seconds'.format(end - start))
                break
            except Exception as e:
                count += 1
                logger.info('This is {} time(s) failed'.format(count))

                if count == 5:
                    logger.error(e)
                    raise
                continue

        logger.info(
            'The itinerary is successfully generated and parsed into json')

        return final_itinerary
