from __future__ import print_function

import json
import os
from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from datetime import datetime
from time import time

import pandas as pd
from loguru import logger
from openai import OpenAI
from tqdm import tqdm
from vllm import LLM, SamplingParams

from labeling_prompt import MODEL_PROMPT_TEMPLATES


class LabelingPOI:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def _label_shot_prompt(shots: list):
        prompt = []
        for shot in shots:
            prompt.append(f"{shot['name']}: {shot['summary']}")
        return '\n' + '\n'.join(prompt)

    def set_data(self, poi_file_path, label_file_path):
        self.poi_data = pd.read_csv(poi_file_path)
        logger.info(f'Success Load {len(self.poi_data)} rows poi_data.')
        with open(label_file_path, 'r') as reader:
            self.label_data = json.load(reader)
        logger.info(f'Success Load {len(self.label_data)} labels data.')

    @staticmethod
    def _set_prompt(model, **kwargs):
        prompt_template = MODEL_PROMPT_TEMPLATES.get(model)
        if not prompt_template:
            raise Exception("Missing Model in MODEL_PROMPT_TEMPLATES")
        copy_prompt_template = deepcopy(prompt_template)
        return copy_prompt_template.format(**kwargs)

    def process_poi_and_label(self, model: str):
        logger.info("Start to Process prompt...")
        prompt_args_index = list()
        pre_prompts = list()

        for _, row in enumerate(self.poi_data.to_dict(orient='records')):
            # name, introduction
            prompt_args = dict()
            prompt_args.update(row)
            for label, label_shots in self.label_data.items():
                prompt_args['label'] = label
                prompt_args['few_shots'] = self._label_shot_prompt(label_shots)
                prompt = self._set_prompt(model, **prompt_args)
                pre_prompts.append(prompt)
                prompt_args_index.append(deepcopy(prompt_args))
        return pre_prompts, prompt_args_index

    def process_output(self, outputs, prompt_args_index):
        logger.info("Start to Process outputs...")
        result = dict()
        for n, output in enumerate(outputs):
            prompt_arg = prompt_args_index[n]
            ans = output.outputs[0].text
            labels = result.setdefault(prompt_arg['name'], list())
            if 'yes' in ans.lower():
                labels.append(prompt_arg['label'])
        return result

    def analyst_result(self, result: dict):
        labels_count = list()
        no_label_pois = 0
        for poi, labels in result.items():
            if labels:
                labels_count.extend(labels)
            else:
                no_label_pois += 1

        logger.info(f"No label poi count: {no_label_pois}, {no_label_pois/len(result)*100:.1f}%")
        logger.info(f"Labels Count:\n{Counter(labels_count).most_common()}")

    def breeze_inference(self, **kwargs):
        llm = LLM(model=kwargs['model_path'])
        sampling_params = SamplingParams(
            temperature=kwargs['temperature'],
            top_p=0.9,
            top_k=20,
            repetition_penalty=1.15,
        )

        pre_prompts, prompt_args_index = self.process_poi_and_label(kwargs['model'])

        logger.info("Start to Inference LLM...")
        outputs = llm.generate(pre_prompts, sampling_params)

        result = self.process_output(outputs, prompt_args_index)

        return result
    
    def openai_inference(self, **kwargs):
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        pre_prompts, prompt_args_index = self.process_poi_and_label(kwargs['model'])

        logger.info("Start to Inference LLM...")
        outputs = list()
        for prompt in tqdm(pre_prompts, desc=f"Requesting {kwargs['model']}"):
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=kwargs['model'],
                temperature=kwargs['temperature']
            )
            outputs.append(chat_completion)

        result = self.process_output(outputs, prompt_args_index)

        return result

    def main(self, **kwargs):
        kwargs['model'] = kwargs['model_path'].rsplit('/', 1)[-1]
        self.set_data(kwargs['poi_file_path'], kwargs['labels_file_path'])
        st = time()
        if kwargs['model'] == 'MediaTek-Research_Breeze-7B-Instruct-64k':
            logger.info(f'Start to breeze_inference...')
            result = self.breeze_inference(**kwargs)
            
        elif kwargs['model'] == 'gpt-3.5-turbo':
            logger.info(f'Start to openai inference...')
            result = self.openai_inference(**kwargs)

        self.analyst_result(result)

        today = datetime.now().strftime("%Y%m%d")
        save_file_name = "./data/" + '_'.join([kwargs['model'], today, kwargs['save_file_name']])
        with open(save_file_name, 'w') as writer:
            json.dump(result, writer, indent=4, ensure_ascii=False)
            logger.info(f'Save {len(result)} File to {save_file_name}.')

        logger.info(f'OK. Time: {time()-st:.1f} s')

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-pfp", "--poi-file-path", type=str, default="./data/pois.csv")
    parser.add_argument("-lfp", "--labels-file-path", type=str, default='./data/labels_shot.json')
    parser.add_argument('-m', "--model-path", type=str, default='./models/MediaTek-Research_Breeze-7B-Instruct-64k')
    parser.add_argument('-s', "--save-file-name", type=str, default=f'poi_labeling.json')
    parser.add_argument("-temp", "--temperature", type=float, default=0.7)

    args = parser.parse_args()
    labeling_poi = LabelingPOI()
    labeling_poi.main(**vars(args))
