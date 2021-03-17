"""

Site : au PAY Hometown tax payment	
Link : https://furusato.wowma.jp/

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
LINK = "https://furusato.wowma.jp"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s](%(levelname)s@%(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)

data_lock = threading.Lock()

class ScraperCategory(WebDriver):
    categoryList = []

    def __init__(self, url):
        self.url = url
        super().__init__(url)

    def categoryParser(self,**kwargs):
        self.elementTag = kwargs.get("elementTag")
        self.html = bs(kwargs.get("html"), 'html.parser')
        self.category = self.html.find(class_=self.elementTag)
        self.category = self.category.find("ul")
        self.liTag = self.category.find("li")
        self.liTag = self.liTag.find("li")
        while True:
            self.parent_category_id = self.liTag.find("input").get("value")
            self.child_categories = self.liTag.find(class_="category-child").find_all("li")
            for _ in self.child_categories:
                self.child_category_id = _.find("input").get("value")
                self.child_category_name = _.find("label").get_text()
                ScraperCategory.categoryList.append({"URL":f"https://furusato.wowma.jp/products/list.php?parent_category={self.parent_category_id}&category_{self.child_category_id}={self.child_category_id}","category":self.child_categories})
            if self.liTag.find_next_sibling():
                self.liTag = self.liTag.find_next_sibling()
            else:
                break
            # self.categoryData = re.sub(r'\([^()]*\)', '', self.liTag.find("a").get_text())
            # self.categoryData = re.sub(r'\W+', '', self.categoryData)
            # ScraperCategory.categoryList.append({"URL":self.liTag.find("a").get("href"),"category":self.categoryData})
            # if self.liTag.find_next_sibling():
            #     self.liTag = self.liTag.find_next_sibling()
            # else:
            #     break

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
        self.container = self.html.find(class_="category-sort-contents")
        self.container = self.container.find(class_=self.elementContainer)
        self.ChildElement = self.container.find_all(class_="contents-detail")
        for _ in self.ChildElement:
            self.itemList.append(_.find(class_="item-list").get("href"))

class DataParserClass(web_driver_1.WebDriver):

    isNotActive = True
    data = []
    totalData = 0

    def __init__(self, url):
        self.url = url
        type(self).totalData +=1
        super().__init__()

    def dataParser(self,html,itemUrl,categoryFinder,localNameFinder,titleFinder,descriptionFinder,priceFinder,capacityFinder,imageUrlFinder):
        self.html = bs(html, 'html.parser')
        try:
            self.categoryFinder = self.html.find(class_=categoryFinder).find_all("li")
            self.categoryFinder = self.categoryFinder[-2].find("a").get_text()
            self.categoryFinder =  re.sub(r'\W+', '', self.categoryFinder)
        except:
            self.categoryFinder =  None
        try:
            self.localNameFinder = self.html.find(class_=localNameFinder).get_text()
            self.localNameFinder = re.sub(r'\W+', '', self.localNameFinder)
        except:
            self.localNameFinder = None
        try:
            self.titleFinder = self.html.find(class_=titleFinder).find_all("li")
            self.titleFinder = self.titleFinder[-1].get_text()
            self.titleFinder = re.sub(r'\W+', '', self.titleFinder)
        except:
            self.titleFinder = None
        try:
            self.descriptionFinder = self.html.find(class_=descriptionFinder).get_text()
            self.descriptionFinder = re.sub(r'\W+', '', self.descriptionFinder)
        except:
            self.descriptionFinder = None
        try:
            self.priceFinder = self.html.find(id=priceFinder).get_text()
            self.priceFinder = re.sub(r'\W+', '', self.priceFinder)
        except:
            self.priceFinder = None
        try:
            self.capacityFinder = self.html.find(class_=capacityFinder).find("ul").get_text()
            self.capacityFinder = re.sub(r'\W+', '', self.capacityFinder)
        except:
            self.capacityFinder = None
        try:
            self.imageUrlFinder = self.html.find(class_=imageUrlFinder).find_all("img")
            self.imageList = []
            for _ in self.imageUrlFinder:
                self.img= _.get("src") 
                self.imageList.append(LINK+self.img)      
  
        except:
            self.imageList = []
        with data_lock:
                for data in DataParserClass.data:
                    if itemUrl ==  data["URL"]:
                        index_ = DataParserClass.data.index(data)
                        DataParserClass.data[index_]["category"] =self.categoryFinder
                        DataParserClass.data[index_]["local_name"] =self.localNameFinder
                        DataParserClass.data[index_]["title"] =self.titleFinder
                        DataParserClass.data[index_]["description"] =self.descriptionFinder
                        DataParserClass.data[index_]["price"] =self.priceFinder
                        DataParserClass.data[index_]["capacity"] =self.capacityFinder
                        DataParserClass.data[index_]["images"] =self.imageList
                        break

def DataCollectorFunction(data):
    item_url = data["URL"]
    scrapeURL = DataParserClass(item_url)
    logging.info(f"{threading.current_thread().name}) -Scraped_items({DataParserClass.totalData}/{len(DataParserClass.data)}) -Fetching({item_url})")
    try:
        time.sleep(3)
        scrapeURL.dataParser(html = scrapeURL.get(item_url).text,
                           itemUrl = item_url,
                           categoryFinder = "breadcrumb", 
                           localNameFinder = "municipality-name",
                           titleFinder = "breadcrumb",
                           descriptionFinder = "gift-comment",
                           priceFinder = "gift-money-contents",
                           capacityFinder = "slider-txt",
                           imageUrlFinder = "thumbnail-photo" )
    except:
        raise Exception (f"{threading.current_thread().name}) - Unable to load the element")

def ItemLinkCollector(data):
    nxt_btn ="next"
    element_container = "list-column2"
    url_category=data["URL"]
    category=data["category"]
    scrapeURL = ListParserClass(url_category)
    scrapeURL.driver.get(scrapeURL.url)
    logging.info(f"{threading.current_thread().name}) -Scraping([{category}]{url_category})")
    while True:
        time.sleep(1)
        itemlist = WebDriverWait(scrapeURL.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, element_container)))
        scrapeURL.listParser(html =scrapeURL.driver.page_source, elementContainer = element_container)
        nextButton = scrapeURL.driver.find_element_by_class_name(nxt_btn)
        if nextButton.get_attribute("href") == 'javascript:void(0);':
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category}) -Scraped_categories({ListParserClass.totalList}/{len(ScraperCategory.categoryList)})")
            with data_lock:
                for _ in scrapeURL.itemList:
                    DataParserClass.data.append({"URL":LINK+_,"category":category})
                logging.info(f"{threading.current_thread().name}) -Adding_items({len(scrapeURL.itemList)})  -Total_item({len(DataParserClass.data)})")
            break
        else:
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Next_Page({category}) -Scraped_categories({ListParserClass.totalList}/{len(ScraperCategory.categoryList)})")
            nextButton.click()
    scrapeURL.driver.quit()

if __name__ == '__main__':
    start = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Scraping has been started...")
    site=ScraperCategory(LINK)
    site.driver.get(site.url)
    current_url, user_agent = site.displaySiteInfo()
    logging.info(f"{threading.current_thread().name}) -{current_url} {user_agent}")
    site.categoryParser(html= site.driver.page_source, elementTag = "list-contents")
    data=site.categoryList
    # data=[{'URL':'https://furusato.wowma.jp/products/list.php?parent_category=244','category':'Metalwork'},
    # {'URL':'https://furusato.wowma.jp/products/list.php?parent_category=274','category':'Doll'}
    # ]
    site.driver.quit()
    final = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds for fetching {len(data)} categories")
    # start = time.perf_counter()
    # with concurrent.futures.ThreadPoolExecutor(max_workers=8 , thread_name_prefix='Fetching_URL') as executor:
    #     futures = [executor.submit(ItemLinkCollector, datum) for datum in data]
    #     for future in concurrent.futures.as_completed(futures):
    #         if future.result():
    #             logging.info(f"{threading.current_thread().name}) -{future.result()}")
    # final = time.perf_counter()
    # logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  fetch  {len(DataParserClass.data)} items URL")

    # start = time.perf_counter()
    # with concurrent.futures.ThreadPoolExecutor(thread_name_prefix='Fetching_Item_Data') as executor:
    #     futures = [executor.submit(DataCollectorFunction, data) for data in DataParserClass.data]
    #     for future in concurrent.futures.as_completed(futures):
    #         if future.result():
    #             logging.info(f"{threading.current_thread().name}) -{future.result()}")
    # final = time.perf_counter()
    # logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  scrape  {len(DataParserClass.data)} items data")
