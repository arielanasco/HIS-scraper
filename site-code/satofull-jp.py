"""

Site : Satoful		
Link : https://www.satofull.jp/

"""


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


def main():
   start = time.perf_counter()
   logging.info(f"{threading.current_thread().name}) - Scraping has been started...")
   site2= ScraperCategory("https://www.satofull.jp/products/list.php?cnt=60&p=1")
   site2.driver.get(site2.url)
   current_url, user_agent = site2.displaySiteInfo()
   logging.info(f"{threading.current_thread().name}) - {current_url} {user_agent}")
   site2.categoryParser(html= site2.driver.page_source, elementTag = "Section")
   data=site2.categoryList
   site2.driver.close()

   print(data)


   
if __name__ == '__main__':
   main()