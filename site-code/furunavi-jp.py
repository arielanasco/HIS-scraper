"""

Site : Furupo (JTB)
Link : https://furunavi.jp/

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
LINK = "https://furunavi.jp"

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
        self.category = self.html.find(class_="category_list_all")
        self.category = self.category.find(class_=self.elementTag)
        self.liTag = self.category.li
        while True:
            self.categoryData = re.sub(r'\([^()]*\)', '', self.liTag.find("a").get_text())
            self.categoryData = re.sub(r'\W+', '', self.categoryData)
            ScraperCategory.categoryList.append([LINK+self.liTag.find("a").get("href"),self.categoryData])
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
        self.ChildElement = self.container.find_all("li")
        for _ in self.ChildElement:
            logging.info(f"{threading.current_thread().name}) -{_}")
            #self.itemList.append(_.find(class_="product-image").find("a").get("href"))

    def dataParser(self,html,itemUrl,localNameFinder,titleFinder,descriptionFinder,priceFinder,capacityFinder,imageUrlFinder):
        self.html = bs(html, 'html.parser')
        logging.info(f"{threading.current_thread().name}) -Getting data now...")
        try:
            self.localNameFinder = self.html.find(class_=localNameFinder).find("span").get_text()
            self.localNameFinder_ = self.html.find(class_=localNameFinder).find("p").get_text()
            self.localNameFinder = self.localNameFinder + self.localNameFinder_
            self.localNameFinder =  re.sub(r'\W+', '', self.localNameFinder)
        except:
            raise Exception ("Unable to locate the localNameFinder")
        try:
            self.titleFinder = self.html.find(class_=titleFinder).find("h1").get_text()
            self.titleFinder = re.sub(r'\W+', '', self.titleFinder)
        except:
            raise Exception ("Unable to locate the titleFinder")
        try:
            self.descriptionFinder = self.html.find(class_=descriptionFinder).get_text()
            self.descriptionFinder = re.sub(r'\W+', '', self.descriptionFinder)
        except:
            raise Exception ("Unable to locate the descriptionFinder")
        try:
            self.priceFinder = self.html.find(class_=priceFinder).find("i").get_text()
            self.priceFinder = re.sub(r'\W+', '', self.priceFinder)
        except:
            raise Exception ("Unable to locate the priceFinder")
        try:
            self.capacityFinder = self.html.find(class_=capacityFinder).get_text()
            self.capacityFinder = re.sub(r'\W+', '', self.capacityFinder)
        except:
            raise Exception ("Unable to locate the capacityFinder")
        try:
            self.imageUrlFinder = self.html.find(class_=imageUrlFinder).find_all("li")
            self.imageList = []
            for _ in self.imageUrlFinder:
                self.imageList.append(_.find("img").get("src")) 
        except:
            raise Exception ("Unable to locate the imageUrlFinder")
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
    item_url = data[0]
    scrapeURL = DataCollector(item_url)
    scrapeURL.driver.get(scrapeURL.url)
    logging.info(f"{threading.current_thread().name}) -Fetching...{item_url}")
    try:
        time.sleep(1)
        item_info = WebDriverWait(scrapeURL.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "m_info")))
        scrapeURL.dataParser(html = scrapeURL.driver.page_source,
                           itemUrl = item_url, 
                           localNameFinder = "m_info",
                           titleFinder = "page_product_single",
                           descriptionFinder = "product_description",
                           priceFinder = "product_price",
                           capacityFinder = "product_detail",
                           imageUrlFinder = "swiper-wrapper")
    except:
        scrapeURL.driver.close()
        scrapeURL.driver.quit()
        raise Exception (f"{threading.current_thread().name}) - Unable to load the element")
    scrapeURL.driver.close()
    scrapeURL.driver.quit()

def ItemLinkCollector(data):
    prev_btn = ""
    nxt_btn ="pagination"
    element_container = "list-product"
    url_category=data[0]
    category=data[1]
    scrapeURL = DataCollector(url_category)
    scrapeURL.driver.get(scrapeURL.url)
    logging.info(f"{threading.current_thread().name}) -Scraping...{category}:{url_category}")
    while True:
        try:
            time.sleep(3)
            itemlist = WebDriverWait(scrapeURL.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, element_container)))
            scrapeURL.listParser(html =scrapeURL.driver.page_source, elementContainer = element_container)
            try:
                nextButton = scrapeURL.driver.find_element_by_class_name(nxt_btn)
                currentval = nextButton.find_element_by_class_name("current")
                nextButton = nextButton.find_elements_by_tag_name("li")
                
                
                # if prev_btn == "":
                #     logging.info(f"{threading.current_thread().name}) -Active_thread : {int(threading.activeCount())-1} Next_Page of {category}")
                #     nextButton[-1].find_element_by_class_name("page_next").click()

                if prev_btn != currentval.text:
                    logging.info(f"{threading.current_thread().name}) -Active_thread : {int(threading.activeCount())-1} Next_Page of {category}")
                    nextButton[-1].find_element_by_class_name("page_next").click()

                if prev_btn == currentval.text:
                    logging.info(f"{threading.current_thread().name}) -Active_thread : {int(threading.activeCount())-1} Exiting {category} ")
                    while True:
                        if scrapeURL.isNotActive:            
                            scrapeURL.isNotActive = False
                            for _ in scrapeURL.itemList:
                                scrapeURL.data.append([_,category])
                            scrapeURL.isNotActive = True
                            logging.info(f"{threading.current_thread().name}) -Adding {len(scrapeURL.itemList)} items | Total item {len(scrapeURL.data)}")
                            break
                    break
                prev_btn = currentval.text
       
            except:
                raise Exception (f"{threading.current_thread().name}) -Unable to load the element")
                break
                
        except:
            scrapeURL.driver.close()
            scrapeURL.driver.quit()
            raise Exception (f"{threading.current_thread().name}) -Unable to load the element")
            break
    scrapeURL.driver.close()
    scrapeURL.driver.quit()


if __name__ == '__main__':
    start = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Scraping has been started...")
    site=ScraperCategory(LINK)
    site.driver.get(site.url)
    current_url, user_agent = site.displaySiteInfo()
    logging.info(f"{threading.current_thread().name}) -{current_url} {user_agent}")
    site.categoryParser(html= site.driver.page_source, elementTag = "category_list")
    # datum=site.categoryList
    datum=[['https://furunavi.jp/Product/Search?subcategoryid=174,175,176,177,178,179&categoryid=19','test']]
    site.driver.close()
    final = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds for fetching {len(datum)} categories")
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8 , thread_name_prefix='Scraper') as executor:
        futures = [executor.submit(ItemLinkCollector, data) for data in datum]
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                logging.info(f"{threading.current_thread().name}) -{future.result()}")
    final = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  fetch  {len(DataCollector.data)} items URL")

    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(thread_name_prefix='Fetching_Item_Data') as executor:
        futures = [executor.submit(DataCollectorFunction, data) for data in DataCollector.data]
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                logging.info(f"{threading.current_thread().name}) -{future.result()}")
    final = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  scrape  {len(DataCollector.data)} items data")