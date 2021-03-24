"""

Site : Furusato Honpo	
Link : https://furusatohonpo.jp/

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
import os

""" This section declares all the variables used """
LINK = "https://furusatohonpo.jp"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s](%(levelname)s@%(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)

data_lock = threading.Lock()

class ScraperCategory(WebDriver):
    categoryList = []

    def __init__(self, url):
        self.url = url
        super().__init__(url)

    def categoryParser(self,**kwargs):
        self.elementCat = kwargs.get("elementCat")
        self.html = kwargs.get("html")
        ScraperCategory.categoryList.append({"URL":self.html,"category":self.elementCat})

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
        self.container = self.html.find(class_="gifts")
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
        self.compName =  "NA"        
        self.capacityFinder =  "NA"
        self.shipMethod =  "NA"
        self.stockStatus =  "NA"
        self.localNameFinder =  "NA"
        self.titleFinder = "NA"
        self.descriptionFinder = "NA"
        self.priceFinder = "NA"
        self.imageList = "NA"
        self.categoryFinder = "NA"
        self.stockStatus =  "NA"


    def dataParser(self,html,itemUrl,categoryFinder,localNameFinder,titleFinder,descriptionFinder,priceFinder,shipMethod,capacityFinder,compName,imageUrlFinder):
        self.html = bs(html, 'html.parser')
        try:
            self.categoryFinder = self.html.find(class_=categoryFinder).find_all("li")
            self.categoryFinder = self.categoryFinder[-2].find("a").get_text()
            self.categoryFinder =  re.sub(r'\W+', '', self.categoryFinder)
            self.categoryFinder =  re.sub(r'のふるさと納税一覧', '', self.categoryFinder)
        except:
             self.categoryFinder = "NA"

        self.about = self.html.find(class_="p-detailInfo")
        self.about = self.about.find_all("tr")
        for _ in self.about:
            self.th = _.find("th").get_text()
            self.th = re.sub(r'\W+', '', self.th)
            if re.match("配送方法",self.th):
                try:
                    self.shipMethod = _.find(shipMethod).get_text()
                    self.shipMethod = re.sub(r'\W+', '', self.shipMethod)
                except:
                    self.shipMethod = "NA"
            if re.match("事業者名",self.th):
                try:
                    self.compName = _.find(compName).get_text()
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
            self.localNameFinder = "NA"
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
            self.priceFinder = self.html.find(class_=priceFinder).find("span").get_text()
            self.priceFinder = re.sub(r'\W+', '', self.priceFinder)
        except:
            raise Exception ("Unable to locate the priceFinder")
        try:
            self.capacityFinder = self.html.find(class_=capacityFinder).get_text()
            self.capacityFinder = self.html.find(class_=capacityFinder).find("span").get_text()
            self.capacityFinder = re.sub(r'\W+', '', self.capacityFinder)
        except:
            self.capacityFinder = "NA"
        try:
            self.imageUrlFinder = self.html.find(class_=imageUrlFinder).find_all("div", {"class":"p-detailMv__mainItem"})
            self.imageList = []
            for _ in self.imageUrlFinder:
                self.holder = _.find("div").get("style")
                self.holder = self.holder.split('"')
                self.imageList.append(self.holder[1])      
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
        scrapeURL.dataParser(html = scrapeURL.driver.page_source,
                           itemUrl = item_url,
                           categoryFinder = "c-contents", 
                           localNameFinder = "p-detailName__municipality",
                           titleFinder = "p-detailName__ttl",
                           descriptionFinder = "p-detailDescription__txt",
                           priceFinder = "p-detailName__price",
                           shipMethod = "td",
                           capacityFinder = "p-detailAddCart__ttl",
                           compName = "td",
                           imageUrlFinder = "slick-track")
    except:
        scrapeURL.driver.quit()
        raise Exception (f"{threading.current_thread().name}) - Unable to load the element")
    scrapeURL.driver.quit()

def ItemLinkCollector(data):
    nxt_btn ="c-pagination"
    element_container = "c-itemList"
    url_category=data["URL"]
    category=data["category"]
    scrapeURL = ListParserClass(url_category)
    scrapeURL.driver.get(scrapeURL.url)
    logging.info(f"{threading.current_thread().name}) -Scraping([{category}]{url_category})")
    while True:
        try:
            time.sleep(1)
            itemlist = WebDriverWait(scrapeURL.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, element_container)))
            scrapeURL.listParser(html =scrapeURL.driver.page_source, elementContainer = element_container)
            try:
                nextButton = scrapeURL.driver.find_element_by_class_name(nxt_btn)
                nextButton = nextButton.find_element_by_class_name("c-pagination__next")
                nextButton.send_keys(Keys.ENTER)

                logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Next_Page({category})")
            except NoSuchElementException:
                logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category})")
                with data_lock:
                    for _ in scrapeURL.itemList:
                        DataParserClass.data.append({"URL":LINK+_,"category":category})
                    logging.info(f"{threading.current_thread().name}) -Adding_items({len(scrapeURL.itemList)})  -Total_item({len(DataParserClass.data)})")
                break
        except:
            scrapeURL.driver.quit()
            raise Exception (f"{threading.current_thread().name}) -Unable to load the element")
            break
    scrapeURL.driver.quit()



start = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Scraping has been started...")
site=ScraperCategory("https://furusatohonpo.jp/donate/s/?")
site.categoryParser(0)
data=site.categoryList
site.driver.quit()
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} for fetching {len(data)} categories")
# data=[{"URL":"https://furusatohonpo.jp/donate/s/?categories=18","category":"test"}]
# {"URL":"https://furusatohonpo.jp/donate/s/?categories=1601","category":"test2"}]
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

# start = time.perf_counter()
# site_name = os.path.basename(__file__).split(".")[0]
# cwd = os.getcwd()
# save_data = SaveData()
# for data_dict in DataParserClass.data:
#     for image_link in data_dict["images"]:
#         save_data.save_img(cwd,site_name,data_dict["category"],data_dict["title"],image_link)
#     # save_data.query_db(data_dict)
# final = time.perf_counter()
# logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  scrape  {len(DataParserClass.data)} items images")

