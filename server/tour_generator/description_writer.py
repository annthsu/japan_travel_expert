import os
import time
import ast
from openai import AzureOpenAI
import tiktoken

from typing import Dict, List
from utils.log_tool import Log
from config import basic

from dotenv import load_dotenv
load_dotenv()

log = Log(basic.LOG_PATH)
logger = log.setup_logger('logger', 'desc.log')


class Description_Writer():
    def __init__(self) -> None:
        self.api_version = '2024-02-15-preview'
        self.model_name = "gpt-35-turbo-16k"
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=self.api_version,
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.system_prompt = """As a expert in travel itinerary writer, you need to write a daily itinerary description based on the provided schedule, incorporating detailed descriptions of each attraction. 
        Our goal is to create a narrative that is both informative and captivating,offering not only practical schedule information but also integrating the charm and stories of the attractions,allowing readers to experience the wonders of the journey through text.
        You should write in the following two steps:
        step 1. Consider the features of itinerary, provide an title for each day, the title name should be Aesthetic.
        step 2. Write down the description of the day."""
        self.conversation = [{'role': 'system', 'content': self.system_prompt}]
        self.JSON_FORMAT = """{
            'DAY 1' : {'Title':The day 1 title of itinerary wite Aesthetic,
                        'Description':The day 1 description of itinerary}, 
            'DAY 1' : {'Title':The day 2 title of itinerary wite Aesthetic,
                        'Description':The day 2 description of itinerary}, 
            ...
        }"""
        self.user_prompt_template = """Please write a Traditional Chinese daily itinerary description base on these two files:
        Schedule:{itinerary}
        Attraction descriptions:{description}
        Your response must follow the following points:
        1. Must write in Traditional Chinese.
        2. Must follow the JSON format:{JSON_FORMAT}"""
        self.retry = 0

    def write(self, itinerary: Dict, poi_query_description: Dict) -> Dict:
        start = time.time()
        logger.info("Start writing description...")
        description = self._map_attraction_des(itinerary, poi_query_description)
        # Format user input
        self.user_prompt = self.user_prompt_template.format(itinerary=itinerary,
                                                            description=description,
                                                            JSON_FORMAT=self.JSON_FORMAT)
        # Append into conversation
        self.conversation.append({'role': 'user', 'content': self.user_prompt})
        logger.info("Request GPT...")
        # Get response
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=0.1,
            messages=self.conversation,
            max_tokens=16385 -
            self.num_tokens_from_string(string=str(self.conversation), encoding_name="cl100k_base")
        )
        output = response.choices[0].message.content
        logger.info("Output Get.")
        #
        try:
            output_dict = self._output_formatter(output, itinerary)
            logger.info('Writing Description Done.')
            end = time.time()
            logger.info("執行時間：{} 秒".format(end - start))
            return output_dict
        except:
            if self.retry == 3:
                logger.error("Failed. Retry over 3 Times.")
                return None
            self.retry += 1
            self.write(self.conversation)

    def _map_attraction_des(self, itinerary, poi_query_description):
        logger.info('Start mapping attraction description...')
        description = {}
        for day, itin in itinerary.items():
            description[day] = {}
            for attraction in itin['Attractions'].keys():
                try:
                    description[attraction] = poi_query_description[attraction]
                except Exception as e:
                    logger.error(e)
        return description

    def _output_formatter(self, output, itinerary):
        logger.info("Start formatting...")
        output_dict = ast.literal_eval(output)
        try:
            for day, itin in itinerary.items():
                itin.update(output_dict[day])
        except Exception as e:
            logger.error(e)
        return itinerary

    def num_tokens_from_string(self, string: str, encoding_name: str) -> int:
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens
