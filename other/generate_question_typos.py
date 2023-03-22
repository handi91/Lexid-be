from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pandas as pd
import random

url = '''https://www.rankwatch.com/free-tools/typo-generator'''
driver = webdriver.Chrome()
driver.get(url)

data_test = pd.read_csv('other/SampleQ1-Q5.csv')

noise_res = ['', '1. Skip Letter ', '5. Reverse Letter ', '3. Extra Letter ', '2. Double Letter ',
             '4. Wrong Letter ']
questions = []
question_typo_list = []

# print(len(list(data_test['type1'])))
counter = 1
for question in data_test['Q']:
    print(counter)
    question_words = question[:-1].split(' ')
    words_variation = {}
    for word in question_words: 
        if not word.isnumeric():
            keyword = driver.find_element(By.TAG_NAME, "textarea")
            keyword.send_keys(word)

            driver.find_element(By.ID, "skip_letter").send_keys(Keys.SPACE)
            driver.find_element(By.ID, "double_letter").send_keys(Keys.SPACE)
            driver.find_element(By.ID, "reverse_letter").send_keys(Keys.SPACE)
            driver.find_element(By.ID, "extra_letter").send_keys(Keys.SPACE)
            driver.find_element(By.ID, "wrong_letter").send_keys(Keys.SPACE)
            driver.find_element(By.ID, "res-search").send_keys(Keys.ENTER)

            typo_results = driver.find_element(By.ID, "result").get_attribute("value")
            typo_words = set(typo_results.split('\n'))
            for noise in noise_res:
                if noise in typo_words:
                    typo_words.remove(noise)
            typo_words.add(word)
            words_variation[word] = list(typo_words)
            driver.find_element(By.TAG_NAME, "textarea").clear()
        else:
            words_variation[word] = [word]

    typo_questions = set()
    while len(typo_questions) < 50:
        typo_combination = []
        for w in question_words:
            typo_combination.append(random.choice(words_variation[w]))
        typo_question = " ".join(typo_combination) + '?'
        if typo_question != question:
            typo_questions.add(typo_question)
    questions.append(question)
    question_typo_list.append(list(typo_questions))
    counter += 1


data = pd.DataFrame({
    'type1': list(data_test['type1']),
    'type2': list(data_test['type2']),
    'question': questions,
    'question_typos': question_typo_list
})

data.to_csv('other/question-typo.csv', index=False)

# data = pd.read_csv('other/question-typo.csv')

# data.sort_values(['type1', 'type2'], inplace=True)
# data.to_csv('other/question-typo-sorted.csv', index=False)

# data = pd.read_csv('other/question-typo-sorted.csv')
# questions = data['question']
# tipe = data['type2']
# peraturans = []

# for i in range(len(questions)):
#     q_tipe = str(tipe[i])
#     q_words = questions[i][:-1].split()
#     if q_tipe == "Q1.1":
#         peraturan = q_words[3:]
#     elif q_tipe == "Q1.2" or q_tipe == "Q1.3":
#         peraturan = q_words[1:-1]
#     elif q_tipe == "Q1.4" or q_tipe == "Q4.1":
#         peraturan = q_words[4:]
#     elif q_tipe in ["Q2.1", "Q2.2", "Q3.1", "Q3.2", "Q4.2", "Q5.2", "Q5.3"]:
#         peraturan = q_words[6:]
#     elif q_tipe == "Q2.3" or q_tipe == "Q2.4":
#         peraturan = q_words[5:]
#     elif q_tipe == "Q5.1":
#         if "ayat" in q_words:
#             peraturan = q_words[7:]
#         else:
#             peraturan = q_words[5:]
#     elif q_tipe == "Q5.4" or q_tipe == "Q5.5":
#         peraturan = q_words[1:-2]
#     else:
#         print("error")
#     print(" ".join(peraturan).title())
#     peraturans.append(" ".join(peraturan).title())

# data['peraturan'] = peraturans
# data.to_csv('other/question-typo-sorted-peraturan.csv', index=False)
