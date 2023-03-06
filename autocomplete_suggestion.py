import re
import pandas as pd
from rapidfuzz import fuzz as rapidfuzz_fuzz, process as rapidfuzz_process

def generate_autocomplete_suggestion():
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
    def get_suggestion(input_text):
        suggestions = []
        if not input_text:
            return suggestions
        scorer_metric = rapidfuzz_fuzz.token_set_ratio
        pasal_ayat_metric = rapidfuzz_fuzz.ratio
        question_process = rapidfuzz_process.extract(input_text, question_pattern, scorer=scorer_metric, limit=3)
        peraturan_process = rapidfuzz_process.extract(input_text, peraturan_label, scorer=rapidfuzz_fuzz.token_ratio, limit=2)
        peraturan = [p for p, _, _ in peraturan_process]
        if len(peraturan) == 0:
            peraturan.extend(peraturan_df['Peraturan'][0:2])
        for q, _, _ in question_process:
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
                pasal_ayat_process = rapidfuzz_process.extract(input_text, data_used, scorer=pasal_ayat_metric, limit=2)
                pasal_ayat = [a for a, _, _ in pasal_ayat_process]
                for title in peraturan:
                    q = re.sub('legal_title', title, q)
                    for pasal_ayat_num in pasal_ayat:
                        suggestions.append(re.sub(pattern_replaced, pasal_ayat_num, q))
            else:
                for title in peraturan:
                    suggestions.append(re.sub('legal_title', title, q))
        return suggestions
    
    return get_suggestion