import random
import ast
import pandas as pd
from rapidfuzz import fuzz as rapidfuzz_fuzz, process as rapidfuzz_process

def generate_autocomplete_suggestion():
    pasal_optional_ayat_df = pd.read_csv("valid-pasal-optional-ayat-label.csv")
    pasal_optional_ayat = list(pasal_optional_ayat_df['pasal_ayat'])
    # random.shuffle(pasal_optional_ayat)
    question_pattern_df = pd.read_csv("Question-Head-And-Tail.csv", keep_default_na=False)
    question_head = list(question_pattern_df['head'].unique())
    legal_parse_df = pd.read_csv("peraturan-grouping.csv")
    legal_type = legal_parse_df['tipe']
    legal_number_year = legal_parse_df.set_index('tipe')
    pasal_and_ayat_question_head = ['Bagaimana bunyi', 'Bagaimana perubahan bunyi']
    with_tail_question_head = {'Apakah': ['mengalami amandemen?', 'masih berlaku?'], 'Kapan':['ditetapkan?', 'diundangkan?']}
    def get_suggestion(input_text, autocomplete_index, q_head, previous):
        suggestions = []
        if not input_text:
            return suggestions
        scorer_metric = rapidfuzz_fuzz.token_set_ratio
        
        prefix = ''
        data_used = []
        if autocomplete_index == 0:
            data_used = question_head
        elif autocomplete_index == 1:
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
        choice = rapidfuzz_process.extract(input_text, data_used, scorer=rapidfuzz_fuzz.token_ratio, score_cutoff=50, limit=5)
            
        return [q for q, _, _ in choice] if prefix == '' else [q+prefix for q, _, _ in choice]
    
    return get_suggestion

# a = generate_autocomplete_suggestion()
# print(a("a", 0, '', ''))