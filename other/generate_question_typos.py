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
data_test2 = pd.read_csv('other/SampleQ6.csv')

noise_res = [
    '',
    '1. Skip Letter ',
    '5. Reverse Letter ',
    '3. Extra Letter ',
    '2. Double Letter ',
    '4. Wrong Letter '
]

questions = []
question_typo_list = []
sample_questions = list(data_test['Q'])
sample_questions.extend(list(data_test2['Q']))

for question in sample_questions:
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

data = pd.DataFrame({
    'type': list(data_test['type1']),
    'question': questions,
    'question_typos': question_typo_list
})

data.to_csv('other/question-typo-collection.csv', index=False)