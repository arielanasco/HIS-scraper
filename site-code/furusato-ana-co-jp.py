"""

Site : ANA's hometown tax payment	
Link : https://furusato.ana.co.jp/	

"""
from web_driver import SaveData
import web_driver_1
import time
import threading 
import logging
import  concurrent.futures
from bs4 import BeautifulSoup as bs
import re

import os

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
        self.managementNumber =  "NA"        
        self.compName =  "NA"        
        self.capacityFinder =  "NA"
        self.shipMethod =  "NA"
        self.stockStatus =  "NA"
        self.localNameFinder =  "NA"
        self.titleFinder = "NA"
        self.descriptionFinder = "NA"
        self.priceFinder = "NA"
        self.imageList = "NA"
        self.consumption = "NA"
        self.appDeadline ="NA"  

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
    def dataParser(self,html,itemUrl,stockStatus,categoryFinder,localNameFinder,managementNumber,appDeadline,titleFinder,descriptionFinder,priceFinder,
                   shipMethod,capacityFinder,consumption,compName,imageUrlFinder):
        self.html = bs(html, 'html.parser')
        self.table = self.html.find(class_="as-tbset")
        self.th = self.table.find_all("th")
        self.td = self.table.find_all("td")
        for _ in self.th:
            self.dt_ = _.get_text()
            if re.match("内容量",self.dt_):
                try:
                    self.capacityFinder = self.td[self.th.index(_)].get_text()
                except:
                    self.capacityFinder = "NA" 
            if re.match("賞味期限",self.dt_):
                try:
                    self.consumption = self.td[self.th.index(_)].get_text()
                except:
                    self.consumption = "NA"
            if re.match("事業者名",self.dt_): 
                try:
                    self.compName = self.td[self.th.index(_)].get_text()
                except:
                    self.compName = "NA"

        try:
            self.stockStatus = self.html.find(class_=stockStatus).find("span").get_text()
            self.stockStatus =  re.sub(r'\W+', '', self.stockStatus)
        except:
            self.stockStatus =  "NA"
        try:
            self.localNameFinder = self.html.find(class_=localNameFinder).get_text()
            self.localNameFinder = re.sub(r'\s+', '', self.localNameFinder)
        except:
            self.localNameFinder = "NA"
        try:
            self.managementNumber = self.html.find(name=managementNumber).get_text()
            self.managementNumber =  re.sub(r'\W+', '', self.managementNumber)
        except:
            self.managementNumber =  "NA"    
        try:
            self.titleFinder = self.html.find(class_=titleFinder).get_text()
            self.titleFinder = re.sub(r'\s+', '', self.titleFinder)
            if self.managementNumber != "NA":
                self.titleFinder.replace(self.managementNumber,"")
                self.titleFinder = self.titleFinder[2:]
        except:
            self.titleFinder = "NA"
        try:
            self.descriptionFinder = self.html.find(class_=descriptionFinder).get_text()
            self.descriptionFinder = re.sub(r'\s+', '', self.descriptionFinder)
        except:
            self.descriptionFinder = "NA"
        try:
            self.priceFinder = self.html.find(class_=priceFinder).get_text()
            self.priceFinder = re.sub(r'\s+', '', self.priceFinder)
        except:
            self.priceFinder = "NA"
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
                        DataParserClass.data[index_]["stock_status"] =self.stockStatus
                        DataParserClass.data[index_]["local_name"] =self.localNameFinder
                        DataParserClass.data[index_]["management_number"] =self.managementNumber
                        DataParserClass.data[index_]["app_deadline"] =self.appDeadline
                        DataParserClass.data[index_]["title"] =self.titleFinder
                        DataParserClass.data[index_]["description"] =self.descriptionFinder
                        DataParserClass.data[index_]["price"] =self.priceFinder
                        DataParserClass.data[index_]["ship_method"] =self.shipMethod
                        DataParserClass.data[index_]["capacity"] =self.capacityFinder
                        DataParserClass.data[index_]["consumption"] =self.consumption
                        DataParserClass.data[index_]["comp_name"] =self.compName
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
                           stockStatus = "stock",
                           categoryFinder = "NA",
                           localNameFinder = "as-item_pref_detail",
                           managementNumber = "product_code",
                           appDeadline = "NA",
                           titleFinder = "as-item_name_detail",
                           descriptionFinder = "as-txarea_m",
                           priceFinder = "as-pl_m",
                           shipMethod = "td",
                           capacityFinder = "td",
                           consumption = "td",
                           compName = "td",
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
    site.categoryParser(html= site.get(LINK).text, elementTag = "gnav_detail_contents")
    data=site.categoryList
    # save_data = SaveData()
    # for  datum in data:
    #     save_data.query_db_save_catgy(datum)
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

    start = time.perf_counter()
    site_name = os.path.basename(__file__).split(".")[0]
    cwd = os.getcwd()
    save_data = SaveData()
    for data_dict in DataParserClass.data:
        for image_link in data_dict["images"]:
            save_data.save_img(cwd,site_name,data_dict["category"],data_dict["title"],image_link)
    final = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  scrape  {len(DataParserClass.data)} items images")
