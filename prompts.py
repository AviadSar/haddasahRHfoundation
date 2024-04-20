social_assessment_fewshot_addendum = """

###

Social assessment {0}:
{1}

@@@

Answer {0}:
{2}"""


social_assessment_prompt_suffix = """

###

Social assessment {0}:
{1}

@@@

Answer {0}:
"""

attribute_prompts = {
    'sex': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out the sex of the patient, out of these 3 options: "male", "female", "unknown".
For each social assessment, answer with only "male", "female" or "unknown". Write nothing else.""",

    'age': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out the age of the patient.
For each social assessment, respond only with the age of the patient (an integer). Write nothing else.
If the age of the patient is unknown, respond with "unknown". Write nothing else.""",

    'immigrant': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out if the patient is an immigrant to Israel (as opposed to born in Israel).
For each social assessment, answer the question "is the patient an immigrant".
Answer only with "yes", "no" or "unknown". Write nothing else.""",

    'year_of_immigration': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out the year the patient is immigrated to Israel.
For each social assessment, respond only with the age of the year the patient is immigrated to Israel (an integer). Write nothing else.
If the year the patient is immigrated to Israel is unknown, or if there is no indication the patient immigrate, respond with "unknown". Write nothing else.""",

    'marital_status': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out the marital status of the patient.
The options for marital status are: "married", "single", "divorced", "widowed", "not married", "unknown".
The option "not married" is for patients who are not married, but it's not clear if they are single, divorced, or widowed.
For each social assessment, respond with only "married", "single", "divorced", "widowed", "not married" or "unknown". Write nothing else.""",

    'children': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out the number of children the patient has.
For each social assessment, respond only with the number of children the patient has (an integer). Write nothing else.
If the number of children the patient has is unknown, respond with "unknown". Write nothing else.""",

    'closest_relative': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out if the patient has any relatives living close to them.
The options for how close the closest relative is are: "at home", "close", "far".
"close" relatives are those who live a short driving distance from the patient, for example in the same city as the patient.
"far" relatives are those who live further than that.
For each social assessment, answer the question "how close is the patient's closest relative".
Answer with only "at home", "close", "far" or "unknown". Write nothing else.""",

    'closest_supporting_relative': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out if the patient has any relatives living close to them that are able to support them.
A supporting relative is a healthy family member who is able to physically and mentally support the patient. 
The options for how close the closest relative is are: "at home", "close", "far".
"close" relatives are those who live a short driving distance from the patient, for example in the same city as the patient.
"far" relatives are those who live further than that.
For each social assessment, answer the question "how close is the patient's closest supporting relative".
Answer with only "at home", "close", "far" or "unknown". Write nothing else.""",

    'help_at_home_hours': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out how many hours of professional help the receive each week.
When our social worker writes that a patient gets a number "weekly hours", they refer to hours of professional help.
If a patient lives with nurse, sometimes referred to as a "foreign worker", an "Aoz" or a "home attorney", they are considered to get the maximal number of weekly hours, which is 100. 
For each social assessment, respond with only the total amount of hours of professional help they receive each week. Write nothing else.
Write only the final number of hours.
If the amount of hours of professional help is unknown, respond with "unknown". Write nothing else.""",

    'seeking_help_at_home': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out if the patient requested more professional help at home (such as more hours of professional care or a dedicated nurse, sometimes referred to as a "foreign worker", an "Aoz" or a "home attorney").
For each social assessment, answer the question "does the patient request more professional help at home".
Answer only with "yes", "no" or "unknown". Write nothing else.""",

    'is_holocaust_survivor': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out if the patient is a holocaust survivor.
For each social assessment, respond with only "yes", "no" or "unknown". Write nothing else.""",

    'is_exhausted': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out if the patient is physically exhausted (sometimes referred to as debilitated).
A physically exhausted patient is a patient who is not fully independent, or one that requieres full nursing care.
For each social assessment, answer the question "is the patient physically exhausted".
For each social assessment, respond with only "yes", "no" or "unknown". Write nothing else.""",

    'needs_extreme_nursing': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out if the patient needs full nursing care.
A patient who needs full nursing care is a patient who is completely dependent on nursing for every aspect of their life.
A patient who needs full nursing care and has full nursing care, still counts as needing it.
For each social assessment, answer the question "does the patient need full nursing care".
For each social assessment, respond with only "yes", "no" or "unknown". Write nothing else.""",

    'has_extreme_nursing': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out if the patient receive full nursing care.
A patient who needs full nursing care is a patient who is completely dependent on nursing for every aspect of their life.
A patient may need full nursing care, but not receive it. 
For each social assessment, answer the question "does the patient receive full nursing care".
For each social assessment, respond with only "yes", "no" or "unknown". Write nothing else.""",

    'is_confused': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out if the patient is mentally confused.
A mentally confused patient is a patient who can no longer think clearly, or a patient of suffers from dementia.
For each social assessment, answer the question "is the patient mentally confused".
For each social assessment, respond with only "yes", "no" or "unknown". Write nothing else.""",

    'is_dementic': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out if the patient suffers from full dementia.
A patient who suffers from full dementia is a patient who can't perform basic function of memory and thought to any extent.
For each social assessment, answer the question "does the patient suffer from full dementia".
For each social assessment, respond with only "yes", "no" or "unknown". Write nothing else.""",

    'residence': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out where does the patient live, out of these 3 options: "home", "nursing home", "unknown".
A patient who permanently lives in an establishment that is not a private home, can be assumed to live in a nursing home. 
For each social assessment, answer with only "home", "nursing home" or "unknown". Write nothing else.""",

    'recommended_residence': """Our social worker wrote social assessments about our patients.
Your task is to read each social assessment and find out what residence does the social worker recommends for the patient, out of these 3 options: "home", "nursing home", "unknown".
A patient may live in a home or a nursing home regardless of the social worker's recommendation.
Your response should be based on the social worker's recommendation. If there is no recommendation, respond with "unknown".
For each social assessment, answer with only "home", "nursing home" or "unknown". Write nothing else.""",
}

attribute_names = [attribute_name for attribute_name in attribute_prompts.keys()]


