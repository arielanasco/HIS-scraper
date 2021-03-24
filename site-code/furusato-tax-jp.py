from web_driver import WebDriver
import  web_driver_1
import time
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import logging
import  concurrent.futures
from bs4 import BeautifulSoup as bs

import re

import mysql.connector as connect
""" This section declares all the variables used """

LINK = "https://www.furusato-tax.jp/search/"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s](%(levelname)s@%(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)

data_lock = threading.Lock()

class ScraperCategory(WebDriver):
    categoryList = []
    def __init__(self, url):
        self.url = url
        super().__init__(url)

    def categoryParser(self,**kwargs):
        self.driver.get(self.url)
        self.elementTag = kwargs.get("elementTag")
        self.html = bs(self.driver.page_source, 'html.parser')
        self.category = self.html.find(class_=self.elementTag)
        self.category = self.category.find_all("ul")
        for category in self.category:
            self.holder = category.find_all("li")
            for holder in self.holder[3:]:
                self.categoryData = re.sub(r'\([^()]*\)', '', holder.find(class_="categories__name").text.strip())
                self.categoryData = re.sub(r'\W+', '', self.categoryData)
                ScraperCategory.categoryList.append({"URL":"https://www.furusato-tax.jp"+holder.find("a").get("href"),"category":self.categoryData})






#Start of the main program
start = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Scraping has been started...")
site=ScraperCategory(LINK)
site.categoryParser(elementTag = "search-grandson-categories")
data=site.categoryList
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds for fetching {len(data)} categories")

