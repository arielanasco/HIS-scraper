# This is the site for  https://furusato.ana.co.jp/
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
   site5= ScraperCategory("https://furusato.ana.co.jp/products/list.php")
   site5.driver.get(site5.url)
   current_url, user_agent = site5.displaySiteInfo()
   logging.info(f"{threading.current_thread().name}) - {current_url} {user_agent}")
   site5.categoryParser(html= site5.driver.page_source, elementTag = "link_wrap")
   data=site5.categoryList
   site5.driver.close()

   print(data)


   
if __name__ == '__main__':
   main()
