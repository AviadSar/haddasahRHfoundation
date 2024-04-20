import os

import numpy as np
import pandas as pd

from evaluator import get_attribute_winners
from prompts import attribute_prompts, social_assessment_prompt_suffix, attribute_names, \
    social_assessment_fewshot_addendum
from dotenv import load_dotenv
from data_loader import DataLoader
from answer_resolver import resolve_answer, autofill_answer, resolve_label, english_baseline, hebrew_baseline
from typing import List, Dict, Tuple, Any
from openai import OpenAI
import tiktoken
import json


def load_anonymized_data(data_dir, data_file) -> Tuple[str, List[Dict[str, Any]]]:
    if '_anonymized' not in data_file:
        DataLoader.anonymize_data_file(os.path.join(data_dir, data_file))
        data_file = data_file.replace('.xlsx', '_anonymized.xlsx')
    assert '_anonymized' in data_file

    data_json_list = DataLoader.load_data_from_file(os.path.join(data_dir, data_file))

    return data_file, data_json_list


def prepare_zero_shot_prompt(attribute_name: str, data_json_list: List[Dict[str, Any]]) -> Tuple[str, int]:
    prompt = attribute_prompts[attribute_name] + social_assessment_prompt_suffix
    return prompt, 1


def prepare_one_shot_prompt(attribute_name: str, data_json_list: List[Dict[str, Any]]) -> Tuple[str, int]:
    prompt = attribute_prompts[attribute_name]

    assessment = data_json_list[0]['anonymized_social_assessment']
    label = data_json_list[0][attribute_name]
    openai_label = resolve_label(attribute_name, label)
    prompt += social_assessment_fewshot_addendum.format(1, assessment, openai_label)

    prompt += social_assessment_prompt_suffix
    return prompt, 2


def prepare_few_shot_prompt(attribute_name: str, data_json_list: List[Dict[str, Any]]) -> Tuple[str, int]:
    prompt = attribute_prompts[attribute_name]

    for i in range(5):
        assessment = data_json_list[i]['anonymized_social_assessment']
        label = data_json_list[i][attribute_name]
        openai_label = resolve_label(attribute_name, label)
        prompt += social_assessment_fewshot_addendum.format(i + 1, assessment, openai_label)

    prompt += social_assessment_prompt_suffix
    return prompt, 6


def get_answer_from_model(client, model_name: str, prompt: str):
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
        max_tokens=5,
    )
    answer = completion.choices[0].message.content
    return answer


def tag_with_specified_model():
    client = OpenAI()
    data_dir = r"C:\Users\aavia\OneDrive\Documents\study\tau\HaddassahRH\HadadssahRH-20230816T160303Z-001\HadadssahRH\social_assesments\HaddassahRH_dataset"
    data_file = r"social_assesments_300_annotations_clean_en_filled_anonymized.xlsx"
    autofill_function = autofill_answer
    model_name = ""
    filename_addition = 'ai_gpt4'
    # tokenizer = tiktoken.encoding_for_model('gpt-4')
    # token_count = 0

    data_file, data_json_list = load_anonymized_data(data_dir, data_file)

    # the evaluation set indices are 5, 300
    set_names_and_init_functions = {
        'zero_shot': prepare_zero_shot_prompt,
        # 'one_shot': prepare_one_shot_prompt,
        # 'few_shot': prepare_few_shot_prompt,
    }

    data_json_list = data_json_list
    for set_name, init_function in set_names_and_init_functions.items():
        for attribute_name in attribute_names:
            attribute_prompt, next_format_idx = init_function(attribute_name, data_json_list)
            for data_entry_idx, data_entry in enumerate(data_json_list[5:5]):
                prompt = attribute_prompt.format(next_format_idx, data_entry['anonymized_social_assessment'], )
                # autofilled_answer = autofill_function(attribute_name,
                #                                       data_entry['social_assessment'],
                #                                       data_entry['social_assessment_hebrew'],)
                autofilled_answer = None
                if autofilled_answer is not None:
                    data_entry[attribute_name + '_ai'] = autofilled_answer
                else:
                    # tokens = len(tokenizer.encode(prompt)) + 3
                    # token_count += tokens
                    try:
                        answer = get_answer_from_model(model_name, prompt)
                        data_entry[attribute_name + '_ai'] = resolve_answer(attribute_name, answer)
                        print(f"Got response for attribute {attribute_name} for data entry {data_entry_idx}")
                    except Exception as e:
                        print(e)
                        data_entry[attribute_name + '_ai'] = 'openai_call_failed'
            data_df = pd.DataFrame(data_json_list)
            data_df.to_excel(
                os.path.join(data_dir, data_file.replace('.xlsx', f'_{filename_addition}_{set_name}_2.xlsx')))
    # print(token_count)


def tag_from_pet_data(
        model_to_use,
        attribute_name,
        data_json_list,
        data_dir,
        data_file,
        filename_addition,
        data_range,
):
    base_pet_dir = r"C:\Users\aavia\PycharmProjects\pet\outputs"
    config_file = os.path.join(base_pet_dir, r"{}\{}\final\p0-i0\wrapper_config.json".format(model_to_use, attribute_name))
    if model_to_use == 'pet':
        predictions_file = os.path.join(base_pet_dir, r"pet\{}\unlabeled_logits.txt".format(attribute_name))
    elif model_to_use == 'ipet':
        predictions_file = os.path.join(base_pet_dir, r"ipet\{}\g2\unlabeled_logits.txt".format(attribute_name))
    else:
        raise ValueError(f"No such baseline model: {model_to_use}")
    with open(config_file, 'r') as config_file_p:
        labels = json.load(config_file_p)['label_list']
    with open(predictions_file, 'r') as predictions_file_p:
        logits = predictions_file_p.readlines()[1:]
        logits = [np.array([float(value) for value in line.split()]) for line in logits]
    for data_entry_idx, data_entry in enumerate(data_json_list[data_range[0]:data_range[1]]):
        entry_logits = logits[data_entry_idx]
        entry_label = labels[int(np.argmax(entry_logits))]
        data_entry[attribute_name + '_ai'] = entry_label
        print(f"Got {model_to_use} label for attribute {attribute_name} for data entry {data_entry_idx}")
    data_df = pd.DataFrame(data_json_list)
    data_df.to_excel(os.path.join(data_dir, data_file.replace('.xlsx', f'_{filename_addition}.xlsx')))
    data_df.to_excel(os.path.join(data_dir, data_file.replace('.xlsx', f'_{filename_addition}_backup.xlsx')))


def tag_with_baseline_model(
        model_to_use,
        attribute_name,
        data_json_list,
        data_dir,
        data_file,
        filename_addition,
        data_range,
):
    if model_to_use == 'hebrew_baseline':
        baseline_model = hebrew_baseline
    elif model_to_use == 'english_baseline':
        baseline_model = english_baseline
    else:
        raise ValueError(f"No such baseline model: {model_to_use}")
    for data_entry_idx, data_entry in enumerate(data_json_list[data_range[0]:data_range[1]]):
        answer = baseline_model(
            attribute_name,
            data_entry['social_assessment'],
            data_entry['social_assessment_hebrew'],
        )
        data_entry[attribute_name + '_ai'] = answer
        print(f"Got baseline label for attribute {attribute_name} for data entry {data_entry_idx}")
    data_df = pd.DataFrame(data_json_list)
    data_df.to_excel(os.path.join(data_dir, data_file.replace('.xlsx', f'_{filename_addition}.xlsx')))
    data_df.to_excel(os.path.join(data_dir, data_file.replace('.xlsx', f'_{filename_addition}_backup.xlsx')))


def tag_with_openai_model(
        client,
        model_name,
        tokenizer,
        prompt_init_function,
        attribute_name,
        data_json_list,
        token_count,
        data_dir,
        data_file,
        filename_addition,
        data_range,
):
    attribute_prompt, next_format_idx = prompt_init_function(attribute_name, data_json_list)
    for data_entry_idx, data_entry in enumerate(data_json_list[data_range[0]:data_range[1]]):
        prompt = attribute_prompt.format(next_format_idx, data_entry['anonymized_social_assessment'], )
        tokens = len(tokenizer.encode(prompt))
        token_count += tokens
        try:
            answer = get_answer_from_model(client, model_name, prompt)
            data_entry[attribute_name + '_ai'] = resolve_answer(attribute_name, answer)
            print(f"Got openai response for attribute {attribute_name} for data entry {data_entry_idx}")
        except Exception as e:
            print(e)
            data_entry[attribute_name + '_ai'] = 'openai_call_failed'
    data_df = pd.DataFrame(data_json_list)
    data_df.to_excel(os.path.join(data_dir, data_file.replace('.xlsx', f'_{filename_addition}.xlsx')))
    data_df.to_excel(os.path.join(data_dir, data_file.replace('.xlsx', f'_{filename_addition}_backup.xlsx')))
    return token_count


def tag_with_winner_models():
    client = OpenAI()
    data_dir = r"C:\Users\aavia\OneDrive\Documents\study\tau\HaddassahRH\HadadssahRH-20230816T160303Z-001\HadadssahRH\social_assesments\HaddassahRH_dataset"
    data_file = r"social_assesments_300_annotations_clean_en_filled_anonymized.xlsx"
    filename_addition = 'winner_models'
    attribute_winners = get_attribute_winners()
    model_name = 'gpt-3.5-turbo'
    tokenizer = tiktoken.encoding_for_model('gpt-3.5-turbo')
    token_count = 0

    data_file, data_json_list = load_anonymized_data(data_dir, data_file)
    data_range = 300, 5000

    # the evaluation set indices are 5, 300
    set_names_and_init_functions = {
        'zero_shot': prepare_zero_shot_prompt,
        'one_shot': prepare_one_shot_prompt,
        'few_shot': prepare_few_shot_prompt,
    }

    data_json_list = data_json_list
    for attribute_name in attribute_names:
        model_to_use = attribute_winners[attribute_name]
        if model_to_use in set_names_and_init_functions:
            prompt_init_function = set_names_and_init_functions[model_to_use]
            token_count = tag_with_openai_model(
                client,
                model_name,
                tokenizer,
                prompt_init_function,
                attribute_name,
                data_json_list,
                token_count,
                data_dir,
                data_file,
                filename_addition,
                data_range,
            )
        elif 'baseline' in model_to_use:
            tag_with_baseline_model(
                model_to_use,
                attribute_name,
                data_json_list,
                data_dir,
                data_file,
                filename_addition,
                data_range,
            )
        elif "pet" in model_to_use:
            tag_from_pet_data(
                model_to_use,
                attribute_name,
                data_json_list,
                data_dir,
                data_file,
                filename_addition,
                data_range,
            )
        else:
            raise ValueError(f"illegal winner model: {model_to_use}")
    print("Token count: ", token_count)


if __name__ == '__main__':
    load_dotenv()
    # tag_with_specified_model()
    tag_with_winner_models()

