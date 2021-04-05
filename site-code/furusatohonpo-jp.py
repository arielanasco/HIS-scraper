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
import mysql.connector as connect

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
        self.driver.get(self.url)
        self.elementTag = kwargs.get("elementTag")
        self.html = bs(self.driver.page_source, 'html.parser')
        self.parent =  self.html.find(class_=self.elementTag)
        self.parent =  self.parent.find_all("li")

        for parent in self.parent:
            self.child = parent.find_all("li")
            self.parent_category = parent.find("a").get_text()
            for child in self.child:
                ScraperCategory.categoryList.append({"URL":"https://furusatohonpo.jp"+child.find("a").get("href"),"category":self.parent_category+"_"+child.get_text()})

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
        if self.container != None:
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
    seen = []

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
            self.categoryFinderChild = self.categoryFinder[-2].find("a").get_text()
            self.categoryFinderChild =  re.sub(r'のふるさと納税一覧', '', self.categoryFinderChild)
            self.categoryFinderParent = self.categoryFinder[-3].find("a").get_text()
            self.categoryFinderParent =  re.sub(r'のふるさと納税一覧', '', self.categoryFinderParent)
            self.categoryFinderChild =  re.sub(r'\W+', '', self.categoryFinderChild)
            self.categoryFinderParent =  re.sub(r'\W+', '', self.categoryFinderParent)
            self.categoryFinderLink = self.categoryFinder[-2].find("a").get("href")
            
            with data_lock:
                print(f"https://furusatohonpo.jp{str(self.categoryFinderLink)}   {self.categoryFinderParent}_{self.categoryFinder}")
                self.seen.append({"URL":"https://furusatohonpo.jp"+str(self.categoryFinderLink),"category":self.categoryFinderParent+"_"+self.categoryFinder})
            self.categoryFinder = self.categoryFinderParent+"_"+self.categoryFinder
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
            self.priceFinder = int(self.priceFinder)
        except:
            self.priceFinder = "NA"
        try:
            self.capacityFinder = self.html.find(class_=capacityFinder).get_text()
            self.capacityFinder = self.capacityFinder.replace(str(self.priceFinder)+" 円","")
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
        time.sleep(3)
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
                        DataParserClass.data.append({"URL":LINK+_,
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
site.categoryParser(elementTag="vue-footer-categories")
data=site.categoryList
site.driver.quit()
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} for fetching {len(data)} categories")

data=[data[20]]

start = time.perf_counter()
with concurrent.futures.ThreadPoolExecutor(max_workers=5 , thread_name_prefix='Fetching_URL') as executor:
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

agt_cd = "FHP"
mydb = connect.connect(host="localhost",user="user",password="password",database="his_furusato")
mycursor = mydb.cursor()


# for  datum in DataParserClass.seen:
#     mycursor.execute("INSERT INTO m_agt_catgy (agt_catgy_url,agt_catgy_nm,agt_cd)VALUES (%s,%s,%s)",(datum["URL"],datum["category"],agt_cd))
#     mydb.commit()

# for  datum in DataParserClass.data:
#     try:
#         mycursor.execute("INSERT INTO t_agt_mchan (agt_mchan_url,agt_city_nm,agt_mchan_cd,mchan_nm,mchan_desc,appli_dline,price,capacity,mchan_co,agt_cd) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
#         (datum["URL"],datum["local_name"],datum["management_number"],datum["title"],datum["description"],datum["app_deadline"],datum["price"],datum["capacity"],datum["comp_name"][:30],agt_cd))
#         mydb.commit()
#         if type(datum["category"]) == list:
#             for cat in datum["category"][:8]:
#                 mycursor.execute("UPDATE  t_agt_mchan SET agt_catgy_nm%s = %s  WHERE agt_mchan_url = %s",(datum['category'].index(cat)+1,cat,datum["URL"]))
#                 mydb.commit()
#         else:
#             mycursor.execute("UPDATE  t_agt_mchan SET agt_catgy_nm1 = %s WHERE agt_mchan_url = %s",(datum["category"],datum["URL"]))
#             mydb.commit()       
#         for  img in datum["images"][:5]:
#             mycursor.execute("UPDATE  t_agt_mchan SET mchan_img_url%s = %s  WHERE agt_mchan_url = %s",(datum["images"].index(img)+1,img,datum["URL"]))
#             mydb.commit()
#     except:
#         logging.info(f"{threading.current_thread().name}) -Data failed to be saved...{datum['URL']}")
# final = time.perf_counter()
# logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  save  {len(DataParserClass.data)} items data")

