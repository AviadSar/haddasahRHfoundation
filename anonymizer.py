import copy
import time

# make sure to install spacy and spacy-transformers
import spacy
import enchant
import pandas as pd
import os
import re
import json

pd.options.mode.chained_assignment = None
from collections import Counter
from copy import deepcopy


# befoe first use, uncomment this line to download spacy model
# spacy.cli.download("en_core_web_trf")
ner_model_transformer = spacy.load('en_core_web_trf')
en_dictionary = enchant.Dict("en_US")


def find_urls(string):
    # findall() has been used
    # with valid conditions for urls in string
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]


def find_addresses(parsed_string):
    address_tokens = set()
    address_entities_spans = []

    for ent in parsed_string.ents:
        if ent.label_ == 'LOC' or ent.label_ == 'GPE' or ent.label_ == 'FAC':
            address_entities_spans.append((ent.start, ent.end))
            for i in range(ent.start, ent.end):
                address_tokens.add(i)

    for address_span in address_entities_spans:
        if address_span[0] > 0:
            for ent in parsed_string.ents:
                if address_span[0] - 1 < ent.end + 1 and address_span[0] - 1 >= ent.start and ent.label_ == 'CARDINAL':
                    for i in range(ent.start, ent.end):
                        address_tokens.add(i)

        if address_span[1] < len(parsed_string):
            for ent in parsed_string.ents:
                if address_span[1] >= ent.start - 1 and address_span[1] < ent.end and ent.label_ == 'CARDINAL':
                    for i in range(ent.start, ent.end):
                        address_tokens.add(i)

        iter_address_tokens = deepcopy(address_tokens)
        for i in range(len(parsed_string)):
            l_distances = [i - j for j in iter_address_tokens if i - j > 0]
            r_distances = [j - i for j in iter_address_tokens if j - i > 0]
            if not l_distances or not r_distances:
                continue
            if min(l_distances) + min(r_distances) <= 3:
                address_tokens.add(i)

    sorted_address_tokens = sorted(list(address_tokens))
    address_spans = []
    address_span = []
    for idx in sorted_address_tokens:
        if not address_span or idx - address_span[-1] == 1:
            address_span.append(idx)
        else:
            address_spans.append(address_span)
            address_span = [idx]
    if address_span:
        address_spans.append(address_span)

    addresses = [parsed_string[address_span[0]: address_span[-1] + 1] for address_span in address_spans]

    return address_spans, addresses


def get_synonym(ent_label, type_anonymization_dict, text):
    for synonym in type_anonymization_dict[ent_label]:
        if synonym[1] == 'not_used' and synonym[0] not in text and synonym[0].lower() not in text:
            synonym[1] = 'used'
            return synonym[0]
        elif synonym[1] != 'used' and synonym[1] != 'not_used':
            return_value = synonym[0] + str(synonym[1])
            synonym[1] += 1
            return return_value
    return 0


def anonymize_text_nl(text, ner_model_transformer=ner_model_transformer):
    unseperated_text = text
    for seperator in '_-':
        unseperated_text = unseperated_text.replace(seperator, ' ')

    type_anonymization_dict = copy.deepcopy({'ORG': [['Company1', 'not_used'], ['Company2', 'not_used'], ['Company3', 'not_used'], ['Company4', 'not_used'], ['Company', 0]],
                               'PRODUCT': [['Product1', 'not_used'], ['Product2', 'not_used'], ['Product3', 'not_used'], ['Product4', 'not_used'], ['Product', 0]],
                               'PERSON': [['Person1', 'not_used'], ['Person2', 'not_used'], ['Person3', 'not_used'], ['Person4', 'not_used'], ['Person', 0]],
                               'LOC': [['Area1', 'not_used'], ['Area2', 'not_used'], ['Area3', 'not_used'], ['Area4', 'not_used'], ['Area', 0]],
                               'GPE': [['Country1', 'not_used'], ['Country2', 'not_used'], ['Country3', 'not_used'], ['Country4', 'not_used'], ['Country', 0]],
                               'FAC': [['Main st', 'not_used'], ['Broadway', 'not_used'], ['Park Avenue', 'not_used'], ['Columbus Avenue', 'not_used'], ['Street', 0]],
                               'ADDRESS': [['1 Madison Avenue, Springfield', 'not_used'], ['34 Lexington st., South Park', 'not_used'], ['156 Thomson Avenue, Chelsea', 'not_used'], ['87 Woodside st., Oxford', 'not_used'], ['Address', 0]],
                               'URL': [['a.com', 'not_used'], ['b.com', 'not_used'], ['c.com', 'not_used'], ['d.com', 'not_used'], ['URL', 0]],
                               'EMAIL': [['a@b.com', 'not_used'], ['c@d.com', 'not_used'], ['e@f.com', 'not_used'], ['g@h.com', 'not_used'], ['Email', 0]],
                               'PHONE': [['84651965', 'not_used'], ['32168657', 'not_used'], ['47512568', 'not_used'], ['95324684', 'not_used'], ['Phone Number', 0]],
                               })
    entities_synonym_dict = {}

    parsed_text = ner_model_transformer(unseperated_text)
    all_entities = ([(str(ent), ent.label_) for ent in parsed_text.ents if ent.label_ == 'ORG'] +
                    [(str(ent), ent.label_) for ent in parsed_text.ents if ent.label_ == 'PRODUCT'] +
                    [(str(ent), ent.label_) for ent in parsed_text.ents if ent.label_ == 'PERSON'] +
                    [(str(ent), ent.label_) for ent in parsed_text.ents if ent.label_ == 'LOC'] +
                    [(str(ent), ent.label_) for ent in parsed_text.ents if ent.label_ == 'GPE'] +
                    [(str(ent), ent.label_) for ent in parsed_text.ents if ent.label_ == 'FAC'] +
                    [(str(ent), "ADDRESS") for ent in find_addresses(parsed_text)[1]] +
                    [(str(ent), "URL") for ent in find_urls(text)] +
                    [(str(ent), "EMAIL") for ent in re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)] +
                    [(str(ent), "PHONE") for ent in re.findall(r'^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$', text) + re.findall('((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))', text)])

    for ent_str, ent_label in all_entities:
        entities_synonym_dict[ent_str] = get_synonym(ent_label, type_anonymization_dict, text)

    for entity in [item[0] for item in sorted(entities_synonym_dict.items(), key=lambda item: item[1])]:
        text = text.replace(entity, entities_synonym_dict[entity])

    split_text = text.split()
    for word_idx, word in enumerate(split_text):
        # if first letter is capitalized, and the word is not an english word
        if word[0].lower() != word[0] and not en_dictionary.check(''.join(char for char in word if char.isalpha())):
            split_text[word_idx] = '<unk>'
    text = ' '.join(split_text)

    return text, entities_synonym_dict


def deanonymize_text(text, entities_synonym_dict):
    for entity in [item[0] for item in sorted(entities_synonym_dict.items(), key=lambda item: item[1], reverse=True)]:
        text = text.replace(entities_synonym_dict[entity], entity)
    return text
