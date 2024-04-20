import os
import pandas as pd
from answer_resolver import resolve_answer


def test_resolve_age():
    age_1 = resolve_answer('age', 'The patient is 45 years old.')
    age_2 = resolve_answer('age', 'The patient is tall.')

    assert age_1 == '45'
    assert age_2 == 'unknown'

# test_resolve_age()