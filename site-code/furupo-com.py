"""

Site : Furupo (JTB)	
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
        self.liTag_ = self.category.li
        while True:
            self.liTag = self.liTag_.find_all("li")
            for _ in self.liTag:
                self.categoryData = re.sub(r'\([^()]*\)', '', _.find("a").get_text())
                self.categoryData = re.sub(r'\W+', '', self.categoryData)
                ScraperCategory.categoryList.append({"URL":_.find("a").get("href"),"category":self.categoryData})
            if self.liTag_.find_next_sibling():
                self.liTag_ = self.liTag_.find_next_sibling()
            else:
                break

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
        self.container = self.html.find(class_=self.elementContainer)
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
        self.consumption = "NA"


    def dataParser(self,html,itemUrl,stockStatus,localNameFinder,managementNumber,titleFinder,descriptionFinder,priceFinder,
                   shipMethod,capacityFinder,consumption,compName,imageUrlFinder):
        self.html = bs(html, 'html.parser')
        self.about = self.html.find(class_="info")
        self.about = self.about.find_all(class_="cell")
        for _ in self.about:
            self.th = _.find("l-cell").get_text()
            self.th = re.sub(r'\W+', '', self.th)
            if re.match("配送方法",self.th): 
                try:
                    self.shipMethod = self.aboutShipment.find(class_=shipMethod).get_text()
                    self.shipMethod = re.sub(r'\W+', '', self.shipMethod)
                except:
                    self.shipMethod = "NA"
            if re.match("容量",self.th):
                try:
                    self.capacityFinder = _.find(class_ = capacityFinder).get_text()
                    self.capacityFinder = re.sub(r'\W+', '', self.capacityFinder)
                except:
                    self.capacityFinder = "NA"  
            if re.match("賞味期限",self.th):
                try:
                    self.consumption = _.find(class_ = consumption).get_text()
                    self.consumption = re.sub(r'\W+', '', self.consumption)
                except:
                    self.consumption = "NA"
            if re.match("管理番号",self.th):                 
                try:
                    self.managementNumber = _.find(class_= managementNumber).get_text()
                    self.managementNumber =  re.sub(r'\W+', '', self.managementNumber)
                except:
                    self.managementNumber =  "NA"
        self.aboutShipment = self.html.find(class_="company-info")
        self.aboutShipment = self.aboutShipment.find_all("cell")
        for _ in self.aboutShipment:
            self.th = _.find(class_ = "l-cell").get_text()
            self.th = re.sub(r'\W+', '', self.th)
            if re.match("事業者名",self.th): 
                try:
                    self.compName = self.aboutShipment.find(class_=compName).get_text()
                    self.compName = re.sub(r'\W+', '', self.compName)
                except:
                    self.compName = "NA"
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
            self.titleFinder = self.html.find(class_=titleFinder).find("h1").get_text()
            self.titleFinder = re.sub(r'\W+', '', self.titleFinder)
        except:
            self.titleFinder = None
        try:
            self.descriptionFinder = self.html.find(class_=descriptionFinder).get_text()
            self.descriptionFinder = re.sub(r'\W+', '', self.descriptionFinder)
        except:
            self.descriptionFinder = None
        try:
            self.priceFinder = self.html.find(class_=priceFinder).get_text()
            self.priceFinder = re.sub(r'\W+', '', self.priceFinder)
        except:
            self.priceFinder = None
        try:
            self.imageUrlFinder = self.html.find(class_=imageUrlFinder).find_all("li")
            self.imageList = []
            for _ in self.imageUrlFinder:
                if _.find("img").get("data-lazy"):
                    self.imageList.append(_.find("img").get("data-lazy"))
                else:
                    self.imageList.append(_.find("img").get("src")) 
        except:
            self.imageList = []
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
                        DataParserClass.data[index_]["consumption"] =self.consumption
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
        item_info = WebDriverWait(scrapeURL.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "lg-info")))
        scrapeURL.dataParser(html = scrapeURL.driver.page_source,
                           itemUrl = item_url, 
                           stockStatus = "r-cell",
                           localNameFinder = "lg-info",
                           managementNumber="r-cell",
                           titleFinder = "item_detail",
                           descriptionFinder = "item-description",
                           priceFinder = "price",
                           shipMethod = "r-cell",
                           capacityFinder = "r-cell",
                           consumption = "r-cell",
                           compName="r-cell",
                           imageUrlFinder = "slick-track" )
    except:
        scrapeURL.driver.quit()
        raise Exception (f"{threading.current_thread().name}) - Unable to load the element")
    scrapeURL.driver.quit()

def ItemLinkCollector(data):
    nxt_btn ="//*[@id='form_events']/section/div[2]/div[1]/div/div[2]/div[3]/ul/li[3]/a"
    element_container = "itemlist"
    url_category=data["URL"]
    category=data["category"]
    scrapeURL = ListParserClass(url_category)
    scrapeURL.driver.get(scrapeURL.url)
    logging.info(f"{threading.current_thread().name}) -Scraping([{category}]{url_category})")
    while True:
        try:
            time.sleep(1)
            itemlist = WebDriverWait(scrapeURL.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, element_container)))
            scrapeURL.listParser(html =scrapeURL.driver.page_source, elementContainer = element_container)
            try:
                nextButton = scrapeURL.driver.find_element_by_xpath(nxt_btn)
                nextButton.send_keys(Keys.ENTER)
                logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Next_Page({category}) -Scraped_categories({ListParserClass.totalList}/{len(ScraperCategory.categoryList)})")
            except NoSuchElementException:
                logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category}) -Scraped_categories({ListParserClass.totalList}/{len(ScraperCategory.categoryList)})")
                with data_lock:
                    for _ in scrapeURL.itemList:
                        DataParserClass.data.append({"URL":_,"category":category})
                    logging.info(f"{threading.current_thread().name}) -Adding_items({len(scrapeURL.itemList)})  - Total_item({len(DataParserClass.data)})")
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
    site.categoryParser(html= site.driver.page_source, elementTag = "popover")
    data=site.categoryList
    data=[{"URL":"https://furu-po.com/goods_list/152","category":"test:"}]
    #{"URL":"https://furu-po.com/goods_list/166/168","category":"test2"}]
    site.driver.quit()
    final = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds for fetching {len(data)} categories")
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8 , thread_name_prefix='Scraper') as executor:
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