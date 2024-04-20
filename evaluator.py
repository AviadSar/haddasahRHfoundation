import copy
import os
import json
import pandas as pd

from typing import Dict, Any
from prompts import attribute_names
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


def get_scores(path: str, min_column: int, max_column: int) -> Dict[str, Dict[str, float]]:
    data_df = pd.read_excel(path)
    data_df = data_df[min_column: max_column]
    result_dict = {}
    for attribute_name in attribute_names:
        ai_attribute_name = attribute_name + '_ai'
        if attribute_name in data_df.columns and ai_attribute_name in data_df.columns:
            gold_labels = data_df[attribute_name].tolist()
            predicted_labels = data_df[attribute_name + '_ai'].tolist()
            gold_labels = [str(label) for label in gold_labels]
            predicted_labels = [str(label) for label in predicted_labels]

            accuracy = accuracy_score(gold_labels, predicted_labels)
            # precision = precision_score(gold_labels, predicted_labels, average='macro')
            # recall = recall_score(gold_labels, predicted_labels, average='macro')
            f1_macro = f1_score(gold_labels, predicted_labels, average='macro')

            # result_dict[attribute_name] = {'accuracy': accuracy, 'precision': precision, 'recall': recall, 'f1': f1}
            result_dict[attribute_name] = {'accuracy': accuracy, 'f1-macro': f1_macro}
    result_dict_json_string = json.dumps(result_dict, indent=4)
    return result_dict


def get_scores_for_pet_attribute(result_dict: Dict[str, Any], method: str, attribute_name: str):
    file_path = os.path.join(
        'C:\\Users\\aavia\\PycharmProjects\\pet\\outputs\\', method, attribute_name, 'final\\p0-i0\\results.json'
    )
    with open(file_path, 'r') as fp:
        json_data = json.load(fp)
        accuracy = json_data['test_set_after_training']['acc']
        f1_macro = json_data['test_set_after_training']['f1-macro']
        result_dict[attribute_name] = {'accuracy': accuracy, 'f1-macro': f1_macro}


def get_scores_from_pet(method: str) -> Dict[str, Any]:
    pet_attribute_names = [
        'sex',
        'immigrant',
        'marital_status',
        'closest_relative',
        'closest_supporting_relative',
        'seeking_help_at_home',
        'is_holocaust_survivor',
        'is_exhausted',
        'needs_extreme_nursing',
        'has_extreme_nursing',
        'is_confused',
        'is_dementic',
        'residence',
        'recommended_residence',
    ]
    # extra attributes that are not compatible with pet:
    # [
    #     'age',
    #     'year_of_immigration',
    #     'children',
    #     'help_at_home_hours',
    # ]
    result_dict = {}
    for attribute_name in pet_attribute_names:
        try:
            get_scores_for_pet_attribute(result_dict, method, attribute_name)
        except Exception as e:
            print(e)
    return result_dict


def clear_root():
    rootdir = "C:\\Users\\aavia\\PycharmProjects\\pet\\outputs"
    for folder, subs, files in os.walk(rootdir):
        if 'final' in folder:
            continue
        else:
            for file in files:
                if 'pytorch_model.bin' in file:
                    os.remove(os.path.join(folder, file))


def get_RH_dataset():
    data_dir = r"C:\Users\aavia\OneDrive\Documents\study\tau\HaddassahRH\HadadssahRH-20230816T160303Z-001\HadadssahRH\social_assesments\HaddassahRH_dataset"
    data_file = r"social_assesments_300_annotations_clean_en_filled_anonymized.xlsx"

    data_df = pd.read_excel(os.path.join(data_dir, data_file))
    patient_groups = data_df.groupby('patient_identifier')
    returned_groups = [(group_id, group_members) for group_id, group_members in patient_groups.groups.items() if
                       len(group_members) > 1]


def get_attribute_winners():
    result_dict_pet = get_scores_from_pet('pet')
    result_dict_ipet = get_scores_from_pet('ipet')
    # path = r"C:\Users\aavia\OneDrive\Documents\study\tau\HaddassahRH\HadadssahRH-20230816T160303Z-001\HadadssahRH\social_assesments\HaddassahRH_dataset\social_assesments_300_annotations_clean_en_filled_anonymized_ai_gpt4_zero_shot_p.xlsx"
    # result_dict_ai_gpt4_zero_shot = get_scores(path, 5, 300)
    path = r"C:\Users\aavia\OneDrive\Documents\study\tau\HaddassahRH\HadadssahRH-20230816T160303Z-001\HadadssahRH\social_assesments\HaddassahRH_dataset\social_assesments_300_annotations_clean_en_filled_anonymized_ai_few_shot_p.xlsx"
    result_dict_ai_few_shot = get_scores(path, 5, 300)
    path = r"C:\Users\aavia\OneDrive\Documents\study\tau\HaddassahRH\HadadssahRH-20230816T160303Z-001\HadadssahRH\social_assesments\HaddassahRH_dataset\social_assesments_300_annotations_clean_en_filled_anonymized_ai_one_shot_p.xlsx"
    result_dict_ai_one_shot = get_scores(path, 5, 300)
    path = r"C:\Users\aavia\OneDrive\Documents\study\tau\HaddassahRH\HadadssahRH-20230816T160303Z-001\HadadssahRH\social_assesments\HaddassahRH_dataset\social_assesments_300_annotations_clean_en_filled_anonymized_ai_zero_shot_p.xlsx"
    result_dict_ai_zero_shot = get_scores(path, 5, 300)
    path = r"C:\Users\aavia\OneDrive\Documents\study\tau\HaddassahRH\HadadssahRH-20230816T160303Z-001\HadadssahRH\social_assesments\HaddassahRH_dataset\social_assesments_300_annotations_clean_en_filled_anonymized_hebrew_baseline_p.xlsx"
    result_dict_hebrew = get_scores(path, 5, 300)
    path = r"C:\Users\aavia\OneDrive\Documents\study\tau\HaddassahRH\HadadssahRH-20230816T160303Z-001\HadadssahRH\social_assesments\HaddassahRH_dataset\social_assesments_300_annotations_clean_en_filled_anonymized_english_baseline_p.xlsx"
    result_dict_english = get_scores(path, 5, 300)

    result_dict = copy.deepcopy(result_dict_pet)
    for attribute_key, attribute_val in result_dict_pet.items():
        for metric_key, metric_val in attribute_val.items():
            result_dict[attribute_key][metric_key] = {
                'pet': result_dict_pet[attribute_key][metric_key],
                'ipet': result_dict_ipet[attribute_key][metric_key],
                # 'gpt4': result_dict_ai_gpt4_zero_shot[attribute_key][metric_key],
                'few_shot': result_dict_ai_few_shot[attribute_key][metric_key],
                'one_shot': result_dict_ai_one_shot[attribute_key][metric_key],
                'zero_shot': result_dict_ai_zero_shot[attribute_key][metric_key],
                'hebrew_baseline': result_dict_hebrew[attribute_key][metric_key],
                'english_baseline': result_dict_english[attribute_key][metric_key]
            }
    for attribute_key, attribute_val in result_dict_ai_few_shot.items():
        if attribute_key not in result_dict:
            result_dict[attribute_key] = {}
            for metric_key, metric_val in attribute_val.items():
                result_dict[attribute_key][metric_key] = {
                    # 'gpt4': result_dict_ai_gpt4_zero_shot[attribute_key][metric_key],
                    'few_shot': result_dict_ai_few_shot[attribute_key][metric_key],
                    'one_shot': result_dict_ai_one_shot[attribute_key][metric_key],
                    'zero_shot': result_dict_ai_zero_shot[attribute_key][metric_key],
                    'hebrew_baseline': result_dict_hebrew[attribute_key][metric_key],
                    'english_baseline': result_dict_english[attribute_key][metric_key]
                }
    attribute_winners = {}
    for attribute_key, attribute_val in result_dict.items():
        scores = [(contestant, contesnat_score) for contestant, contesnat_score in attribute_val['f1-macro'].items()]
        scores.sort(key=lambda t: t[1], reverse=True)
        winner = scores[0]
        baseline_winner = None
        for score in scores:
            if 'baseline' in score[0]:
                baseline_winner = score
                break
        print(f'{attribute_key}:\n{winner[0]}: {winner[1]}\n{baseline_winner[0]}: {baseline_winner[1]}\ngap: {winner[1] - baseline_winner[1]}\n')
        attribute_winners[attribute_key] = winner[0]
    return attribute_winners


if __name__ == '__main__':
    # clear_root()
    get_attribute_winners()


# winners (if not mentioned - ai zero shot is winner):
# marital_status - hebrew baseline
# holocaust survivor - english baseline
# need extreme nursing - hebrew baseline
# has extreme nursing - hebrew baseline
# is_dementic - english baseline