# This is the site for  https://tokyu-furusato.jp/
from web_driver import ScraperCategory,ScraperList
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


logging.basicConfig(level=logging.INFO, format='[%(asctime)s](%(levelname)s@%(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)


def main():
   start = time.perf_counter()
   logging.info(f"{threading.current_thread().name}) - Scraping has been started...")
   site3= ScraperCategory("https://tokyu-furusato.jp/goods/result")
   site3.driver.get(site3.url)
   current_url, user_agent = site3.displaySiteInfo()
   logging.info(f"{threading.current_thread().name}) - {current_url} {user_agent}")
   site3.categoryParser(html= site3.driver.page_source, elementTag = "section_localnav")
   data=site3.categoryList
   site3.driver.close()

   print(data)


   
if __name__ == '__main__':
   main()