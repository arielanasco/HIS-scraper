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


def ItemCollector(url_category):
   scrapeURL = ScraperList(url_category)
   scrapeURL.driver.get(scrapeURL.url)
   logging.info(f"{threading.current_thread().name}_{scrapeURL.driver.title}) - Scraping...")
   while True:
      try:
         time.sleep(3)
         itemlist = WebDriverWait(scrapeURL.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "itemlist"))
         )
         scrapeURL.listParser(html = scrapeURL.driver.page_source, elementContainer = "itemlist")
         try: 
            nextButton = scrapeURL.driver.find_element_by_xpath("//*[@id='form_events']/section/div[2]/div[1]/div/div[2]/div[3]/ul/li[3]/a")
            nextButton.send_keys(Keys.ENTER)
            logging.info(f"{threading.current_thread().name}_{scrapeURL.driver.title}) - PLS WAIT...  ACTIVE THREAD: {int(threading.activeCount())-1}")
         except NoSuchElementException:
            logging.info(f"{threading.current_thread().name}_{scrapeURL.driver.title}) - EXITING... ACTIVE THREAD: {int(threading.activeCount())-1}")
            while True:
               if scrapeURL.isNotActive:            
                  scrapeURL.isNotActive = False
                  logging.info(f"{threading.current_thread().name}_{scrapeURL.driver.title}) - Saving {len(scrapeURL.itemList)} --> {ScraperList.data}")
                  for _ in scrapeURL.itemList:
                     scrapeURL.data.append(_)
                  scrapeURL.isNotActive = True
                  break
            break
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
   site1.driver.close()
   final = time.perf_counter()

   logging.info(f"{threading.current_thread().name}) - Took {round((final-start),2)} second(s) to fetch list of category")
   url = ["https://furu-po.com/goods_list/176","https://furu-po.com/goods_list/1150"]

   with concurrent.futures.ThreadPoolExecutor(thread_name_prefix='Scraper') as executor:
      for data in site1.categoryList:
         executor.submit(ItemCollector, (data[0]))
   final = time.perf_counter()
   logging.info(f"{threading.current_thread().name}) - Took {round((final-start),2)} second(s) to complete scraping category url")


if __name__ == '__main__':
   main()
