import ast
import pandas as pd
from rapidfuzz import fuzz as rapidfuzz_fuzz, process as rapidfuzz_process

def generate_autocomplete_suggestion():
    pasal_optional_ayat_df = pd.read_csv("valid-pasal-optional-ayat-label.csv")
    pasal_optional_ayat = list(pasal_optional_ayat_df['pasal_ayat'])
    question_head_df = pd.read_csv("Question-Head.csv", keep_default_na=False)
    question_head = list(question_head_df['head'])
    semantic_type =  question_head_df.set_index('head')
    legal_parse_df = pd.read_csv("peraturan-grouping.csv")
    legal_type = legal_parse_df['tipe']
    legal_number_year = legal_parse_df.set_index('tipe')
    pasal_and_ayat_question_head = ['Bagaimana bunyi', 'Bagaimana perubahan bunyi']
    with_tail_question_head = {
        'Apakah': ['mengalami amandemen?', 'masih berlaku?'],
        'Kapan':['ditetapkan?', 'diundangkan?']
    }
    def get_suggestion(input_text, autocomplete_index, q_head, previous):
        suggestions = []
        if not input_text and autocomplete_index==0:
            return suggestions
        scorer_metric = rapidfuzz_fuzz.token_ratio
        prefix = ''
        data_used = []
        if autocomplete_index == 0:
            data_used = question_head
        elif autocomplete_index == 1:
            is_semantic_content = semantic_type['is_semantic'][previous]
            if is_semantic_content == 1:
                return suggestions
            if q_head in pasal_and_ayat_question_head:
                data_used = pasal_optional_ayat
                prefix = " dalam"
            else:
                data_used = legal_type
        elif autocomplete_index == 2:
            if q_head in pasal_and_ayat_question_head:
                data_used = legal_type
            else:
                data_used = ast.literal_eval(legal_number_year['nomor_tahun'][previous])
        elif autocomplete_index == 3:
            if q_head in pasal_and_ayat_question_head:
                data_used = ast.literal_eval(legal_number_year['nomor_tahun'][previous])
            elif q_head in with_tail_question_head:
                return with_tail_question_head[q_head]
        choice = rapidfuzz_process.extract(input_text, data_used, scorer=scorer_metric, limit=5)
            
        return [q for q, _, _ in choice] if prefix == '' else [q+prefix for q, _, _ in choice]
    
    return get_suggestion