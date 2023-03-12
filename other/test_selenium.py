from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

url = '''https://www.rankwatch.com/free-tools/typo-generator'''
driver = webdriver.Chrome()
driver.get(url)

keyword = driver.find_element(By.TAG_NAME, "textarea")
keyword.send_keys("apakah")

driver.find_element(By.ID, "skip_letter").send_keys(Keys.SPACE)
driver.find_element(By.ID, "double_letter").send_keys(Keys.SPACE)
driver.find_element(By.ID, "reverse_letter").send_keys(Keys.SPACE)
driver.find_element(By.ID, "extra_letter").send_keys(Keys.SPACE)
driver.find_element(By.ID, "wrong_letter").send_keys(Keys.SPACE)
driver.find_element(By.ID, "res-search").send_keys(Keys.ENTER)

hasil = driver.find_element(By.ID, "result").get_attribute("value")
hasils = hasil.split('\n')
time.sleep(3)
print(hasils)

