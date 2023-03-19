import pandas as pd
import ast
from mapping import generate_mapping
from alternative_mapping import generate_alternative_mapping

typo_data = pd.read_csv('other/question-typo.csv')
questions = typo_data['question']
questions_typos = typo_data['question_typos']

map = generate_mapping()
alt_map = generate_alternative_mapping()
acc_score = []
failed_text = []

for i in range(len(questions)):
    print(i)
    q = questions[i]
    expected = map(q)
    same_count = 0
    diff_count = 0
    for j in ast.literal_eval(questions_typos[i]):
        if alt_map(j)[0] == expected:
            same_count += 1
        else:
            diff_count += 1
    acc_score.append(same_count*100/(same_count+diff_count))
typo_data['accuracy_score'] = acc_score

typo_data.to_csv('other/question-typo-evaluation.csv', index=False)

# data = pd.read_csv('other/question-typo-evaluation.csv')
print(typo_data['accuracy_score'].mean())
print(typo_data.groupby('type1')['accuracy_score'].mean())
# print(map('Apakah Peraturan Menteri Energi dan Sumber Daya Mineral Republik Indonesia Tahun 2018 Nomor 23 masih berlaku?')[370:])
# print(alt_map('Apa pertimbantan dalam membuagt Peraturan Menteir Keuangan Republio Indonesia Nokmor 184 Tahun 2017?')[0])