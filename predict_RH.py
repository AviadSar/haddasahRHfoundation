import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
import lightgbm as lgb


def load_data():
    data_dir = r"C:\Users\aavia\OneDrive\Documents\study\tau\HaddassahRH\HadadssahRH-20230816T160303Z-001\HadadssahRH\social_assesments\HaddassahRH_dataset"
    data_file = r"baseline_tagged_data_for_classifier_training.xlsx"

    data_df = pd.read_excel(os.path.join(data_dir, data_file))
    patient_groups = data_df.groupby('patient_identifier')
    returned_groups = [(group_id, group_members) for group_id, group_members in patient_groups.groups.items() if
                       len(group_members) > 1]
    returned_groups_with_events = [(t[0], {member: data_df.iloc[member]['event_identifier'] for member in t[1]}) for t in returned_groups]
    for t in returned_groups_with_events:
        t[1].pop(max(t[1], key=lambda key: t[1][key]))
    RH_indices_firsts = [e for t in returned_groups_with_events for e in t[1]]

    RH_df = data_df.iloc[RH_indices_firsts]
    RH_df['label'] = 1
    return_indices = data_df.index.isin(RH_indices_firsts)
    non_RH_df = data_df[~return_indices][:len(RH_df)]
    non_RH_df['label'] = 0
    final_df = pd.concat([RH_df, non_RH_df], ignore_index=True)
    return final_df


def replace_unknown_with_average(data_df, column_name):
    data_df[column_name] = pd.to_numeric(data_df[column_name], errors='coerce')
    average = data_df[column_name].mean()
    data_df[column_name].fillna(average, inplace=True)


def prepare_data_for_classifier(data_df, classifier):
    non_feature_columns = ['social_assessment_hebrew', 'social_assessment', 'patient_identifier', 'event_identifier', 'year_of_immigration']
    data_df = data_df.drop(non_feature_columns, axis=1)
    scalar_columns = ['age', 'children', 'help_at_home_hours']

    if classifier in ['xgboost', 'random_forest']:
        for column_name in scalar_columns:
            replace_unknown_with_average(data_df, column_name)
        columns_for_onehot_encoding = None
        df_encoded = pd.get_dummies(data_df, columns=columns_for_onehot_encoding)
    elif classifier == 'lightgbm':
        for col in data_df.select_dtypes(include=['object']).columns:
            data_df[col] = data_df[col].astype('category')
        df_encoded = data_df
    else:
        raise ValueError(f'no such classifier: {classifier}')

    X = df_encoded.drop('label', axis=1)
    y = df_encoded['label']

    return train_test_split(X, y, test_size=0.2, random_state=42)


def fit_and_predict(X_train, X_test, y_train, y_test, classifier):
    if classifier == 'xgboost':
        model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
    elif classifier == 'lightgbm':
        lgb_train = lgb.Dataset(X_train, y_train)
        lgb_params = {
            'objective': 'binary',  # or 'multiclass' for multi-class classification
            'metric': 'binary_logloss',  # or 'multi_logloss' for multi-class
            'num_leaves': 31,
            'learning_rate': 0.05
        }
        lgb_model = lgb.train(lgb_params, lgb_train, num_boost_round=100)
        y_pred_lgb = lgb_model.predict(X_test)
        predictions = (y_pred_lgb >= 0.5).astype(int)
    elif classifier == 'random_forest':
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        predictions = rf_model.predict(X_test)
    else:
        raise ValueError(f'no such classifier: {classifier}')
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, average='binary')
    recall = recall_score(y_test, predictions, average='binary')
    f1 = f1_score(y_test, predictions, average='binary')
    print(f'CLASSIFIER: {classifier}')
    print(f'Accuracy: {accuracy:.2f}')
    print(f'precision: {precision:.2f}')
    print(f'recall: {recall:.2f}')
    print(f'f1: {f1:.2f}')


if __name__ == "__main__":
    data_df = load_data()
    for classifier in ['xgboost', 'lightgbm', 'random_forest']:
        X_train, X_test, y_train, y_test = prepare_data_for_classifier(data_df, classifier)
        fit_and_predict(X_train, X_test, y_train, y_test, classifier)
