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
                ScraperCategory.categoryList.append([category_[-1].find("a").get("href"),self.categoryData])                

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
            raise Exception ("Unable to locate the localNameFinder")
        try:
            self.titleFinder = self.html.find(class_=titleFinder).get_text()
            self.titleFinder = self.titleFinder.replace(self.localNameFinder,'')
            self.titleFinder = re.sub(r'\s+', '', self.titleFinder)
        except:
            raise Exception ("Unable to locate the titleFinder")
        try:
            self.descriptionFinder = self.html.find(class_=descriptionFinder).get_text()
            self.descriptionFinder = re.sub(r'\s+', '', self.descriptionFinder)
        except:
            raise Exception ("Unable to locate the descriptionFinder")
        try:
            self.priceFinder = self.html.find(class_=priceFinder).get_text()
            self.priceFinder = re.sub(r'\s+', '', self.priceFinder)
        except:
            raise Exception ("Unable to locate the priceFinder")
        try:
            self.capacityFinder = self.html.find(class_=capacityFinder).get_text()
            self.capacityFinder = re.sub(r'\s+', '', self.capacityFinder)
        except:
            raise Exception ("Unable to locate the capacityFinder")
        try:
            self.imageUrlFinder = self.html.find(class_="as-detail_wrap").find(class_=imageUrlFinder).find_all("li")
            self.imageList = []
            for _ in self.imageUrlFinder:
                self.imageList.append("https://furusato.ana.co.jp"+_.find("img").get("src")) 
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
    scrapeURL = DataParserClass()
    logging.info(f"{threading.current_thread().name}) -Scraped_items({DataParserClass.totalData}/{len(DataParserClass.data)}) -Fetching({item_url})")
    time.sleep(3)
    scrapeURL.dataParser(html = scrapeURL.get(item_url).text,
                           itemUrl = item_url, 
                           localNameFinder = "as-item_pref_detail",
                           titleFinder = "as-item_name_detail",
                           descriptionFinder = "as-txarea_m",
                           priceFinder = "as-pl_m",
                           capacityFinder = "table01",
                           imageUrlFinder = "as-main" )



def ItemLinkCollector(data):
    element_container = "as-flex_left"
    url_category=data[0]
    category=data[1]
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
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Next_Page({category}) -Scraped_categories({DataParserClass.totalList -1}/{len(ScraperCategory.categoryList)})")
        else:
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category}) -Scraped_categories({DataParserClass.totalList -1}/{len(ScraperCategory.categoryList)})")
            while True:
                if scrapeURL.isNotActive:            
                    scrapeURL.isNotActive = False
                    for _ in scrapeURL.itemList:
                        scrapeURL.data.append(["https://furusato.ana.co.jp"+_,category])
                    scrapeURL.isNotActive = True
                    logging.info(f"{threading.current_thread().name}) -Adding {len(scrapeURL.itemList)} items | Total item {len(scrapeURL.data)}")
                    break
            break

if __name__ == '__main__':
    start = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Scraping has been started...")
    site=ScraperCategory()
    user_agent = site.displaySiteInfo()
    logging.info(f"{threading.current_thread().name}) -{user_agent}")
    site.categoryParser(html= site.get(LINK).text, elementTag = "gnav_detail_contents")
    data=site.categoryList
    # data = [['https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E8%82%89_%E8%B1%9A%E8%82%89_%E4%B8%89%E5%85%83%E8%B1%9A&sort=number5%2CNumber1%2CScore','ANAオリジナル']]
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