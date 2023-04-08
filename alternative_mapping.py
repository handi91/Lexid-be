import re
import pandas as pd
from rapidfuzz import fuzz as rapidfuzz_fuzz, process as rapidfuzz_process

def generate_alternative_mapping():
    question_template_df = pd.read_csv("question-sparql-template.csv")
    question_pattern = question_template_df["q_pattern"]
    semantic_questions_df = pd.read_csv('semantic-question-collection.csv').fillna('')
    semantic_questions = list(semantic_questions_df['Question'])
    semantic_question_reference = semantic_questions_df.set_index('Question')
    peraturan_df = pd.read_csv("valid-document-title.csv")
    peraturan_label = peraturan_df["Peraturan"]
    pasal_df = pd.read_csv("valid-pasal-label.csv")
    pasal_label = pasal_df['pasal']
    pasal_with_ayat_df = pd.read_csv("valid-pasal-with-ayat-label.csv")
    pasal_with_ayat = pasal_with_ayat_df['pasal_ayat']
    pasal_optional_ayat_df = pd.read_csv("valid-pasal-optional-ayat-label.csv").fillna('')
    pasal_optional_ayat = pasal_optional_ayat_df['pasal_ayat']
    pasal_ayat_reference = pasal_optional_ayat_df.set_index('pasal_ayat')

    def set_query(query_index, **kwargs):
        query_template = question_template_df[question_template_df['query_index'] == query_index]\
                                              .reset_index(drop=True)['query_template'][0]
        for key, value in kwargs.items():
            query_template = re.sub(key, value, query_template)
        return query_template
    
    def alternative_mapping(input_text):
        ratio_metric = rapidfuzz_fuzz.ratio
        input_words = input_text.split(" ")
        result_prefix = ""
        if len(input_words) <= 7:
            candidate_question_process = rapidfuzz_process.extract(
                input_text,
                semantic_questions,
                scorer=ratio_metric
            )[0][0]
            legal_ref = semantic_question_reference['legal_ref'][candidate_question_process]
            pasal_ref = semantic_question_reference['pasal_ref'][candidate_question_process]
            ayat_ref = semantic_question_reference['ayat_ref'][candidate_question_process]
            query_param = {
                'legal_title': legal_ref,
                'pasal_num': pasal_ref,
                'ayat_num': ayat_ref
            }
            result_prefix = f"Berdasarkan {pasal_ref} {ayat_ref} {legal_ref}:\n" if ayat_ref \
                            else f"Berdasarkan {pasal_ref} {legal_ref}:\n"
            query_index = 11
            if ayat_ref != '':
                query_index = 12
            return set_query(query_index,
                             **query_param), candidate_question_process, query_index, result_prefix
        
        question_part = " ".join(input_words[:4] + input_words[-1:])
        peraturan_part = " ".join(input_words[2:])
        pasal_ayat_part = " ".join(input_words[2:7])
        question_process = rapidfuzz_process.extract(
            question_part,
            question_pattern,
            scorer=ratio_metric,
            limit=4
        )
        peraturan_process = rapidfuzz_process.extract(
            peraturan_part,
            peraturan_label,
            scorer=ratio_metric,
            limit=5
        )
        peraturan = [p for p, _, _ in peraturan_process]
        candidate_list = {}
        for q, _, _ in question_process:
            query_index = int(question_template_df[question_template_df['q_pattern']==q]['query_index'])
            if query_index == 11 or query_index == 12 or query_index == 13:
                data_used = pasal_label
                pattern_replaced = "pasal_num" if query_index == 11 else "pasal_num ayat_num"
                if query_index == 12:
                    data_used = pasal_with_ayat
                elif query_index == 13:
                    data_used = pasal_optional_ayat
                pasal_ayat_process = rapidfuzz_process.extract(
                    pasal_ayat_part,
                    data_used,
                    scorer=ratio_metric,
                    limit=5
                )
                pasal_ayat = [a for a, _, _ in pasal_ayat_process]
                for title in peraturan:
                    question = re.sub('legal_title', title, q)
                    for pasal_ayat_num in pasal_ayat:
                        question_complete = re.sub(pattern_replaced, pasal_ayat_num, question)
                        candidate_list[question_complete] = {
                            'query_index': query_index,
                            'pasal_num': pasal_ayat_reference['pasal'][pasal_ayat_num],
                            'ayat_num': pasal_ayat_reference['ayat'][pasal_ayat_num],
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
            candidate_question_process = rapidfuzz_process.extract(
                input_text,
                [j for j in candidate_list.keys()] + semantic_questions,
                scorer=ratio_metric,
                score_cutoff=50)[0][0]
            query_index = candidate_list[candidate_question_process].pop('query_index')
            return set_query(query_index,
                            **candidate_list[candidate_question_process]
                            ), candidate_question_process, query_index, result_prefix
        except:
            try:
                legal_ref = semantic_question_reference['legal_ref'][candidate_question_process]
                pasal_ref = semantic_question_reference['pasal_ref'][candidate_question_process]
                ayat_ref = semantic_question_reference['ayat_ref'][candidate_question_process]
                query_param = {
                    'legal_title': legal_ref,
                    'pasal_num': pasal_ref,
                    'ayat_num': ayat_ref
                }
                query_index = 11
                result_prefix = f"Berdasarkan {pasal_ref} {ayat_ref} {legal_ref}:\n" if ayat_ref \
                            else f"Berdasarkan {pasal_ref} {legal_ref}:\n"
                if ayat_ref != '':
                    query_index = 12
                return set_query(query_index,
                                 **query_param), candidate_question_process, query_index, result_prefix
            except:
                return "", "", -1
    
    return alternative_mapping