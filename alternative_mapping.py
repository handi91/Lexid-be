import re
import pandas as pd
from rapidfuzz import fuzz as rapidfuzz_fuzz, process as rapidfuzz_process
from execute_query import generate_get_query_result
from mapping import generate_mapping


def generate_alternative_mapping():
    question_template_df = pd.read_csv("question-sparql-template.csv")
    question_pattern = question_template_df["q_pattern"]
    peraturan_df = pd.read_csv("valid-document-title.csv")
    peraturan_label = peraturan_df["Peraturan"]
    pasal_df = pd.read_csv("valid-pasal-label.csv")
    pasal_label = pasal_df['pasal']
    pasal_with_ayat_df = pd.read_csv("valid-pasal-with-ayat-label.csv")
    pasal_with_ayat = pasal_with_ayat_df['pasal_ayat']
    pasal_optional_ayat_df = pd.read_csv("valid-pasal-optional-ayat-label.csv")
    pasal_optional_ayat = pasal_optional_ayat_df['pasal_ayat']
    def set_query(query_index, **kwargs):
        query_template = question_template_df[question_template_df['query_index'] == query_index].reset_index(drop=True)['query_template'][0]
        for key, value in kwargs.items():
            query_template = re.sub(key, value, query_template)
        return query_template
    
    def alternative_mapping(input_text):
        input_words = input_text.split(" ")
        if len(input_words) <= 5: # word count threshold
            return "", ""

        scorer_metric = rapidfuzz_fuzz.token_set_ratio
        question_process = rapidfuzz_process.extract(" ".join(input_words[:4] + input_words[-1:]), question_pattern, scorer=scorer_metric, limit=5)
        print(question_process)
        peraturan_process = rapidfuzz_process.extract(" ".join(input_words[1:]), peraturan_label, scorer=rapidfuzz_fuzz.token_sort_ratio, limit=5)
        peraturan = [p for p, _, _ in peraturan_process]
        candidate_list = {}
        for q, _, _ in question_process:
            print(q)
            query_index = int(question_template_df[question_template_df['q_pattern']==q]['query_index'])
            if query_index == 11 or query_index == 12 or query_index == 13:
                data_used = pasal_label
                pattern_replaced = "pasal_num"
                if query_index == 12:
                    data_used = pasal_with_ayat
                    pattern_replaced = "pasal_num ayat_num"
                elif query_index == 13:
                    data_used = pasal_optional_ayat
                    pattern_replaced = "pasal_num ayat_num"
                pasal_ayat_process = rapidfuzz_process.extract(input_text, data_used, scorer=scorer_metric, limit=5)
                pasal_ayat = [a for a, _, _ in pasal_ayat_process]
                for title in peraturan:
                    question = re.sub('legal_title', title, q)
                    for pasal_ayat_num in pasal_ayat:
                        question_complete = re.sub(pattern_replaced, pasal_ayat_num, question)
                        candidate_list[question_complete] = {
                            'query_index': query_index,
                            'pasal_num': str([a for a in pasal_optional_ayat_df[pasal_optional_ayat_df['pasal_ayat']==pasal_ayat_num]['pasal']][0]),
                            'ayat_num': str([a for a in pasal_optional_ayat_df[pasal_optional_ayat_df['pasal_ayat']==pasal_ayat_num]['ayat']][0]),
                            'legal_title': title
                        }
            else:
                for title in peraturan:
                    question = re.sub('legal_title', title, q)
                    candidate_list[question] = {
                        'query_index': query_index,
                        'legal_title': title
                    }
        try:
            candidate_question_process = rapidfuzz_process.extract(input_text, candidate_list.keys(), scorer=rapidfuzz_fuzz.ratio)[0][0]
            query_index = candidate_list[candidate_question_process].pop('query_index')
            return set_query(query_index, **candidate_list[candidate_question_process]), candidate_question_process
        except:
            return "", ""
    
    return alternative_mapping
