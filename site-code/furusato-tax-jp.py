"""

Site : Hometown Choice	
Link : https://www.furusato-tax.jp/

"""
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
""" This section declares all the variables used """
LINK = "https://www.furusato-tax.jp/search"

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
        self.category = self.category.find_all("ul")
        for category in self.category:
            self.holder = category.find_all("li")
            for holder in self.holder[2:]:
                self.categoryData = re.sub(r'\([^()]*\)', '', holder.find(class_="categories__name").get_text())
                self.categoryData = re.sub(r'\W+', '', self.categoryData)
                ScraperCategory.categoryList.append(["https://www.furusato-tax.jp"+holder.find("a").get("href"),self.categoryData])



        # self.liTag = self.category.li
        # while True:
        #     self.categoryData = re.sub(r'\([^()]*\)', '', self.liTag.find("a").get_text())
        #     self.categoryData = re.sub(r'\W+', '', self.categoryData)
        #     ScraperCategory.categoryList.append(["https://www.furusato-tax.jp"+self.liTag.find("a").get("href"),self.categoryData])
        #     if self.liTag.find_next_sibling():
        #         self.liTag = self.liTag.find_next_sibling()
        #     else:
        #         break

class ListParserClass(WebDriver):
    totalList = 0

    def __init__(self, url):
        self.url = url
        type(self).totalList +=1
        self.itemList = []
        super().__init__(url)

    def listParser(self,html,elementContainer):
        self.elementContainer = elementContainer
        self.html = bs(html, 'html.parser')
        self.container = self.html.find(class_="result-search")
        self.container = self.container.find(class_=self.elementContainer)
        self.ChildElement = self.container.find_next()
        while True:
            self.itemList.append(self.ChildElement.find("a").get("href"))
            if self.ChildElement.find_next_sibling():
                self.ChildElement = self.ChildElement.find_next_sibling()
            else:
                break

class DataParserClass(web_driver_1.WebDriver):

    isNotActive = True
    data = []
    totalData = 0

    def __init__(self, url):
        self.url = url
        type(self).totalData +=1
        super().__init__()



    def dataParser(self,html,itemUrl,localNameFinder,titleFinder,descriptionFinder,priceFinder,capacityFinder,imageUrlFinder):
        self.html = bs(html, 'html.parser')
        try:
            self.localNameFinder = self.html.find(class_="inner").find(class_=localNameFinder).get_text()
            self.localNameFinder =  re.sub(r'\W+', '', self.localNameFinder)
        except:
            raise Exception ("Unable to locate the localNameFinder")
        try:
            self.titleFinder = self.html.find(class_=titleFinder).get_text()
            self.titleFinder = re.sub(r'\W+', '', self.titleFinder)
        except:
            raise Exception ("Unable to locate the titleFinder")
        try:
            self.descriptionFinder = self.html.find(class_=descriptionFinder).get_text()
            self.descriptionFinder = re.sub(r'\W+', '', self.descriptionFinder)
        except:
            raise Exception ("Unable to locate the descriptionFinder")
        try:
            self.priceFinder = self.html.find(class_=priceFinder).get_text()
            self.priceFinder = re.sub(r'\W+', '', self.priceFinder)
        except:
            raise Exception ("Unable to locate the priceFinder")
        try:
            self.capacityFinder = self.html.find(class_=capacityFinder).get_text()
            self.capacityFinder = re.sub(r'\W+', '', self.capacityFinder)
        except:
            raise Exception ("Unable to locate the capacityFinder")
        try:
            self.imageUrlFinder = self.html.find(id=imageUrlFinder).find(class_="sld__list").find_all("li")
            self.imageList = []
            for _ in self.imageUrlFinder:
                self.imageList.append(_.find("img").get("src")) 
        except:
            raise Exception ("Unable to locate the imageUrlFinder")
        while True:
            if DataParserClass.isNotActive: 
                DataParserClass.isNotActive = False
                for data in DataParserClass.data:
                    if itemUrl in data:
                        index_ = DataParserClass.data.index(data)
                        DataParserClass.data[index_].insert(2,self.localNameFinder)
                        DataParserClass.data[index_].insert(3,self.titleFinder)
                        DataParserClass.data[index_].insert(4,self.descriptionFinder)
                        DataParserClass.data[index_].insert(5,self.priceFinder)
                        DataParserClass.data[index_].insert(6,self.capacityFinder)
                        DataParserClass.data[index_].insert(7,self.imageList)
                        DataParserClass.isNotActive = True
                        break
            break

def DataCollectorFunction(data):
    item_url = data[0]
    scrapeURL = DataParserClass(item_url)
    # scrapeURL.driver.get(scrapeURL.url)
    logging.info(f"{threading.current_thread().name}) -Scraped_items({DataParserClass.totalData}/{len(DataParserClass.data)}) -Fetching({item_url})")
    try:
        time.sleep(2)
        # item_info = WebDriverWait(scrapeURL.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "city-title")))
        scrapeURL.dataParser(html =  scrapeURL.get(item_url).text,
                           itemUrl = item_url, 
                           localNameFinder = "city-title",
                           titleFinder = "ttl-h1__text",
                           descriptionFinder = "overview",
                           priceFinder = "basicinfo_price",
                           capacityFinder = "basicinfo_pay",
                           imageUrlFinder = "basicinfo_slider" )
    except:
        # scrapeURL.driver.quit()
        raise Exception (f"{threading.current_thread().name}) - Unable to load the element")
    # scrapeURL.driver.quit()


def ItemLinkCollector(data):
    nxt_btn =  "//*[@id='main']/div[3]/div[2]/div[1]/div[4]/div[3]/div/div[2]/a"
    nxt_btn1 = "//*[@id='main']/div[2]/div[2]/div[1]/div[4]/div[3]/div/div[3]/a"
    element_container = "grid"
    url_category=data[0]
    category=data[1]
    scrapeURL = ListParserClass(url_category)
    scrapeURL.driver.get(scrapeURL.url)
    logging.info(f"{threading.current_thread().name}) -Scraping([{category}]{url_category})")
    while True:
        try:
            time.sleep(1)
            itemlist = WebDriverWait(scrapeURL.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, element_container)))
            scrapeURL.listParser(html =scrapeURL.driver.page_source, elementContainer = element_container)
            try:
                # try:
                #     nextButton = scrapeURL.driver.find_element_by_xpath(nxt_btn)
                # except:    
                #     nextButton = scrapeURL.driver.find_element_by_xpath(nxt_btn1)
                nextButton = scrapeURL.driver.find_element_by_class_name("nv-pager__next").find_element_by_tag_name("a")
                nextButton.send_keys(Keys.ENTER)
                logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Next_Page({category}) -Scraped_categories({ListParserClass.totalList}/{len(ScraperCategory.categoryList)})")
            except NoSuchElementException:
                logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category}) -Scraped_categories({ListParserClass.totalList}/{len(ScraperCategory.categoryList)})")
                while True:
                    if DataParserClass.isNotActive:            
                        DataParserClass.isNotActive = False
                        for _ in scrapeURL.itemList:
                            DataParserClass.data.append(["https://www.furusato-tax.jp"+_,category])
                        DataParserClass.isNotActive = True
                        logging.info(f"{threading.current_thread().name}) -Adding {len(scrapeURL.itemList)} items | Total item {len(DataParserClass.data)}")
                        break
                break
        except:
            scrapeURL.driver.quit()
            raise Exception (f"{threading.current_thread().name}) -Unable to load the element")
            break
    scrapeURL.driver.quit()


if __name__ == '__main__':
    start = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Scraping has been started...")
    site=ScraperCategory(LINK)
    site.driver.get(site.url)
    current_url, user_agent = site.displaySiteInfo()
    logging.info(f"{threading.current_thread().name}) -{current_url} {user_agent}")
    site.categoryParser(html= site.driver.page_source, elementTag = "search-child-categories")
    # data=site.categoryList
    data=[['https://www.furusato-tax.jp/search/152?disabled_category_top=1&target=1','test']]
    site.driver.close()
    final = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds for fetching {len(data)} categories")
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8 , thread_name_prefix='Fetching_URL') as executor:
        futures = [executor.submit(ItemLinkCollector, datum) for datum in data]
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                logging.info(f"{threading.current_thread().name}) -{future.result()}")
    final = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  fetch  {len(DataParserClass.data)} items URL")

    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(thread_name_prefix='Fetching_Item_Data') as executor:
        futures = [executor.submit(DataCollectorFunction, data) for data in DataParserClass.data]
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                logging.info(f"{threading.current_thread().name}) -{future.result()}")
    final = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  scrape  {len(DataParserClass.data)} items data")