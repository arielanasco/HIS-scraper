"""

Site : Hometown pallet	
Link : https://tokyu-furusato.jp/

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
LINK = "https://tokyu-furusato.jp/goods/result"

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
        self.category_container = self.html.find(class_=self.elementTag)
        self.liTag = self.category_container.li
        while True:
            self.subcat = self.liTag.find_all("li")
            for _ in self.subcat:
                self.categoryData = re.sub(r"\([0-9]+\)", "", _.find("span").get_text())
                self.categoryData = re.sub(r'\W+', '', self.categoryData)
                self.link = _.find("input").get("value")
                ScraperCategory.categoryList.append({"URL":"https://tokyu-furusato.jp/goods/result?limit=&order=1&chk_sub_ctg%5B%5D="+self.link,"category":self.categoryData})
            if self.liTag.find_next_sibling():
                self.liTag = self.liTag.find_next_sibling()
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
        self.container = self.html.find(class_="section_search")
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
        self.itemList = []
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
        self.imageList = []
        self.consumption = "NA"
        self.appDeadline ="NA"

    def dataParser(self,html,itemUrl,stockStatus,categoryFinder,localNameFinder,managementNumber,appDeadline,titleFinder,descriptionFinder,priceFinder,
                   shipMethod,capacityFinder,consumption,compName,imageUrlFinder):
        self.html = bs(html, 'html.parser')
        self.about = self.html.find(class_="itembox-data")
        self.dt = self.about.find_all("dt")
        self.dd = self.about.find_all("dd")
        for _ in self.dt:
            self.dt_ = _.get_text()
            if re.match("内容",self.dt_): 
                try:
                    self.capacityFinder = self.dd[self.dt.index(_)].get_text()
                    # self.capacityFinder = re.sub(r'\s+', '', self.capacityFinder)
                except:
                    self.capacityFinder = "NA"
            if re.match("提供元",self.dt_): 
                try:
                    self.compName = self.dd[self.dt.index(_)].get_text()
                    # self.capacityFinder = re.sub(r'\s+', '', self.capacityFinder)
                except:
                    self.compName = "NA"
        try:
            self.guide = self.html.find(class_="guidelist")
            self.dt = self.guide.find_all("dt")
            self.dd = self.guide.find_all("dd")
            for _ in self.dt:
                self.dt_ = _.get_text()
                if re.match("内容",self.dt_): 
                    self.shipMethod = self.dd[self.dt.index(_)].get_text()
                    # self.capacityFinder = re.sub(r'\s+', '', self.capacityFinder)
        except:
            self.shipMethod = "NA"
        try:
            self.localNameFinder = self.html.find(class_=localNameFinder).find("em",{"class":"text_area"}).get_text()
            self.localNameFinder =  re.sub(r'\W+', '', self.localNameFinder)
        except:
            self.localNameFinder =  "NA"
        try:
            self.titleFinder = self.html.find(class_=titleFinder).find_all("li")
            self.titleFinder = re.sub(r'\W+', '', self.titleFinder[-1].get_text())
        except:
            self.titleFinder = "NA"
        try:
            self.descriptionFinder = self.html.find(class_=descriptionFinder).find("p").get_text()
            self.descriptionFinder = re.sub(r'\W+', '', self.descriptionFinder)
        except:
            self.descriptionFinder = "NA"
        try:
            self.priceFinder = self.html.find(class_=priceFinder).find("dd").get_text()
            self.priceFinder = re.sub(r'\W+', '', self.priceFinder)
        except:
            self.priceFinder = None
        try:
            self.imageUrlFinder = self.html.find(class_=imageUrlFinder).find_all("img")
            self.imageList = []
            for _ in self.imageUrlFinder:
                self.imageList.append(_.get("src"))      
        except:
            self.imageList = None
        with data_lock:
                for data in DataParserClass.data:
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
    scrapeURL = DataParserClass(item_url)
    logging.info(f"{threading.current_thread().name}) -Scraped_items({DataParserClass.totalData}/{len(DataParserClass.data)}) -Fetching({item_url})")
    try:
        time.sleep(3)
        scrapeURL.dataParser(html = scrapeURL.get(item_url).text,
                           itemUrl = item_url,
                           stockStatus ="NA",
                           categoryFinder = "NA", 
                           localNameFinder = "heading_page",
                           managementNumber="NA",
                           appDeadline = "NA",
                           titleFinder = "topicpath",
                           descriptionFinder = "section_block",
                           shipMethod="NA",
                           priceFinder = "itembox-price",
                           capacityFinder = "itembox-data",
                           consumption = "NA",
                           compName ="NA",
                           imageUrlFinder = "itembox-mainimage" )
    except:
        raise Exception (f"{threading.current_thread().name}) - Unable to load the element")



def ItemLinkCollector(data):
    nxt_btn_xpath = "//*[@id='top']/main/div[1]/ul/li[7]/a"
    nxt_btn_xpath1 ="//*[@id='top']/main/div[1]/ul/li[9]/a"
    element_container = "cards"
    url_category=data["URL"]
    category=data["category"]
    scrapeURL = ListParserClass(url_category)
    scrapeURL.driver.get(scrapeURL.url)
    logging.info(f"{threading.current_thread().name}) -Scraping([{category}]{url_category})")
    while True:
        time.sleep(1)
        itemlist = WebDriverWait(scrapeURL.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, element_container)))
        scrapeURL.listParser(html =scrapeURL.driver.page_source, elementContainer = element_container)
        try:
            lenPagination = scrapeURL.driver.find_element_by_xpath("//*[@id='top']/main/div[1]/ul")
            lenPagination = lenPagination.find_elements_by_class_name("pagination-item")
            nxtbtn = lenPagination[-1].find_element_by_class_name("pagination-link").get_attribute("href")
            if nxtbtn[-1] == "#":
                logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category}) -Scraped_categories({ListParserClass.totalList}/{len(ScraperCategory.categoryList)})")
                with data_lock:
                    for _ in scrapeURL.itemList:
                        DataParserClass.data.append({"URL":_,"category":category})
                    logging.info(f"{threading.current_thread().name}) -Adding_items({len(scrapeURL.itemList)})  -Total_item({len(DataParserClass.data)})")
                break
            else:
                logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Next_Page({category}) -Scraped_categories({ListParserClass.totalList}/{len(ScraperCategory.categoryList)})")
                lenPagination[-1].find_element_by_tag_name("a").send_keys(Keys.ENTER)
        except NoSuchElementException:
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category}) -Scraped_categories({ListParserClass.totalList}/{len(ScraperCategory.categoryList)})")
            with data_lock:
                for _ in scrapeURL.itemList:
                    DataParserClass.data.append({"URL":_,"category":category})
                logging.info(f"{threading.current_thread().name}) -Adding_items({len(scrapeURL.itemList)})  -Total_item({len(DataParserClass.data)})")
            break
    scrapeURL.driver.quit()


if __name__ == '__main__':
    start = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Scraping for category has been started...")
    site=ScraperCategory(LINK)
    site.driver.get(site.url)
    current_url, user_agent = site.displaySiteInfo()
    logging.info(f"{threading.current_thread().name}) - {current_url} {user_agent}")
    site.categoryParser(html= site.driver.page_source, elementTag ="dropdownlist")
    data=site.categoryList
    data=[{'URL':'https://tokyu-furusato.jp/goods/result?limit=&order=1&chk_sub_ctg%5B%5D=82', 'category':'Testing'}
    # {'URL':'https://tokyu-furusato.jp/goods/result?limit=&order=1&chk_sub_ctg%5B%5D=76', 'category':'toiletries'}
    ]
    site.driver.quit()
    final = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  fetch  {len(data)} categories")
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