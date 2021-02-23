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

logging.basicConfig(level=logging.INFO, format='[%(asctime)s](%(levelname)s@%(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)


def URLCollector(data):
   url_category=data[0]
   category=data[1]
   scrapeURL = ScraperList(url_category)
   scrapeURL.driver.get(scrapeURL.url)
   logging.info(f"{threading.current_thread().name}) - Scraping...{category}")
   while True:
      try:
         time.sleep(1)
         itemlist = WebDriverWait(scrapeURL.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "itemlist"))
         )
         scrapeURL.listParser(html = itemlist, elementContainer = "itemlist")
         try: 
            nextButton = scrapeURL.driver.find_element_by_xpath("//*[@id='form_events']/section/div[2]/div[1]/div/div[2]/div[3]/ul/li[3]/a")
            nextButton.send_keys(Keys.ENTER)
            logging.info(f"{threading.current_thread().name}) - ACTIVE THREAD:{int(threading.activeCount())-1} Next Page of {category}")
         except NoSuchElementException:
            logging.info(f"{threading.current_thread().name}) - ACTIVE THREAD:{int(threading.activeCount())-1} Exiting {category} ")
            while True:
               if scrapeURL.isNotActive:            
                  scrapeURL.isNotActive = False
                  for _ in scrapeURL.itemList:
                     scrapeURL.data.append([_,category])
                  scrapeURL.isNotActive = True
                  logging.info(f"{threading.current_thread().name}) - Saving collected{len(scrapeURL.itemList)} --> Total Collected URL{len(scrapeURL.data)}")
                  break
            break
      except:
         scrapeURL.driver.close()
         raise Exception (f"{threading.current_thread().name}) - Unable to locate the element")
   scrapeURL.driver.close()

def DataCollector():
   scrapeURL = ScraperList()
   scrapeURL.driver.get(scrapeURL.url)
   try:
      time.sleep(1)
      item_info = WebDriverWait(scrapeURL.driver, 5).until(
         EC.presence_of_element_located((By.CLASS_NAME, "item_info"))
      )
      scrapeURL.dataParser(html =scrapeURL.driver.page_source, elementContainer = "item_info")
   except:
      scrapeURL.driver.close()
      raise Exception (f"{threading.current_thread().name}) - Unable to locate the element")
   scrapeURL.driver.close()

def main():
   start = time.perf_counter()
   logging.info(f"{threading.current_thread().name}) - Scraping has been started...")
   site1= ScraperCategory("https://furu-po.com/")
   site1.driver.get(site1.url)
   current_url, user_agent = site1.displaySiteInfo()
   logging.info(f"{threading.current_thread().name}) - {current_url} {user_agent}")
   site1.categoryParser(html= site1.driver.page_source, elementTag = "popover")
   data=site1.categoryList
   site1.driver.close()

   with concurrent.futures.ThreadPoolExecutor(max_workers=8 , thread_name_prefix='Scraper') as executor:
      executor.map(URLCollector, data)

   final = time.perf_counter()
   logging.info(f"{threading.current_thread().name}) - Took {round((final-start),2)} second(s)")


if __name__ == '__main__':
   main()
