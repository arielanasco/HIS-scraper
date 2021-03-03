"""

Site : Satoful	
Link : https://furu-po.com/

"""
from web_driver import WebDriver
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
""" This section declares all the variables used """
LINK = "https://furu-po.com/"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s](%(levelname)s@%(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)


class ScraperCategory(WebDriver):
    categoryList = []

    def __init__(self, url):
        self.url = url
        super().__init__(url)

    def categoryParser(self,**kwargs):
        self.elementTag = kwargs.get("elementTag")
        self.html = bs(kwargs.get("html"), 'html.parser')
        self.category = self.html.find(class_=self.elementTag)
        self.liTag = self.category.li
        while True:
            self.categoryData = re.sub(r'\([^()]*\)', '', self.liTag.find("a").get_text())
            self.categoryData = re.sub(r'\W+', '', self.categoryData)
            ScraperCategory.categoryList.append([self.liTag.find("a").get("href"),self.categoryData])
            if self.liTag.find_next_sibling():
                self.liTag = self.liTag.find_next_sibling()
            else:
                break

class DataCollector(WebDriver):

    isNotActive = True
    data = []

    def __init__(self, url):
        self.url = url
        self.itemList = []
        super().__init__(url)

    def listParser(self,html,elementContainer):
        self.elementContainer = elementContainer
        self.html = bs(html, 'html.parser')
        self.container = self.html.find(class_=self.elementContainer)
        self.ChildElement = self.container.find_next()
        while True:
            self.itemList.append(self.ChildElement.find("a").get("href"))
            if self.ChildElement.find_next_sibling():
                self.ChildElement = self.ChildElement.find_next_sibling()
            else:
                break

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
            if DataCollector.isNotActive: 
                DataCollector.isNotActive = False
                for data in DataCollector.data:
                    if itemUrl in data:
                        index_ = DataCollector.data.index(data)
                        DataCollector.data[index_].insert(2,self.localNameFinder)
                        DataCollector.data[index_].insert(3,self.titleFinder)
                        DataCollector.data[index_].insert(4,self.descriptionFinder)
                        DataCollector.data[index_].insert(5,self.priceFinder)
                        DataCollector.data[index_].insert(6,self.capacityFinder)
                        DataCollector.data[index_].insert(7,self.imageList)
                        DataCollector.isNotActive = True
                        break
            break

def DataCollectorFunction(data):
    nxt_btn ="//*[@id='form_events']/section/div[2]/div[1]/div/div[2]/div[3]/ul/li[3]/a"
    element_container = "itemlist"
    url_category=data[0]
    category=data[1]
    scrapeURL = DataCollector(url_category)
    scrapeURL.driver.get(scrapeURL.url)
    logging.info(f"{threading.current_thread().name}) -Scraping...{category}:{url_category}")
    while True:
        try:
            time.sleep(1)
            itemlist = WebDriverWait(scrapeURL.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, element_container)))
            scrapeURL.listParser(html =scrapeURL.driver.page_source, elementContainer = element_container)
            try:
                nextButton = scrapeURL.driver.find_element_by_xpath(nxt_btn)
                nextButton.send_keys(Keys.ENTER)
                logging.info(f"{threading.current_thread().name}) -Active_thread : {int(threading.activeCount())-1} Next_Page of {category}")
            except NoSuchElementException:
                logging.info(f"{threading.current_thread().name}) -Active_thread : {int(threading.activeCount())-1} Exiting {category} ")
                while True:
                    if scrapeURL.isNotActive:            
                        scrapeURL.isNotActive = False
                        for _ in scrapeURL.itemList:
                            scrapeURL.data.append([LINK+_,category])
                        scrapeURL.isNotActive = True
                        logging.info(f"{threading.current_thread().name}) -Adding {len(scrapeURL.itemList)} items | Total item {len(scrapeURL.data)}")
                        break
                break
        except:
            scrapeURL.driver.close()
            raise Exception (f"{threading.current_thread().name}) -Unable to load the element")
            break
    scrapeURL.driver.close()

if __name__ == '__main__':
    start = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Scraping has been started...")
    site=ScraperCategory(LINK)
    site.driver.get(site.url)
    current_url, user_agent = site.displaySiteInfo()
    logging.info(f"{threading.current_thread().name}) -{current_url} {user_agent}")
    site.categoryParser(html= site.driver.page_source, elementTag = "popover")
    datum=site.categoryList
    site.driver.close()
    final = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds for fetching {len(datum)} categories")
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8 , thread_name_prefix='Scraper') as executor:
        futures = [executor.submit(DataCollectorFunction, data) for data in datum]
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                logging.info(f"{threading.current_thread().name}) -{future.result()}")
    final = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  fetch  {len(DataCollector.data)} items URL")
