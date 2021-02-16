import selenium
from selenium import webdriver
import random

url = "https://rifme.net/u/оврааапол"
desired_capabilities = webdriver.DesiredCapabilities.PHANTOMJS.copy()
driver = webdriver.Chrome('chromedriver.exe')
driver.get(url)
rifma = driver.find_element_by_xpath("//body/div[1]/section/form/table/tbody/tr/td[@class='labelRadio']")
rifma.click()
print(rifma)
