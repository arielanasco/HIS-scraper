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
import requests
import shutil
import os 
from PIL import Image

import mysql.connector as connect
""" This section declares all the variables used """
LINK = "https://furu-po.com/"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s](%(levelname)s@%(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)

data_lock = threading.Lock()

class ScraperCategory(WebDriver):
    categoryList = []
    sub_categoryList = []

    def __init__(self, url):
        self.url = url
        super().__init__(url)

    def categoryParser(self,**kwargs):
        self.driver.get(self.url)
        self.elementTag = kwargs.get("elementTag")
        self.html = bs(self.driver.page_source, 'html.parser')
        self.category = self.html.find(class_=self.elementTag)
        self.liTag_ = self.category.li
        while True:
            self.liTag = self.liTag_.find_all("li")
            self.parent =  re.sub(r'\([^()]*\)', '', self.liTag_.find("a").get_text())    
            for _ in self.liTag:
                self.categoryData = re.sub(r'\([^()]*\)', '', _.find("a").get_text())
                ScraperCategory.categoryList.append({"URL":_.find("a").get("href"),"category":self.parent+"_"+self.categoryData})
            if self.liTag_.find_next_sibling():
                self.liTag_ = self.liTag_.find_next_sibling()
            else:
                break
        for item in self.categoryList:
            self.driver.get(item["URL"])
            self.html = bs(self.driver.page_source, 'html.parser')
            try:
                self.sub_category = self.html.find(class_="subcategory").find_all("option")
                for _ in self.sub_category[1:]:
                    ScraperCategory.sub_categoryList.append({"URL":"https://furu-po.com/"+_.get("value"),"category":item["category"]+"_"+_.get_text()})
            except:
                ScraperCategory.sub_categoryList.append(item)
                    

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
        self.priceFinder = 0
        self.imageList = "NA"
        self.consumption = "NA"
        self.appDeadline = "NA"

    def dataParser(self,html,itemUrl,stockStatus,categoryFinder,localNameFinder,managementNumber,appDeadline,titleFinder,descriptionFinder,priceFinder,
                   shipMethod,capacityFinder,consumption,compName,imageUrlFinder):
        self.html = bs(html, 'html.parser')
        self.lcell = self.html.find_all(class_="l-cell")
        self.rcell = self.html.find_all(class_="r-cell")
        for _ in self.lcell:
            self.dt_ = _.get_text()
            if re.match("配送方法",self.dt_):
                try:
                    self.shipMethod = self.rcell[self.lcell.index(_)].get_text()
                    self.shipMethod = re.sub('\s+', '', self.shipMethod)
                except:
                    self.shipMethod = "NA" 
            if re.match("容量",self.dt_):
                try:
                    self.capacityFinder = self.rcell[self.lcell.index(_)].get_text()
                    self.capacityFinder = re.sub('\s+', '', self.capacityFinder)
                except:
                    self.capacityFinder = "NA" 
            if re.match("賞味期限",self.dt_):
                try:
                    self.consumption = self.rcell[self.lcell.index(_)].get_text()
                    self.capacityFinder = re.sub('\s+', '', self.consumption)
                except:
                    self.consumption = "NA" 
            if re.match("管理番号",self.dt_):
                try:
                    self.managementNumber = self.rcell[self.lcell.index(_)].get_text()
                    self.managementNumber = re.sub('\s+', '', self.managementNumber)
                except:
                    self.managementNumber = "NA" 
            if re.match("事業者名",self.dt_):
                try:
                    self.compName = self.rcell[self.lcell.index(_)].get_text()
                    self.compName = re.sub('\s+', '', self.compName)
                except:
                    self.compName = "NA" 

        try:
            self.stockStatus = self.html.find(class_=stockStatus).find("span").get_text()
        except:
            self.stockStatus =  "NA"
        try:
            self.localNameFinder = self.html.find(class_=localNameFinder)
            self.localNameFinder = self.localNameFinder.find_all(class_="icon")
            self.localNameFinder = self.localNameFinder[1].get_text()
            self.localNameFinder = re.sub('\s+', '', self.localNameFinder)
        except:
            self.localNameFinder =  "NA"

        try:
            self.titleFinder = self.html.find(class_=titleFinder).find("h1").get_text()
            self.titleFinder = re.sub('\s+', '', self.titleFinder)
        except:
            self.titleFinder = "NA"

        try:
            self.descriptionFinder = self.html.find(class_=descriptionFinder).get_text()
            self.descriptionFinder = re.sub('\s+', '', self.descriptionFinder)
        except:
            self.descriptionFinder = "NA"
        try:
            self.priceFinder = self.html.find(class_=priceFinder).get_text()
            self.priceFinder = self.priceFinder.replace("円","")
            self.priceFinder = int(self.priceFinder.replace(",",""))        
        except:
            self.priceFinder = 0
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
    scrapeURL.driver.get(scrapeURL.url)
    logging.info(f"{threading.current_thread().name}) -Scraped_items({DataParserClass.totalData}/{len(DataParserClass.data)}) -Fetching({item_url})")
    try:
        item_info = WebDriverWait(scrapeURL.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "lg-info")))
        scrapeURL.dataParser(html = scrapeURL.driver.page_source,
                           itemUrl = item_url, 
                           stockStatus = "NA",
                           categoryFinder = "NA", 
                           localNameFinder = "lg-info",
                           managementNumber="NA",
                           appDeadline = "NA",
                           titleFinder = "item_detail",
                           descriptionFinder = "item-description",
                           priceFinder = "price",
                           shipMethod = "NA",
                           capacityFinder = "NA",
                           consumption = "NA",
                           compName="NA",
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
            itemlist = WebDriverWait(scrapeURL.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, element_container)))
            scrapeURL.listParser(html =scrapeURL.driver.page_source, elementContainer = element_container)
            try:
                nextButton = scrapeURL.driver.find_element_by_xpath(nxt_btn)
                nextButton.send_keys(Keys.ENTER)
                logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Next_Page({category}) -Scraped_categories({ListParserClass.totalList}/{len(ScraperCategory.categoryList)})")
            except NoSuchElementException:
                logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category}) -Scraped_categories({ListParserClass.totalList}/{len(ScraperCategory.categoryList)})")
                with data_lock:
                    for _ in scrapeURL.itemList:
                        DataParserClass.data.append({"URL":_,
                                                 "category":category,
                                                 "stock_status": "NA",
                                                 "local_name" : "NA",
                                                 "management_number" :"NA",
                                                 "app_deadline": "NA",
                                                 "title" : "NA",
                                                 "description": "NA",
                                                 "price" : 0,
                                                 "ship_method": "NA",
                                                 "capacity" :"NA",
                                                 "consumption": "NA",
                                                 "comp_name" : "NA",
                                                 "images" : "NA"
                                                 })
                    logging.info(f"{threading.current_thread().name}) -Adding_items({len(scrapeURL.itemList)})  - Total_item({len(DataParserClass.data)})")
                break
        except:
            scrapeURL.driver.quit()
            raise Exception (f"{threading.current_thread().name}) -Unable to load the element")
            break
    scrapeURL.driver.quit()

start = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Scraping has been started...")
site=ScraperCategory(LINK)
site.categoryParser(elementTag = "popover")
site.driver.quit()
data = site.sub_categoryList
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds for fetching {len(data)} categories")

data=[data[0]]
start = time.perf_counter()
with concurrent.futures.ThreadPoolExecutor(max_workers=5 , thread_name_prefix='Scraper') as executor:
    futures = [executor.submit(ItemLinkCollector, datum) for datum in data]
    for future in concurrent.futures.as_completed(futures):
        if future.result():
            logging.info(f"{threading.current_thread().name}) -{future.result()}")
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  fetch  {len(DataParserClass.data)} items URL")

start = time.perf_counter()
with concurrent.futures.ThreadPoolExecutor(max_workers=5,thread_name_prefix='Fetching_Item_Data') as executor:
    futures = [executor.submit(DataCollectorFunction, data) for data in DataParserClass.data]
    for future in concurrent.futures.as_completed(futures):
        if future.result():
            logging.info(f"{threading.current_thread().name}) -{future.result()}")
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  scrape  {len(DataParserClass.data)} items data")

start = time.perf_counter()
site_name = os.path.basename(__file__).split(".")[0]
cwd = os.getcwd()
agt_cd = "JTB"
mydb = connect.connect(host="localhost",user="user",password="password",database="his_furusato")
mycursor = mydb.cursor()

for  datum in data:
    mycursor.execute("INSERT INTO m_agt_catgy (agt_catgy_url,agt_catgy_nm,agt_cd)VALUES (%s,%s,%s)",(datum["URL"],datum["category"],agt_cd))
    mydb.commit()

for  datum in DataParserClass.data:
    try:
        mycursor.execute("INSERT INTO t_agt_mchan (agt_mchan_url,agt_city_nm,agt_mchan_cd,mchan_nm,mchan_desc,appli_dline,price,capacity,mchan_co,agt_cd) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (datum["URL"],datum["local_name"],datum["management_number"],datum["title"],datum["description"],datum["app_deadline"],datum["price"],datum["capacity"],datum["comp_name"][:30],agt_cd))
        mydb.commit()
        if type(datum["category"]) == list:
            for cat in datum["category"][:8]:
                mycursor.execute("UPDATE  t_agt_mchan SET agt_catgy_nm%s = %s  WHERE agt_mchan_url = %s",(datum['category'].index(cat)+1,cat,datum["URL"]))
                mydb.commit()
        else:
            mycursor.execute("UPDATE  t_agt_mchan SET agt_catgy_nm1 = %s WHERE agt_mchan_url = %s",(datum["category"],datum["URL"]))
            mydb.commit()       
        for  img in datum["images"][:5]:
            mycursor.execute("UPDATE  t_agt_mchan SET mchan_img_url%s = %s  WHERE agt_mchan_url = %s",(datum["images"].index(img)+1,img,datum["URL"]))
            mydb.commit()
    except:
        logging.info(f"{threading.current_thread().name}) -Data failed to be saved...{datum['URL']}")
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  save  {len(DataParserClass.data)} items data")
