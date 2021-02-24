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

class URLCollectorClass(ScraperList):
   def __init__(self, url):
      self.url = url
      super().__init__(url)
   def dataParser(self,html,itemUrl = "",localNameFinder = "",titleFinder = "",descriptionFinder = "",priceFinder = "",capacityFinder = "",imageUrlFinder = ""):
      self.html = bs(html, 'html.parser')
      logging.info(f"{threading.current_thread().name}) - Getting data now...")
      try:
         self.localNameFinder = self.html.find(class_=localNameFinder).get_text()
         self.localNameFinder =  re.sub(r'\W+', '', self.localNameFinder)
      except:
         self.localNameFinder = "Error in localNameFinder"
      try:
         self.titleFinder = self.html.find(class_="lg-info").find_next("h1").get_text()
         self.titleFinder = re.sub(r'\W+', '', self.titleFinder)
      except:
         self.titleFinder = "Error in titleFinder"
      try:
         self.descriptionFinder = self.html.find(class_=descriptionFinder).get_text()
         self.descriptionFinder = re.sub(r'\W+', '', self.descriptionFinder)
      except:
         self.descriptionFinder = "Error in descriptionFinder"
      try:
         self.priceFinder = self.html.find(class_=priceFinder).find_next(class_="price").get_text()
         self.priceFinder = re.sub(r'\W+', '', self.priceFinder)
      except:
         self.priceFinder = "Error in priceFinder"
      try:
         self.capacityFinder = self.html.find(class_=capacityFinder).get_text()
         self.capacityFinder = re.sub(r'\W+', '', self.capacityFinder)
      except:
         self.capacityFinder = "Error in capacityFinder"
      try:
        self.imageUrlFinder = self.html.find(class_=imageUrlFinder).find_all("img")
        self.imageList = []
        for _ in self.imageUrlFinder:
           self.imageList.append(_.get("src"))      
      except:
         self.imageUrlFinder = "Error in imageUrlFinder"
      while True:
         if ScraperList.isNotActive: 
            ScraperList.isNotActive = False
            for data in ScraperList.data:
               if itemUrl in data:
                  index_ = ScraperList.data.index(data)
                  ScraperList.data[index_].insert(2,self.localNameFinder)
                  ScraperList.data[index_].insert(3,self.titleFinder)
                  ScraperList.data[index_].insert(4,self.descriptionFinder)
                  ScraperList.data[index_].insert(5,self.priceFinder)
                  ScraperList.data[index_].insert(6,self.capacityFinder)
                  ScraperList.data[index_].insert(7,self.imageList)
                  ScraperList.isNotActive = True
                  break
            break

# data = ['https://furu-po.com/goods_detail.php?id=664459', 'test']
# ScraperList.data = [['https://furu-po.com/goods_detail.php?id=664459', 'test']]
# [['https://stack...','category','localName','title','description',price','capacity','[imageURL]'],
# ['https://stack...','category','localName','title','description',price','capacity','[imageURL]'],
# ['https://stack...','category','localName','title','description',price','capacity','[imageURL]']
#


def URLCollector(data):
   url_category=data[0]
   category=data[1]
   scrapeURL = URLCollectorClass(url_category)
   scrapeURL.driver.get(scrapeURL.url)
   logging.info(f"{threading.current_thread().name}) - Scraping...{category}")
   while True:
      try:
         time.sleep(1)
         itemlist = WebDriverWait(scrapeURL.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "itemlist"))
         )
         scrapeURL.listParser(html =scrapeURL.driver.page_source, elementContainer = "itemlist")
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
         raise Exception (f"{threading.current_thread().name}) - Unable to load the element")
         break
   scrapeURL.driver.close()

def DataCollector(data):
   item_url = data[0]
   scrapeURL = URLCollectorClass(item_url)
   scrapeURL.driver.get(scrapeURL.url)
   logging.info(f"{threading.current_thread().name}) - Fetching...{item_url}")
   try:
      time.sleep(1)
      item_info = WebDriverWait(scrapeURL.driver, 5).until(
         EC.presence_of_element_located((By.CLASS_NAME, "item_info"))
      )
      scrapeURL.dataParser(html = scrapeURL.driver.page_source,
                           itemUrl = item_url, 
                           localNameFinder = "lg-info",
                           titleFinder = "",
                           descriptionFinder = "item-description",
                           priceFinder = "item-information",
                           capacityFinder = "info",
                           imageUrlFinder = "slick-list" )
   except:
      scrapeURL.driver.close()
      raise Exception (f"{threading.current_thread().name}) - Unable to load the element")
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
   # data=[["https://furu-po.com/goods_list/1150","test"]]
   site1.driver.close()

   print(data)


   with concurrent.futures.ThreadPoolExecutor(max_workers=8 , thread_name_prefix='Scraper') as executor:
      executor.map(URLCollector, data)

   final = time.perf_counter()
   logging.info(f"{threading.current_thread().name}) - Took {round((final-start),2)} second(s)")

   with concurrent.futures.ThreadPoolExecutor(thread_name_prefix='Fetch') as executor:
      executor.map(DataCollector, ScraperList.data)

   final = time.perf_counter()
   logging.info(f"{threading.current_thread().name}) - Took {round((final-start),2)} second(s)")

if __name__ == '__main__':
   main()
