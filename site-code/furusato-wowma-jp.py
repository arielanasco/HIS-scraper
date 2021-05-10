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
import re
import  concurrent.futures
from bs4 import BeautifulSoup as bs
from datetime import datetime
import mysql.connector as connect
import os 
""" This section declares all the variables used """
LINK = "https://furusato.wowma.jp"
date = datetime.now().strftime("%Y%m%d")
script_name = os.path.splitext(os.path.basename(__file__))[0]

logging.basicConfig(filename=f"/home/ec2-user/prj_his_furusato_scrape/logs/{script_name}_{date}.log",filemode='a',level=logging.INFO, format='[%(asctime)s](%(levelname)s@%(message)s', datefmt='%d-%b-%y %H:%M:%S')


data_lock = threading.Lock()

class ScraperCategory(WebDriver):
    category_list = []

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
                ScraperCategory.category_list.append({"URL":f"https://furusato.wowma.jp/products/list.php?parent_category={self.parent_category_id}&category_{self.child_category_id}={self.child_category_id}","category":f"{self.parent_category}_{self.child_category_name}"})
            if self.liTag.find_next_sibling():
                self.liTag = self.liTag.find_next_sibling()
            else:
                break

class ListParserClass(WebDriver):
    total_list = 0

    def __init__(self, url):
        self.url = url
        type(self).total_list +=1
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
    data = []
    total_data = 0
    seen = set()

    def __init__(self, url):
        self.url = url
        type(self).total_data +=1
        super().__init__()
        self.categoryFinder =  []       
        self.managementNumber =  None        
        self.compName =  None        
        self.capacityFinder =  None
        self.shipMethod =  None
        self.stockStatus =  None
        self.localNameFinder =  None
        self.titleFinder = None
        self.descriptionFinder = None
        self.priceFinder = None
        self.imageList = []
        self.consumption = None
        self.appDeadline =None

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
                    # self.appDeadline =  re.sub('\s+', '', self.appDeadline)
                    if self.appDeadline == " ":
                        self.appDeadline = None
                except:
                    self.appDeadline = None 
            if re.match("内容量",self.dt_): 
                try:
                    self.capacityFinder = self.dd[self.dt.index(_)].get_text()
                    # self.capacityFinder =  re.sub('\s+', '', self.capacityFinder)
                    if self.capacityFinder == " ":
                        self.capacityFinder = None
                except:
                    self.capacityFinder = None
            if re.match("配送方法",self.dt_): 
                try:
                    self.shipMethod = self.dd[self.dt.index(_)].get_text()
                    # self.shipMethod =  re.sub('\s+', '', self.shipMethod)
                    if self.shipMethod == " ":
                        self.shipMethod = None
                except:
                    self.shipMethod = None 
            if re.match("提供者",self.dt_):
                try:
                    self.compName = self.dd[self.dt.index(_)].get_text()
                    # self.compName =  re.sub('\s+', '', self.compName)
                    if self.compName == " ":
                        self.compName = None
                except:
                    self.compName = None
            if re.match("消費期限/賞味期限",self.dt_): 
                try:
                    self.consumption = self.dd[self.dt.index(_)].get_text()
                    # self.consumption =  re.sub('\s+', '', self.consumption)
                    if self.consumption == " ":
                        self.consumption = None
                except:
                    self.consumption = None
            
        try:
            self.categoryFinder = self.html.find(class_=categoryFinder).find_all("ul")
            self.multiple_category = []
            for cat in self.categoryFinder:
                self.parent_category = ""
                self.liTag = cat.find_all("li")[1:-1]
                for i,_ in enumerate(self.liTag):
                    self.temp = _.find("a").get_text()
                    self.temp = re.sub(r'\s+', '', self.temp)
                    if (i == (len(self.liTag) - 1)):
                        self.parent_category += self.temp
                    else:
                        self.parent_category +=self.temp+"_"
                self.multiple_category.append(self.parent_category)
        except:
            self.multiple_category =  []

        try:
            self.localNameFinder = self.html.find(class_=localNameFinder).get_text()
            # self.localNameFinder =  re.sub('\s+', '', self.localNameFinder)
            if self.localNameFinder == " ":
                self.localNameFinder = None
        except:
            self.localNameFinder = None
        try:
            self.titleFinder = self.html.find(class_=titleFinder).find_all("li")
            self.titleFinder = self.titleFinder[-1].get_text()
            # self.titleFinder =  re.sub('\s+', '', self.titleFinder)
            if self.titleFinder == " ":
                self.titleFinder = None
        except:
            self.titleFinder = None

        self.item_info = self.html.find_all(class_="gift-comment")

        try:
            self.descriptionFinder = self.item_info[0].get_text()
            # self.descriptionFinder =  re.sub('\s+', '', self.descriptionFinder)
            if self.descriptionFinder == " ":
                self.descriptionFinder = None
        except:
            self.descriptionFinder = None

        try:
            self.managementNumber = self.item_info[1].get_text()
            self.loc = self.managementNumber.index("商品コード: ")
            self.holder =""
            for _ in self.managementNumber[self.loc + len("商品コード:"):]:
                if _ != "\n":
                    self.holder += _
                else:
                    break
            if self.holder != " ":
                self.managementNumber =  re.sub('\s+', '', self.holder)
            else:
                self.managementNumber = None
        except:
            self.managementNumber =  None

        try:
            self.priceFinder = self.html.find(id=priceFinder).get_text()
            self.priceFinder = self.priceFinder.replace("円","")
            self.priceFinder = int(self.priceFinder.replace(",",""))
        except:
            self.priceFinder = None

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
    logging.info(f"{threading.current_thread().name}) -Scraped_items({DataParserClass.total_data}/{len(DataParserClass.data)}) -Fetching({item_url})")
    try:
        html = scrapeURL.get(item_url).text
        time.sleep(2)
        scrapeURL.dataParser(html = html,
                           itemUrl = item_url,
                           stockStatus =None,
                           categoryFinder = "breadcrumb", 
                           localNameFinder = "municipality-name",
                           managementNumber=None,
                           appDeadline = None,
                           titleFinder = "breadcrumb",
                           descriptionFinder = "gift-comment",
                           shipMethod=None,
                           priceFinder = "gift-money-contents",
                           capacityFinder = "slider-txt",
                           consumption = None,
                           compName =None,
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
        itemlist = WebDriverWait(scrapeURL.driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, element_container)))
        scrapeURL.listParser(html =scrapeURL.driver.page_source, elementContainer = element_container)
        nextButton = scrapeURL.driver.find_element_by_class_name(nxt_btn)
        if nextButton.get_attribute("href") == 'javascript:void(0);':
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category}) -Scraped_categories({ListParserClass.total_list}/{len(ScraperCategory.category_list)})")
            with data_lock:
                for _ in scrapeURL.itemList:
                    key = LINK+_
                    if key not in DataParserClass.seen:
                        DataParserClass.data.append({"URL":LINK+_,
                                                 "category":category,
                                                 "stock_status": None,
                                                 "local_name" : None,
                                                 "management_number" :None,
                                                 "app_deadline": None,
                                                 "title" : None,
                                                 "description": None,
                                                 "price" : None,
                                                 "ship_method": None,
                                                 "capacity" :None,
                                                 "consumption": None,
                                                 "comp_name" : None,
                                                 "images" : None
                                                 })
                        DataParserClass.seen.add(key)
                logging.info(f"{threading.current_thread().name}) -Adding_items({len(scrapeURL.itemList)})  -Total_item({len(DataParserClass.data)})")
            break
        else:
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Next_Page({category}) -Scraped_categories({ListParserClass.total_list}/{len(ScraperCategory.category_list)})")
            nextButton.click()
    scrapeURL.driver.quit()

print(f"{threading.current_thread().name}) -Scraping has been started...Site : au PAY Hometown tax payment	Link : https://furusato.wowma.jp/")

start = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Scraping has been started...Site : au PAY Hometown tax payment	Link : https://furusato.wowma.jp/")
site=ScraperCategory("https://furusato.wowma.jp/products/list.php")
site.categoryParser(elementTag = "list-contents")
data=site.category_list
site.driver.quit()
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds for fetching {len(data)} categories")

# data= [
#     {'URL': 'https://furusato.wowma.jp/products/list.php?parent_category=4&category_18=18', 'category': '米・パン_米'},
# {'URL': 'https://furusato.wowma.jp/products/list.php?parent_category=4&category_19=19', 'category': '米・パン_無洗米'},
# {'URL': 'https://furusato.wowma.jp/products/list.php?parent_category=4&category_20=20', 'category': '米・パン_玄米'},
# {'URL': 'https://furusato.wowma.jp/products/list.php?parent_category=4&category_21=21', 'category': '米・パン_もち米・餅'},
# {'URL': 'https://furusato.wowma.jp/products/list.php?parent_category=4&category_22=22', 'category': '米・パン_雑穀'},
# {'URL': 'https://furusato.wowma.jp/products/list.php?parent_category=4&category_23=23', 'category': '米・パン_パン'},
# {'URL': 'https://furusato.wowma.jp/products/list.php?parent_category=4&category_24=24', 'category': '米・パン_総菜パン・バーガー等'}

# ]
# start = time.perf_counter()
# with concurrent.futures.ThreadPoolExecutor(max_workers=5 , thread_name_prefix='Fetching_URL') as executor:
#     futures = [executor.submit(ItemLinkCollector, datum) for datum in data]
#     for future in concurrent.futures.as_completed(futures):
#         if future.result():
#             logging.info(f"{threading.current_thread().name}) -{future.result()}")
# final = time.perf_counter()
# logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  fetch  {len(DataParserClass.data)} items URL")

# unique_data = set()
# for _ in DataParserClass.data:
#     if _['URL'] not in unique_data:
#         unique_data.add(_['URL'])
#     else:
#         index = DataParserClass.data.index(_)
#         DataParserClass.data.pop(index)
#         logging.info(f"{threading.current_thread().name} -Pre Cleaning ... Duplicate URL detected ")

# start = time.perf_counter()
# with concurrent.futures.ThreadPoolExecutor(max_workers=5, thread_name_prefix='Fetching_Item_Data') as executor:
#     futures = [executor.submit(DataCollectorFunction, data) for data in DataParserClass.data]
#     for future in concurrent.futures.as_completed(futures):
#         if future.result():
#             logging.info(f"{threading.current_thread().name}) -{future.result()}")
# final = time.perf_counter()
# logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  scrape  {len(DataParserClass.data)} items data")

# unique_data = set()
# for _ in DataParserClass.data:
#     if _['URL'] not in unique_data:
#         unique_data.add(_['URL'])
#     else:
#         index = DataParserClass.data.index(_)
#         DataParserClass.data.pop(index)
#         logging.info(f"{threading.current_thread().name} -Post Cleaning ... Duplicate URL detected ")

# start = time.perf_counter()
# agt_cd = "AUP"
# mydb = connect.connect(host="localhost",user="user",password="password",database="his_furusato")
# mycursor = mydb.cursor()

# for  datum in data:
#     try:
#         mycursor.execute("INSERT INTO m_agt_catgy (agt_catgy_url,agt_catgy_nm,agt_cd)VALUES (%s,%s,%s)",(datum["URL"],datum["category"],agt_cd))
#         mydb.commit()
#     except connect.errors.DataError as error:
#         logging.info(f"{threading.current_thread().name}) -Data failed to be saved because {error} {datum['URL']} {datum['category']}")    
#     except connect.errors.IntegrityError as error:
#         logging.info(f"{threading.current_thread().name}) -Data failed to be saved because {error} {datum['URL']}{datum['category']}")

# def val(item,item_type):
#     if item_type == "app_deadline":
#         try:
#             item = item[:200]
#         except:
#             item = None

#     if item_type == "comp_name":
#         try:
#             item = item[:30]
#         except:
#             item = None    
#     return item

# for  datum in DataParserClass.data:
#     try:
#         mycursor.execute("INSERT INTO t_agt_mchan (agt_mchan_url,agt_city_nm,agt_mchan_cd,mchan_nm,mchan_desc,appli_dline,price,capacity,mchan_co,agt_cd) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
#         (datum["URL"],datum["local_name"],datum["management_number"],datum["title"],datum["description"],val(datum["app_deadline"],"app_deadline"),datum["price"],datum["capacity"],val(datum["comp_name"],"comp_name"),agt_cd))
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
#     except connect.errors.DataError as error:
#         logging.warning(f"{threading.current_thread().name}) -Data failed to be saved because {error} ") 
#         logging.warning(f'{datum["URL"]},{datum["local_name"]},{datum["management_number"]},{datum["title"]},{datum["description"]},{val(datum["app_deadline"],"app_deadline")},{datum["price"]},{datum["capacity"]},{val(datum["comp_name"],"comp_name")},{agt_cd}')
#     except connect.errors.IntegrityError as error:
#         logging.warning(f"{threading.current_thread().name}) -Data failed to be saved because {error} ")
#         logging.warning(f'{datum["URL"]},{datum["local_name"]},{datum["management_number"]},{datum["title"]},{datum["description"]},{val(datum["app_deadline"],"app_deadline")},{datum["price"]},{datum["capacity"]},{val(datum["comp_name"],"comp_name")},{agt_cd}')

# final = time.perf_counter()
# logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  save  {len(DataParserClass.data)} items data")
