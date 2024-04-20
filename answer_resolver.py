from prompts import attribute_prompts
from typing import Union
import re


def resolve_answer(attribute_name: str, answer: str
                   ) -> Union[str, None]:
    if attribute_name == 'sex':
        if 'female' in answer.lower():
            return 'f'
        elif 'male' in answer.lower():
            return 'm'
        else:
            return 'unknown'
    if attribute_name == 'age':
        pattern = r'\d+'
        match = re.search(pattern, answer)
        if match:
            return match.group(0)
        else:
            return 'unknown'
    if attribute_name == 'immigrant':
        if "no" in answer.lower():
            return 'no'
        elif 'yes' in answer.lower():
            return 'yes'
        else:
            return 'unknown'
    if attribute_name == 'year_of_immigration':
        pattern = r'\d+'
        match = re.search(pattern, answer)
        if match:
            return match.group(0)
        else:
            return 'unknown'
    if attribute_name == 'marital_status':
        if "not married" in answer.lower():
            return 'not_married'
        elif 'married' in answer.lower():
            return 'married'
        elif 'single' in answer.lower():
            return 'single'
        elif 'divorce' in answer.lower():
            return 'divorced'
        elif 'widow' in answer.lower():
            return 'widowed'
        else:
            return 'unknown'
    if attribute_name == 'children':
        pattern = r'\d+'
        match = re.search(pattern, answer)
        if match:
            return match.group(0)
        else:
            return 'unknown'
    if attribute_name == 'closest_relative' or attribute_name == 'closest_supporting_relative':
        if "at home" in answer.lower():
            return 'at_home'
        elif 'close' in answer.lower():
            return 'close'
        elif 'far' in answer.lower():
            return 'far'
        else:
            return 'unknown'
    if attribute_name == 'help_at_home_hours':
        pattern = r'\d+'
        match = re.search(pattern, answer)
        if match:
            return match.group(0)
        else:
            return '0'
    if attribute_name == 'seeking_help_at_home':
        if 'yes' in answer.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'is_holocaust_survivor':
        if 'yes' in answer.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'is_exhausted':
        if 'yes' in answer.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'needs_extreme_nursing':
        if 'yes' in answer.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'has_extreme_nursing':
        if 'yes' in answer.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'is_confused':
        if 'yes' in answer.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'is_dementic':
        if 'yes' in answer.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'residence':
        if 'nursing home' in answer.lower():
            return 'nursing_home'
        else:
            return 'home'
    if attribute_name == 'recommended_residence':
        if 'nursing home' in answer.lower():
            return 'nursing_home'
        else:
            return 'home'

    if attribute_name in attribute_prompts.keys():
        print("ERROR: illegal attribute name not found in resolve_answer: " + attribute_name)
        return 'unknown'
    return 'unknown'


def autofill_answer(attribute_name: str,  social_assessment: str, social_assessment_hebrew: str) -> Union[str, None]:
    if attribute_name == 'is_holocaust_survivor':
        if 'holocaust' in social_assessment.lower():
            return 'yes'
    if attribute_name == 'is_exhausted':
        if 'תשוש' in social_assessment_hebrew:
            return 'yes'
    if attribute_name == 'is_confused':
        if 'מבולבל' in social_assessment_hebrew:
            return 'yes'
    # looks like it's not safe to assume for these cases
    # if attribute_name == 'needs_extreme_nursing':
    #     if 'סיעוד' in social_assessment_hebrew:
    #         return 'yes'
    # if attribute_name == 'is_dementic':
    #     if 'דמנציה' in social_assessment_hebrew or 'דימנציה' in social_assessment_hebrew:
    #         return 'yes'
    return None


def english_baseline(attribute_name: str,  social_assessment: str, social_assessment_hebrew: str) -> Union[str, None]:
    if attribute_name == 'sex':
        if any(term in social_assessment.lower() for term in [' she ', ' her ']):
            return 'f'
        elif any(term in social_assessment.lower() for term in [' he ', ' him ']):
            return 'm'
        else:
            return 'unknown'
    if attribute_name == 'age':
        pattern = r'\b\d{2,3}\b'
        matches = re.findall(pattern, social_assessment.lower())
        for match in matches:
            try:
                int_match = int(match)
                if int_match > 50:
                    return match
            except Exception as e:
                print(f'ERROR: could not convert match {match} to int')
        return 'unknown'
    if attribute_name == 'immigrant':
        if any(term in social_assessment.lower() for term in ['immigra', 'originally from']):
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'year_of_immigration':
        pattern = r'\b\d{4}\b'
        match = re.search(pattern, social_assessment.lower())
        if match:
            return match.group(0)
        else:
            return 'unknown'
    if attribute_name == 'marital_status':
        if "not married" in social_assessment.lower():
            return 'not_married'
        elif any(term in social_assessment.lower() for term in ['married', 'm+', ' m ']):
            return 'married'
        elif 'single' in social_assessment.lower():
            return 'single'
        elif any(term in social_assessment.lower() for term in ['divorc', 'd+', ' d ']):
            return 'divorced'
        elif any(term in social_assessment.lower() for term in ['widow', 'w+', ' w ']):
            return 'widowed'
        else:
            return 'unknown'
    if attribute_name == 'children':
        pattern = r'\b\d{1}\b'
        match = re.search(pattern, social_assessment.lower())
        if match:
            return match.group(0)
        else:
            return 'unknown'
    if attribute_name == 'closest_relative' or attribute_name == 'closest_supporting_relative':
        return 'unknown'
    if attribute_name == 'help_at_home_hours':
        if any(term in social_assessment.lower() for term in ['foreign worker', 'Aoz', 'home attorney']):
            return '100'
        pattern = r'\b\d{2,3}\b'
        matches = re.findall(pattern, social_assessment.lower())
        for match in matches:
            try:
                int_match = int(match)
                if int_match < 50:
                    return match
            except Exception as e:
                print(f'ERROR: could not convert match {match} to int')
        return '0'
    if attribute_name == 'seeking_help_at_home':
        return 'no'
    if attribute_name == 'is_holocaust_survivor':
        if 'holocaust' in social_assessment.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'is_exhausted':
        if any(term in social_assessment.lower() for term in ['debilitat', 'exhausted']):
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'is_confused':
        if 'confused' in social_assessment.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'needs_extreme_nursing':
        if 'nurs' in social_assessment.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'has_extreme_nursing':
        if 'nurs' in social_assessment.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'is_dementic':
        if 'dement' in social_assessment.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'residence':
        if 'nursing home' in social_assessment.lower():
            return 'nursing_home'
        else:
            return 'home'
    if attribute_name == 'recommended_residence':
        if 'nursing home' in social_assessment.lower():
            return 'nursing_home'
        else:
            return 'home'

    if attribute_name in attribute_prompts.keys():
        print("ERROR: illegal attribute name not found in resolve_answer: " + attribute_name)
        return None
    return None


def hebrew_baseline(attribute_name: str, social_assessment: str, social_assessment_hebrew: str) -> Union[str, None]:
    if attribute_name == 'sex':
        if any(term in social_assessment_hebrew.lower() for term in ['בת']):
            return 'f'
        elif any(term in social_assessment_hebrew.lower() for term in ['בן']):
            return 'm'
        else:
            return 'unknown'
    if attribute_name == 'age':
        pattern = r'\b\d{2,3}\b'
        matches = re.findall(pattern, social_assessment_hebrew.lower())
        for match in matches:
            try:
                int_match = int(match)
                if int_match > 50:
                    return match
            except Exception as e:
                print(f'ERROR: could not convert match {match} to int')
        return 'unknown'
    if attribute_name == 'immigrant':
        if any(term in social_assessment_hebrew.lower() for term in ['במקור ', 'עולה ', 'עלה', 'עלתה']):
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'year_of_immigration':
        pattern = r'\b\d{4}\b'
        match = re.search(pattern, social_assessment_hebrew.lower())
        if match:
            return match.group(0)
        else:
            return 'unknown'
    if attribute_name == 'marital_status':
        if "לא נשו" in social_assessment_hebrew.lower():
            return 'not_married'
        elif any(term in social_assessment_hebrew.lower() for term in ['נשואה', ' נשוי ', 'נ+', ' נ ']):
            return 'married'
        elif 'רווק' in social_assessment_hebrew.lower():
            return 'single'
        elif any(term in social_assessment_hebrew.lower() for term in ['גרוש', 'ג+', ' ג ']):
            return 'divorced'
        elif any(term in social_assessment_hebrew.lower() for term in ['אלמנה', 'אלמן', 'א+', ' א ']):
            return 'widowed'
        else:
            return 'unknown'
    if attribute_name == 'children':
        pattern = r'\b\d{1}\b'
        match = re.search(pattern, social_assessment_hebrew.lower())
        if match:
            return match.group(0)
        else:
            return 'unknown'
    if attribute_name == 'closest_relative' or attribute_name == 'closest_supporting_relative':
        return 'unknown'
    if attribute_name == 'help_at_home_hours':
        if any(term in social_assessment_hebrew.lower() for term in ['עובדת זרה', 'עובד זר', 'עו"ז', 'ע"ז', ' עז ', ' עוז ']):
            return '100'
        pattern = r'\b\d{2,3}\b'
        matches = re.findall(pattern, social_assessment_hebrew.lower())
        for match in matches:
            try:
                int_match = int(match)
                if int_match < 50:
                    return match
            except Exception as e:
                print(f'ERROR: could not convert match {match} to int')
        return '0'
    if attribute_name == 'seeking_help_at_home':
        return 'no'
    if attribute_name == 'is_holocaust_survivor':
        if ' שואה ' in social_assessment_hebrew.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'is_exhausted':
        if any(term in social_assessment_hebrew.lower() for term in ['תשוש']):
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'is_confused':
        if 'מבולבל' in social_assessment_hebrew.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'needs_extreme_nursing':
        if 'סיעוד' in social_assessment_hebrew.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'has_extreme_nursing':
        if 'סיעוד' in social_assessment_hebrew.lower():
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'is_dementic':
        if any(term in social_assessment_hebrew.lower() for term in ['דימנציה', 'דמנציה']):
            return 'yes'
        else:
            return 'no'
    if attribute_name == 'residence':
        if any(term in social_assessment_hebrew.lower() for term in ['בית אבות', 'מעון']):
            return 'nursing_home'
        else:
            return 'home'
    if attribute_name == 'recommended_residence':
        if any(term in social_assessment_hebrew.lower() for term in ['בית אבות', 'מעון']):
            return 'nursing_home'
        else:
            return 'home'

    if attribute_name in attribute_prompts.keys():
        print("ERROR: illegal attribute name not found in resolve_answer: " + attribute_name)
        return None
    return None


def resolve_label(attribute_name: str, label: str) -> Union[str, None]:
    if attribute_name == 'sex':
        if label == 'f':
            return 'female'
        elif label == 'm':
            return 'male'
        else:
            return 'unknown'
    if attribute_name == 'age':
        return label
    if attribute_name == 'immigrant':
        return label
    if attribute_name == 'year_of_immigration':
        return label
    if attribute_name == 'marital_status':
        if label == 'not_married':
            return 'not married'
        else:
            return label
    if attribute_name == 'children':
        return label
    if attribute_name == 'closest_relative' or attribute_name == 'closest_supporting_relative':
        if label == 'at_home':
            return 'at home'
        else:
            return label
    if attribute_name == 'help_at_home_hours':
        return label
    if attribute_name == 'seeking_help_at_home':
        return label
    if attribute_name == 'is_holocaust_survivor':
        return label
    if attribute_name == 'is_exhausted':
        return label
    if attribute_name == 'needs_extreme_nursing':
        return label
    if attribute_name == 'has_extreme_nursing':
        return label
    if attribute_name == 'is_confused':
        return label
    if attribute_name == 'is_dementic':
        return label
    if attribute_name == 'residence':
        if label == 'nursing_home':
            return 'nursing home'
        else:
            return label
    if attribute_name == 'recommended_residence':
        if label == 'nursing_home':
            return 'nursing home'
        else:
            return label

    return 'unknown'

