from selenium import webdriver
from bs4 import BeautifulSoup

chromedriver = "/Users/carolyn/projects/scratch/crawler/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chromedriver)

page = "https://www.fanfiction.net/book/Harry-Potter/"
print "Fetching " + page
    driver.get(page)
