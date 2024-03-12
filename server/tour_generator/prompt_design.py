from liontk.enum.azure_openai import AzureGPT
from liontk.openai.nlp.azure_gpt_client import AzureGPTClient
import arrow
import time


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
            
            Your task is to create a travel itinerary based on the information above and your existing knowledge of {AREA} travel,\
            step1: Understand the attractions and reference information provided. \
            step2: Use the knowledge from Step 1 to create an itinerary for {AREA} {DAYS} days. \
            step3: Think about how to arrange the scenic spots more smoothly and reconstruct it. \
            step4: Finally output in json format. \
                
            This task requires the following 5 points: \
            1. Be sure to plan your itinerary based on your knowledge of the attractions and the relative distance calculated based on the time and latitude and longitude of the attraction reference information. \
            2. The order of attractions should be arranged reasonably and smoothly. Relatively close attractions should be placed on the same day as much as possible, and the transportation time between attractions should be taken into consideration. \
            3. Please try your best to evenly distribute attractions in your daily itinerary to avoid duplicate attractions. \
            4. The output must be in Traditional Chinese.
            5. Make sure the output follows the json format below, no other text. {JSON_PARSER}. \
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

            output[key]['cost_time'] = time_diff.total_seconds() / 3600

        return output

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
                response = self.client.chat(
                    model_name=AzureGPT.DSOPENAI2_GPT_4_8K,
                    temperature=0.5,
                    messages=conversation,
                    max_tokens=8192 -
                    self.client.compute_tokens(str(conversation))
                )

                break
            except:
                count += 1
                print('This is {} times failed'.format(count))
                # time.sjapan_travel/prompt_design.pyleep(30)
                
                if count==3:
                    raise

                continue

        output = eval(response.choices[0].message.content[response.choices[0].message.content.find(
            "{"):response.choices[0].message.content.rfind("}")+1])
        
        # print(output)

        final_itinerary = self.caculate_time(output)
        print(final_itinerary)


if __name__ == "__main__":

    reference_data = {
        '平安神宮': {
            'resident_time': '1 hour',
            'Business_hours': '06:00-17:00',
            'Latitude and longitude': (35.01632498568756, 135.78240484232853)
        },
        '知恩院': {
            'resident_time': '1 hour',
            'Business_hours': '09:00–16:00',
            'Latitude and longitude': (35.005615590922915, 135.78237767267572),
        },
        '嵐山竹林步道': {
            'resident_time': '30 minutes',
            'Business_hours': '24 hours',
            'Latitude and longitude': (35.01696797716031, 135.67133345664692),
        },
        '金閣寺': {
            'resident_time': '1 hour and 30 minutes',
            'Business_hours': '09:00–17:00',
            'Latitude and longitude': (35.03949806410819, 135.72922301701675),
        },
        '伏見稻荷大社': {
            'resident_time': '3 hours',
            'Business_hours': '24 hours',
            'Latitude and longitude': (34.96791427293547, 135.7792090532588),
        },
        '清水寺': {
            'resident_time': '5 hours',
            'Business_hours': '06:00–18:00',
            'Latitude and longitude': (34.9948595332497, 135.78468245344382),
        },
        '嵐山小火車': {
            'resident_time': '2 hours',
            'Business_hours': '08:00-18:00',
            'Latitude and longitude': (35.01752340089544, 135.67036753031155),
        },
        '二條城': {
            'resident_time': '1 hour',
            'Business_hours': '08:45–17:00',
            'Latitude and longitude': (35.01582880477425, 135.74808384506673),
        }
    }
    area = "京都"
    days = "3"
    season = "秋天"

    itinerary_generation = Japan_travel_itinerary_generation(
        reference_data, area, days, season)
    itinerary_generation.main()
