"""

Site : ANA's hometown tax payment	
Link : https://furusato.ana.co.jp/	

"""
import web_driver_1
import time
import threading 
import logging
import  concurrent.futures
from bs4 import BeautifulSoup as bs
import re
""" This section declares all the variables used """
LINK = "https://furusato.ana.co.jp/products/list.php"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s](%(levelname)s@%(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)

data_lock = threading.Lock()

class ScraperCategory(web_driver_1.WebDriver):
    categoryList = []

    def __init__(self):
        super().__init__()

    def categoryParser(self,**kwargs):
        self.elementTag = kwargs.get("elementTag")
        self.html = bs(kwargs.get("html"), 'html.parser')
        self.category_container = self.html.find(class_="gNavContainer1")
        self.category_container = self.category_container.find_all(class_=self.elementTag)
        for category in  self.category_container:
            category_ = category.find_all("li")
            if len(category_) > 2 :
                for _ in category_[2:]:
                    self.categoryData = re.sub(r'\([^()]*\)', '', _.find("a").get_text())
                    self.categoryData = re.sub(r'\W+', '', self.categoryData)
                    ScraperCategory.categoryList.append([_.find("a").get("href"),self.categoryData])
            else:
                self.categoryData = re.sub(r'\([^()]*\)', '', category_[-1].find("a").get_text())
                self.categoryData = re.sub(r'\W+', '', self.categoryData)
                ScraperCategory.categoryList.append({"URL":category_[-1].find("a").get("href"),"category":self.categoryData})                

class DataParserClass(web_driver_1.WebDriver):
    isNotActive = True
    data = []
    totalData = 0
    totalList = 0


    def __init__(self):
        self.itemList = []
        type(self).totalList +=1
        type(self).totalData +=1
        super().__init__()

    def listParser(self,html,elementContainer):
        self.elementContainer = elementContainer
        self.html = bs(html, 'html.parser')
        self.container = self.html.find(id="main_column")
        self.container = self.container.find(class_=self.elementContainer)
        self.ChildElement = self.container.find_next()
        while True:
            self.itemList.append(self.ChildElement.find("div").get("data-product-url"))
            if self.ChildElement.find_next_sibling():
                self.ChildElement = self.ChildElement.find_next_sibling()
            else:
                break

    def dataParser(self,html,itemUrl,localNameFinder,titleFinder,descriptionFinder,priceFinder,capacityFinder,imageUrlFinder):
        self.html = bs(html, 'html.parser')
        try:
            self.localNameFinder = self.html.find(class_=localNameFinder).get_text()
            self.localNameFinder = re.sub(r'\s+', '', self.localNameFinder)
        except:
            self.localNameFinder = None
        try:
            self.titleFinder = self.html.find(class_=titleFinder).get_text()
            self.titleFinder = self.titleFinder.replace(self.localNameFinder,'')
            self.titleFinder = re.sub(r'\s+', '', self.titleFinder)
        except:
            self.titleFinder = None
        try:
            self.descriptionFinder = self.html.find(class_=descriptionFinder).get_text()
            self.descriptionFinder = re.sub(r'\s+', '', self.descriptionFinder)
        except:
            self.descriptionFinder = None
        try:
            self.priceFinder = self.html.find(class_=priceFinder).get_text()
            self.priceFinder = re.sub(r'\s+', '', self.priceFinder)
        except:
            self.priceFinder = None
        try:
            self.capacityFinder = self.html.find(class_=capacityFinder).get_text()
            self.capacityFinder = re.sub(r'\s+', '', self.capacityFinder)
        except:
            self.capacityFinder = None
        try:
            self.imageUrlFinder = self.html.find(class_="as-detail_wrap").find(class_=imageUrlFinder).find_all("li")
            self.imageList = []
            for _ in self.imageUrlFinder:
                self.imageList.append("https://furusato.ana.co.jp"+_.find("img").get("src")) 
        except:
            self.imageList = []
        with data_lock:
                for data in  DataParserClass.data:
                    if itemUrl == data["URL"]:
                        index_ = DataParserClass.data.index(data)
                        DataParserClass.data[index_]["local_name"] =self.localNameFinder
                        DataParserClass.data[index_]["title"] =self.titleFinder
                        DataParserClass.data[index_]["description"] =self.descriptionFinder
                        DataParserClass.data[index_]["price"] =self.priceFinder
                        DataParserClass.data[index_]["capacity"] =self.capacityFinder
                        DataParserClass.data[index_]["images"] =self.imageList
                        break

def DataCollectorFunction(data):
    item_url = data["URL"]
    scrapeURL = DataParserClass()
    logging.info(f"{threading.current_thread().name}) -Scraped_items({DataParserClass.totalData -1 }/{len(DataParserClass.data)}) -Fetching({item_url})")
    try:
        html = scrapeURL.get(item_url).text
        time.sleep(3)
        scrapeURL.dataParser(html = html,
                           itemUrl = item_url, 
                           localNameFinder = "as-item_pref_detail",
                           titleFinder = "as-item_name_detail",
                           descriptionFinder = "as-txarea_m",
                           priceFinder = "as-pl_m",
                           capacityFinder = "table01",
                           imageUrlFinder = "as-main" )
    except:
        raise Exception (f"{threading.current_thread().name}) - Unable to load the element")


def ItemLinkCollector(data):
    element_container = "as-flex_left"
    url_category=data["URL"]
    category=data["category"]
    scrapeURL = DataParserClass()
    logging.info(f"{threading.current_thread().name}) -Scraping([{category}]{url_category})")
    while True:
        html =scrapeURL.get(url_category).text
        time.sleep(1)
        scrapeURL.listParser(html =html, elementContainer = element_container)
        html_ = bs(html, 'html.parser')
        nextButton = html_.find(class_="pager_links")
        nextButton = nextButton.find_all(class_="pager_link")
        url_category_ = LINK+nextButton[-1].find("a").get("href")
        if url_category != url_category_ and len(nextButton) > 1 :
            url_category = url_category_
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Next_Page({category}) -Scraped_categories({DataParserClass.totalList}/{len(ScraperCategory.categoryList)})")
        else:
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category}) -Scraped_categories({DataParserClass.totalList}/{len(ScraperCategory.categoryList)})")
            with data_lock:
                for _ in scrapeURL.itemList:
                    DataParserClass.data.append({"URL":"https://furusato.ana.co.jp"+_,"category":category})
                logging.info(f"{threading.current_thread().name}) -Adding_items({len(scrapeURL.itemList)})  -Total_item({len(DataParserClass.data)})")
            break


if __name__ == '__main__':
    start = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Scraping has been started...")
    site=ScraperCategory()
    user_agent = site.displaySiteInfo()
    logging.info(f"{threading.current_thread().name}) -{user_agent}")
    site.categoryParser(html= site.get(LINK).text, elementTag = "gnav_detail_contents")
    data=site.categoryList
    data = [{'URL':'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E8%82%89_%E7%89%9B%E8%82%89_%E5%B1%B1%E5%BD%A2%E7%89%9B&sort=number5%2CNumber1%2CScore',
    'category':'Test'}]
    final = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds for fetching {len(data)} categories")
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(thread_name_prefix='Scraper') as executor:
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
