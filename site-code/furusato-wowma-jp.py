"""

Site : au PAY Hometown tax payment	
Link : https://furusato.wowma.jp/

"""
from web_driver import WebDriver
import web_driver_1
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
        self.driver.get(self.url)
        self.elementTag = kwargs.get("elementTag")
        self.html = bs(self.driver.page_source, 'html.parser')
        self.category = self.html.find(class_=self.elementTag)
        self.category = self.category.ul
        self.liTag = self.category.li
        self.liTag = self.liTag.find_next_sibling()
        while True:
            self.parent_category = self.liTag.find("label").find("span").get_text()
            self.parent_category_id = self.liTag.find("input").get("value")
            self.child_categories = self.liTag.find(class_="category-child").find_all("li")
            for _ in self.child_categories:
                self.child_category_id = _.find("input").get("value")
                self.child_category_name = _.find("label").get_text()
                self.child_category_name =re.sub(r'\([^()]*\)','',self.child_category_name)
                ScraperCategory.categoryList.append({"URL":f"https://furusato.wowma.jp/products/list.php?parent_category={self.parent_category_id}&category_{self.child_category_id}={self.child_category_id}","category":f"{self.parent_category}_{self.child_category_name}"})
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
        self.container = self.html.find(class_="category-sort-contents")
        self.container = self.container.find(class_=self.elementContainer)
        self.ChildElement = self.container.find_all(class_="contents-detail")
        for _ in self.ChildElement:
            self.itemList.append(_.find(class_="item-list").get("href"))

class DataParserClass(web_driver_1.WebDriver):

    isNotActive = True
    data = []
    totalData = 0
    seen = set()

    def __init__(self, url):
        self.url = url
        type(self).totalData +=1
        super().__init__()
        self.categoryFinder =  []       
        self.managementNumber =  "NA"        
        self.compName =  "NA"        
        self.capacityFinder =  "NA"
        self.shipMethod =  "NA"
        self.stockStatus =  "NA"
        self.localNameFinder =  "NA"
        self.titleFinder = "NA"
        self.descriptionFinder = "NA"
        self.priceFinder = 0
        self.imageList = []
        self.consumption = "NA"
        self.appDeadline ="NA"

    def dataParser(self,html,itemUrl,stockStatus,categoryFinder,localNameFinder,managementNumber,appDeadline,titleFinder,descriptionFinder,priceFinder,
                   shipMethod,capacityFinder,consumption,compName,imageUrlFinder):
        self.html = bs(html, 'html.parser')
        self.table = self.html.find(class_="gift-detail")
        self.dt = self.table.find_all("dt")
        self.dd = self.table.find_all("dd")
        for _ in self.dt:
            self.dt_ = _.get_text()
            if re.match("申込受付期間",self.dt_): 
                try:
                    self.appDeadline = self.dd[self.dt.index(_)].get_text()
                    self.appDeadline =  re.sub('\s+', '', self.appDeadline)

                except:
                    self.appDeadline = "NA" 
            if re.match("内容量",self.dt_): 
                try:
                    self.capacityFinder = self.dd[self.dt.index(_)].get_text()
                    self.capacityFinder =  re.sub('\s+', '', self.capacityFinder)
                except:
                    self.capacityFinder = "NA"
            if re.match("配送方法",self.dt_): 
                try:
                    self.shipMethod = self.dd[self.dt.index(_)].get_text()
                    self.shipMethod =  re.sub('\s+', '', self.shipMethod)
                except:
                    self.shipMethod = "NA" 
            if re.match("提供者",self.dt_):
                try:
                    self.compName = self.dd[self.dt.index(_)].get_text()
                    self.compName =  re.sub('\s+', '', self.compName)
                except:
                    self.compName = "NA"
            if re.match("消費期限/賞味期限",self.dt_): 
                try:
                    self.consumption = self.dd[self.dt.index(_)].get_text()
                    self.consumption =  re.sub('\s+', '', self.consumption)
                except:
                    self.consumption = "NA"
            
        try:
            self.categoryFinder = self.html.find(class_=categoryFinder).find_all("ul")
            self.multiple_category = []
            for _ in self.categoryFinder:
                self.liTag = _.find_all("li")
                self.categoryFinder = self.liTag[-2].find("a").get_text()
                self.multiple_category.append(self.categoryFinder)
        except:
            self.multiple_category =  []

        try:
            self.localNameFinder = self.html.find(class_=localNameFinder).get_text()
            self.localNameFinder =  re.sub('\s+', '', self.localNameFinder)
        except:
            self.localNameFinder = "NA"
        try:
            self.titleFinder = self.html.find(class_=titleFinder).find_all("li")
            self.titleFinder = self.titleFinder[-1].get_text()
            self.titleFinder =  re.sub('\s+', '', self.titleFinder)
        except:
            self.titleFinder = "NA"

        self.item_info = self.html.find_all(class_="gift-comment")

        try:
            self.descriptionFinder = self.item_info[0].get_text()
            self.descriptionFinder =  re.sub('\s+', '', self.descriptionFinder)
        except:
            self.descriptionFinder = "NA"

        try:
            self.managementNumber = self.item_info[1].get_text()
            self.loc = self.managementNumber.index("商品コード:")
            self.managementNumber = self.managementNumber[self.loc+len("#商品コード:"):self.loc+15]
            self.managementNumber =  re.sub('\s+', '', self.managementNumber)

        except:
            self.managementNumber =  "NA"

        try:
            self.priceFinder = self.html.find(id=priceFinder).get_text()
            self.priceFinder = self.priceFinder.replace("円","")
            self.priceFinder = int(self.priceFinder.replace(",",""))
        except:
            self.priceFinder = 0

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
                    if itemUrl == data["URL"]:
                        index_ = DataParserClass.data.index(data)
                        DataParserClass.data[index_]["category"] =self.multiple_category
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
                           categoryFinder = "breadcrumb", 
                           localNameFinder = "municipality-name",
                           managementNumber="NA",
                           appDeadline = "NA",
                           titleFinder = "breadcrumb",
                           descriptionFinder = "gift-comment",
                           shipMethod="NA",
                           priceFinder = "gift-money-contents",
                           capacityFinder = "slider-txt",
                           consumption = "NA",
                           compName ="NA",
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
        itemlist = WebDriverWait(scrapeURL.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, element_container)))
        scrapeURL.listParser(html =scrapeURL.driver.page_source, elementContainer = element_container)
        nextButton = scrapeURL.driver.find_element_by_class_name(nxt_btn)
        if nextButton.get_attribute("href") == 'javascript:void(0);':
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category}) -Scraped_categories({ListParserClass.totalList}/{len(ScraperCategory.categoryList)})")
            with data_lock:
                for _ in scrapeURL.itemList:
                    key = LINK+_
                    if key not in DataParserClass.seen:
                        DataParserClass.data.append({"URL":LINK+_,"category":category})
                        DataParserClass.seen.add(key)
                logging.info(f"{threading.current_thread().name}) -Adding_items({len(scrapeURL.itemList)})  -Total_item({len(DataParserClass.data)})")
            break
        else:
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Next_Page({category}) -Scraped_categories({ListParserClass.totalList}/{len(ScraperCategory.categoryList)})")
            nextButton.click()
    scrapeURL.driver.quit()

start = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Scraping has been started...")
site=ScraperCategory("https://furusato.wowma.jp/products/list.php")
site.categoryParser(elementTag = "list-contents")
data=site.categoryList
site.driver.quit()
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds for fetching {len(data)} categories")

data=[data[0]]
start = time.perf_counter()
with concurrent.futures.ThreadPoolExecutor(max_workers=5 , thread_name_prefix='Fetching_URL') as executor:
    futures = [executor.submit(ItemLinkCollector, datum) for datum in data]
    for future in concurrent.futures.as_completed(futures):
        if future.result():
            logging.info(f"{threading.current_thread().name}) -{future.result()}")
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  fetch  {len(DataParserClass.data)} items URL")

start = time.perf_counter()
with concurrent.futures.ThreadPoolExecutor(max_workers=5, thread_name_prefix='Fetching_Item_Data') as executor:
    futures = [executor.submit(DataCollectorFunction, data) for data in DataParserClass.data]
    for future in concurrent.futures.as_completed(futures):
        if future.result():
            logging.info(f"{threading.current_thread().name}) -{future.result()}")
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  scrape  {len(DataParserClass.data)} items data")

start = time.perf_counter()
site_name = os.path.basename(__file__).split(".")[0]
cwd = os.getcwd()
img_dir_list = []
agt_cd = "AUP"
mydb = connect.connect(host="localhost",user="user",password="password",database="his_furusato")
mycursor = mydb.cursor()

for  datum in data:
    mycursor.execute("INSERT INTO m_agt_catgy (agt_catgy_url,agt_catgy_nm,agt_cd)VALUES (%s,%s,%s)",(datum["URL"],datum["category"],agt_cd))
    mydb.commit()

for  datum in DataParserClass.data:
    mycursor.execute("INSERT INTO t_agt_mchan (agt_mchan_url,agt_city_nm,agt_mchan_cd,mchan_nm,mchan_desc,appli_dline,price,capacity,mchan_co,agt_cd) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
    (datum["URL"],datum["local_name"],datum["management_number"],datum["title"],datum["description"],datum["app_deadline"],datum["price"],datum["capacity"],datum["comp_name"],agt_cd))
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
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  save  {len(DataParserClass.data)} items data")
