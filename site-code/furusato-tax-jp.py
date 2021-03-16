"""

Site : Hometown Choice	
Link : https://www.furusato-tax.jp/

"""
from web_driver import WebDriver,SaveData
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

import os

""" This section declares all the variables used """
LINK = "https://www.furusato-tax.jp/product?header"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s](%(levelname)s@%(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)

data_lock = threading.Lock()

class ScraperCategory(WebDriver):
    categoryList = []
    #https://www.furusato-tax.jp/product?header
    #nv-select-categories
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
            for holder in self.holder[1:]:
                self.categoryData = re.sub(r'\([^()]*\)', '', holder.find(class_="lst-subcategories__link").text.strip())
                self.categoryData = re.sub(r'\W+', '', self.categoryData)
                ScraperCategory.categoryList.append({"URL":"https://www.furusato-tax.jp"+holder.find("a").get("href"),"category":self.categoryData})

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

class DataParserClass(WebDriver):

    isNotActive = True
    data = []
    totalData = 0

    def __init__(self, url):
        self.url = url
        type(self).totalData +=1
        super().__init__(url)
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
        

    def dataParser(self,html,itemUrl,stockStatus,localNameFinder,managementNumber,titleFinder,descriptionFinder,priceFinder,
                   shipMethod,capacityFinder,compName,imageUrlFinder):
        self.html = bs(html, 'html.parser')
        self.about = self.html.find(class_="basicinfo_pay")
        self.about = self.about.find_all("tr")
        for _ in self.about:
            self.th = _.find(class_ = "product-tbl-info__label").get_text()
            self.th = re.sub(r'\W+', '', self.th)
            if re.match("容量",self.th):
                try:
                    self.capacityFinder = _.find(class_=capacityFinder).get_text()
                    self.capacityFinder = re.sub(r'\W+', '', self.capacityFinder)
                except:
                    self.capacityFinder = "NA"
            if re.match("自治体での管理番号",self.th):                 
                try:
                    self.managementNumber = _.find(class_=managementNumber).get_text()
                    self.managementNumber =  re.sub(r'\W+', '', self.managementNumber)
                except:
                    self.managementNumber =  "NA"
            
            if re.match("事業者",self.th): 
                try:
                    self.compName = _.find(class_=compName).get_text()
                    self.compName = re.sub(r'\W+', '', self.compName)
                except:
                    self.compName = "NA"

        self.aboutShipment = self.html.find(class_="product-tbl-info")
        self.aboutShipment = self.aboutShipment.find_all("tr")

        for _ in self.aboutShipment:
            self.th = _.find(class_ = "product-tbl-info__label").get_text()
            if re.match("配送",self.th): 
                try:
                    self.shipMethod = self.aboutShipment.find(class_=shipMethod).get_text()
                    self.shipMethod = re.sub(r'\W+', '', self.shipMethod)
                except:
                    self.shipMethod = "NA"
        try:
            self.stockStatus = self.html.find(class_=stockStatus).find("span").get_text()
            self.stockStatus =  re.sub(r'\W+', '', self.stockStatus)
        except:
            self.stockStatus =  "NA"
        try:
            self.localNameFinder = self.html.find(class_=localNameFinder).get_text()
            self.localNameFinder =  re.sub(r'\W+', '', self.localNameFinder)
        except:
            self.localNameFinder =  "NA"
          
        try:
            self.titleFinder = self.html.find(class_=titleFinder).get_text()
            self.titleFinder = re.sub(r'\W+', '', self.titleFinder)
        except:
            self.titleFinder = "NA"
        try:
            self.descriptionFinder = self.html.find(class_=descriptionFinder).get_text()
            self.descriptionFinder = re.sub(r'\W+', '', self.descriptionFinder)
        except:
            self.descriptionFinder = "NA"
        try:
            self.priceFinder = self.html.find(class_=priceFinder).text.strip()
            self.priceFinder = re.sub(r'\W+', '', self.priceFinder)
            self.priceFinder = re.findall('\d+', self.priceFinder )[0]
        except:
            self.priceFinder = "NA"
        try:
            self.imageUrlFinder = self.html.find(id=imageUrlFinder).find(class_="sld__list").find_all("li")
            self.imageList = []
            for _ in self.imageUrlFinder:
                self.imageList.append(_.find("img").get("src")) 
        except:
            self.imageList = "NA"
        with data_lock:
                for data in  DataParserClass.data:
                    if itemUrl == data["URL"]:
                        index_ = DataParserClass.data.index(data)
                        DataParserClass.data[index_]["stock_status"] =self.stockStatus
                        DataParserClass.data[index_]["local_name"] =self.localNameFinder
                        DataParserClass.data[index_]["management_number"] =self.managementNumber
                        DataParserClass.data[index_]["title"] =self.titleFinder
                        DataParserClass.data[index_]["description"] =self.descriptionFinder
                        DataParserClass.data[index_]["price"] =self.priceFinder
                        DataParserClass.data[index_]["ship_method"] =self.shipMethod
                        DataParserClass.data[index_]["capacity"] =self.capacityFinder
                        DataParserClass.data[index_]["comp_name"] =self.compName
                        DataParserClass.data[index_]["images"] =self.imageList
                        break

def DataCollectorFunction(data):
    item_url = data["URL"]
    scrapeURL = DataParserClass(item_url)
    scrapeURL.driver.get(scrapeURL.url)
    logging.info(f"{threading.current_thread().name}) -Scraped_items({DataParserClass.totalData}/{len(DataParserClass.data)}) -Fetching({item_url})")
    try:
        time.sleep(1)
        item_info = WebDriverWait(scrapeURL.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "city-title")))
        scrapeURL.dataParser(html = scrapeURL.driver.page_source,
                           itemUrl = item_url,
                           stockStatus = "stock", 
                           localNameFinder = "city-title",
                           managementNumber = "product-tbl-info__wrap",
                           titleFinder = "ttl-h1__text",
                           descriptionFinder = "overview",
                           priceFinder = "basicinfo_price",
                           shipMethod = "product-tbl-info__wrap",
                           capacityFinder = "product-tbl-info__wrap",
                           compName = "product-tbl-info__wrap",
                           imageUrlFinder = "basicinfo_slider" )
    except:
        scrapeURL.driver.quit()
        raise Exception (f"{threading.current_thread().name}) - Unable to load the element")
    scrapeURL.driver.quit()


def ItemLinkCollector(data):
    element_container = "grid"
    url_category=data["URL"]
    category=data["category"]
    scrapeURL = ListParserClass(url_category)
    scrapeURL.driver.get(scrapeURL.url)
    logging.info(f"{threading.current_thread().name}) -Scraping([{category}]{url_category})")
    while True:
        time.sleep(1)
        itemlist = WebDriverWait(scrapeURL.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, element_container)))
        scrapeURL.listParser(html =scrapeURL.driver.page_source, elementContainer = element_container)
        nextButton = scrapeURL.driver.find_element_by_class_name("nv-pager")
        nextButton = nextButton.find_element_by_class_name("nv-pager__next").find_element_by_class_name("nv-pager__link")
        nxt = nextButton.get_attribute('href')[-1]
        if nxt != "#":
            nextButton.send_keys(Keys.ENTER)
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Next_Page({category}) -Scraped_categories({ListParserClass.totalList}/{len(ScraperCategory.categoryList)})")
        else:
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category}) -Scraped_categories({ListParserClass.totalList}/{len(ScraperCategory.categoryList)})")
            with data_lock:
                for _ in scrapeURL.itemList:
                    DataParserClass.data.append({"URL":"https://www.furusato-tax.jp"+_,"category":category})
                logging.info(f"{threading.current_thread().name}) -Adding_items({len(scrapeURL.itemList)})  -Total_item({len(DataParserClass.data)})")
            break
    scrapeURL.driver.quit()


if __name__ == '__main__':
    start = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Scraping has been started...")
    site=ScraperCategory(LINK)
    site.driver.get(site.url)
    current_url, user_agent = site.displaySiteInfo()
    logging.info(f"{threading.current_thread().name}) -{current_url} {user_agent}")
    site.categoryParser(html= site.driver.page_source, elementTag = "nv-select-categories")
    data=site.categoryList
    site.driver.quit()
    data=[{'URL':'https://www.furusato-tax.jp/search/154?disabled_category_top=1&target=1','category':'test'},
    {'URL':'https://www.furusato-tax.jp/search/153?disabled_category_top=1&target=1','category':'test2'}]
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

    start = time.perf_counter()
    site_name = os.path.basename(__file__).split(".")[0]
    cwd = os.getcwd()
    save_data = SaveData()
    for data_dict in DataParserClass.data:
        for image_link in data_dict["images"]:
            save_data.save_img(cwd,site_name,data_dict["category"],data_dict["title"],image_link)
        save_data.query_db(data_dict)
    final = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  scrape  {len(DataParserClass.data)} items images")