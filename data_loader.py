import openpyxl
import pandas as pd
import json
from typing import List, Dict, Any
from anonymizer import anonymize_text_nl


# anonymized_text, synonym_dict = anonymize_text_nl("David is a friend of John. I live in michigan")


def anonymize_data(data_json_list: List[Dict]):
    for data_json in data_json_list:
        data_json['anonymized_social_assesment'], _ = anonymize_text_nl(data_json['social_assesment'])


class DataLoader:
    def __init__(self):
        pass

    @staticmethod
    def _df_to_json_list(data_df: pd.DataFrame) -> list:
        json_list = []
        for index, row in data_df.iterrows():
            json_obj = json.loads(row.to_json())
            json_list.append(json_obj)

        return json_list

    @staticmethod
    def load_data_from_file(path: str) -> List[Dict[str, Any]]:
        data_df = pd.read_excel(path)

        json_list = DataLoader._df_to_json_list(data_df)

        return json_list

    @staticmethod
    def anonymize_data_file(path: str):
        data_df = pd.read_excel(path)
        data_df['anonymized_social_assessment'] = data_df['social_assessment'].apply(lambda x: anonymize_text_nl(x)[0])
        data_df.to_excel(path.replace('.xlsx', '_anonymized.xlsx'))
