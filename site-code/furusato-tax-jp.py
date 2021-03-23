"""

Site : Hometown Choice	
Link : https://www.furusato-tax.jp/

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
import requests
import shutil
import os 
from PIL import Image

import mysql.connector as connect
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
        self.consumption ="NA"
        self.appDeadline ="NA"  

    def dataParser(self,html,itemUrl,stockStatus,categoryFinder,localNameFinder,managementNumber,appDeadline,titleFinder,descriptionFinder,priceFinder,
                   shipMethod,capacityFinder,consumption,compName,imageUrlFinder):
        self.html = bs(html, 'html.parser')
        self.info = self.html.find_all(class_="basicinfo_pay")
        self.th = self.info[0].find_all("th")
        self.td = self.info[0].find_all("td")
        for _ in self.th:
            self.dt_ = _.get_text()
            if re.match("容量",self.dt_):
                try:
                    self.capacityFinder = self.td[self.th.index(_)].get_text()
                    self.capacityFinder = self.capacityFinder.replace("/n","")
                    self.capacityFinder = self.capacityFinder.replace("/t","")
                except:
                    self.capacityFinder = "NA"
            if re.match("自治体での管理番号",self.dt_):
                try:
                    self.managementNumber = self.td[self.th.index(_)].get_text()
                    self.managementNumber = self.managementNumber.replace("/n","")
                    self.managementNumber = self.managementNumber.replace("/t","")
                except:
                    self.managementNumber =  "NA"
            if re.match("事業者",self.dt_):
                try:
                    self.compName =self.td[self.th.index(_)].get_text()
                    self.compName = self.compName.replace("/n","")
                    self.compName = self.compName.replace("/t","")
                except:
                    self.compName = "NA"
            if re.match("消費期限",self.dt_):
                try:
                    self.consumption = self.td[self.th.index(_)].get_text()
                    self.consumption = self.consumption.replace("/n","")
                    self.consumption = self.consumption.replace("/t","")
                except:
                    self.consumption = "NA"
        self.th = self.info[1].find_all("th")
        self.td = self.info[1].find_all("td")
        for _ in self.th:
            self.dt_ = _.get_text()
            if re.match("配送",self.dt_): 
                try:
                    self.shipMethod = self.td[self.th.index(_)].get_text()
                    self.shipMethod = self.shipMethod.replace("/n","")
                    self.shipMethod = self.shipMethod.replace("/t","")
                except:
                    self.shipMethod = "NA"            
            if re.match("申込期日",self.dt_): 
                try:
                    self.appDeadline = self.td[self.th.index(_)].get_text()
                    self.appDeadline = self.appDeadline.replace("/n","")
                    self.appDeadline = self.appDeadline.replace("/t","")
                except:
                    self.appDeadline = "NA"

        try:
            self.stockStatus = self.html.find(class_=stockStatus).find("span").get_text()
            self.stockStatus = self.stockStatus.replace("/n","")
            self.stockStatus = self.stockStatus.replace("/t","")
        except:
            self.stockStatus =  "NA"
        try:
            self.localNameFinder = self.html.find(class_=localNameFinder).get_text()
            self.localNameFinder = self.localNameFinder.replace("/n","")
            self.localNameFinder = self.localNameFinder.replace("/t","")
        except:
            self.localNameFinder =  "NA"
          
        try:
            self.titleFinder = self.html.find(class_=titleFinder).get_text()
            self.titleFinder = self.titleFinder.replace("/n","")
            self.titleFinder = self.titleFinder.replace("/t","")
        except:
            self.titleFinder = "NA"
        try:
            self.descriptionFinder = self.html.find(class_=descriptionFinder).get_text()
            self.descriptionFinder = self.descriptionFinder.replace("/n","")
            self.descriptionFinder = self.descriptionFinder.replace("/t","")
        except:
            self.descriptionFinder = "NA"
        try:
            self.priceFinder = self.html.find(class_=priceFinder).get_text()
            self.priceFinder = re.sub(r'\W+', '', self.priceFinder)
            self.priceFinder = self.priceFinder.replace("寄付金額","")
            self.priceFinder = self.priceFinder.replace("円以上の寄付でもらえる","")
            self.priceFinder = int(self.priceFinder.replace(",",""))  
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
        time.sleep(1)
        item_info = WebDriverWait(scrapeURL.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "city-title")))
        scrapeURL.dataParser(html = scrapeURL.driver.page_source,
                           itemUrl = item_url,
                           stockStatus = "stock", 
                           categoryFinder = "NA",
                           localNameFinder = "city-title",
                           managementNumber = "NA",
                           appDeadline = "NA",
                           titleFinder = "ttl-h1__text",
                           descriptionFinder = "overview",
                           shipMethod = "NA",
                           priceFinder = "basicinfo_price",
                           capacityFinder = "NA",
                           consumption = "NA",
                           compName = "NA",
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
    site.categoryParser(html= site.driver.page_source, elementTag = "nv-select-categories")
    data=site.categoryList

    data=[{'URL':'https://www.furusato-tax.jp/search/154?disabled_category_top=1&target=1','category':'感謝状等'}]
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
    img_dir_list = []
    agt_cd = "FCH"
    mydb = connect.connect(host="localhost",user="user",password="password",database="his_furusato")
    mycursor = mydb.cursor()
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
        for img_link in datum["images"]:
            response = requests.get(img_link, stream=True)
            dir_name= os.path.join(cwd,"scraper",site_name,datum["category"],datum["title"])
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            img_link = img_link.split("/")
            dir_file = os.path.join(dir_name,img_link[-1])
            with open(dir_file, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
            img_dir_list.append(dir_file)        
        for  img in img_dir_list[:5]:
            mycursor.execute("UPDATE  t_agt_mchan SET mchan_img_url%s = %s  WHERE agt_mchan_url = %s",(img_dir_list.index(img)+1,img,datum["URL"]))
            mydb.commit()
        img_dir_list = []
    final = time.perf_counter()
    logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  save  {len(DataParserClass.data)} items data")