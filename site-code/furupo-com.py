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
import re
import  concurrent.futures
from bs4 import BeautifulSoup as bs
from datetime import datetime
import mysql.connector as connect
import os
""" This section declares all the variables used """
LINK = "https://furu-po.com/"
date = datetime.now().strftime("%Y%m%d")
script_name = os.path.splitext(os.path.basename(__file__))[0]

logging.basicConfig(filename=f"/home/ec2-user/prj_his_furusato_scrape/logs/{script_name}_{date}.log",filemode='a',level=logging.INFO, format='[%(asctime)s](%(levelname)s@%(message)s', datefmt='%d-%b-%y %H:%M:%S')
data_lock = threading.Lock()

class ScraperCategory(WebDriver):
    category_list = []
    sub_category_list = []

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
                ScraperCategory.category_list.append({"URL":_.find("a").get("href"),"category":self.parent+"_"+self.categoryData})
            if self.liTag_.find_next_sibling():
                self.liTag_ = self.liTag_.find_next_sibling()
            else:
                break
        for item in self.category_list:
            self.driver.get(item["URL"])
            self.html = bs(self.driver.page_source, 'html.parser')
            try:
                self.sub_category = self.html.find(class_="subcategory").find_all("option")
                for _ in self.sub_category[1:]:
                    ScraperCategory.sub_category_list.append({"URL":"https://furu-po.com/"+_.get("value"),"category":item["category"]+"_"+_.get_text()})
            except:
                ScraperCategory.sub_category_list.append(item)
            logging.info(f"{threading.current_thread().name}) -Scraping_sub_category({item['category']})")
                    

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
        self.container = self.html.find(class_=self.elementContainer)
        self.ChildElement = self.container.find_next()
        while True:
            self.itemList.append(self.ChildElement.find("a").get("href"))
            if self.ChildElement.find_next_sibling():
                self.ChildElement = self.ChildElement.find_next_sibling()
            else:
                break
        

class DataParserClass(WebDriver):
    data = []
    total_data = 0

    def __init__(self, url):
        self.url = url
        type(self).total_data +=1
        super().__init__(url)
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
        self.appDeadline = None

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
                    # self.shipMethod = re.sub('\s+', '', self.shipMethod)
                    if self.shipMethod == " ":
                        self.shipMethod = None
                except:
                    self.shipMethod = None
            if re.match("容量",self.dt_):
                try:
                    self.capacityFinder = self.rcell[self.lcell.index(_)].get_text()
                    # self.capacityFinder = re.sub('\s+', '', self.capacityFinder)
                    if self.capacityFinder == " ":
                        self.capacityFinder = None
                except:
                    self.capacityFinder = None 
            if re.match("賞味期限",self.dt_):
                try:
                    self.consumption = self.rcell[self.lcell.index(_)].get_text()
                    # self.consumption = re.sub('\s+', '', self.consumption)
                    if self.consumption == " ":
                        self.consumption = None
                except:
                    self.consumption = None 
            if re.match("管理番号",self.dt_):
                try:
                    self.managementNumber = self.rcell[self.lcell.index(_)].get_text()
                    # self.managementNumber = re.sub('\s+', '', self.managementNumber)
                    if self.managementNumber == " ":
                        self.managementNumber = None
                except:
                    self.managementNumber = None 
            if re.match("事業者名",self.dt_):
                try:
                    self.compName = self.rcell[self.lcell.index(_)].get_text()
                    # self.compName = re.sub('\s+', '', self.compName)
                    if self.compName == " ":
                        self.compName = None
                except:
                    self.compName = None 

        try:
            self.stockStatus = self.html.find(class_=stockStatus).find("span").get_text()
            if self.stockStatus == " ":
                self.stockStatus = None
        except:
            self.stockStatus =  None
        try:
            self.localNameFinder = self.html.find(class_=localNameFinder)
            self.localNameFinder = self.localNameFinder.find_all("div",{"class":"icon"})
            self.localNameFinder = self.localNameFinder[1].get_text()
            # self.localNameFinder = re.sub('\s+', '', self.localNameFinder)
            if self.localNameFinder == " ":
                self.localNameFinder = None
        except:
            self.localNameFinder =  None

        try:
            self.titleFinder = self.html.find(class_=titleFinder).find("h1").get_text()
            # self.titleFinder = re.sub('\s+', '', self.titleFinder)
            if self.titleFinder == " ":
                self.titleFinder = None
        except:
            self.titleFinder = None

        try:
            self.descriptionFinder = self.html.find(class_=descriptionFinder).get_text()
            self.descriptionFinder = re.sub('\s+', '', self.descriptionFinder)
            if self.descriptionFinder == " ":
                self.descriptionFinder = None
        except:
            self.descriptionFinder = None
        try:
            self.priceFinder = self.html.find(class_=priceFinder).get_text()
            self.priceFinder = self.priceFinder.replace("円","")
            self.priceFinder = int(self.priceFinder.replace(",",""))        
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
            self.imageList = None
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
    logging.info(f"{threading.current_thread().name}) -Scraped_items({DataParserClass.total_data}/{len(DataParserClass.data)}) -Fetching({item_url})")
    try:
        item_info = WebDriverWait(scrapeURL.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "lg-info")))
        scrapeURL.dataParser(html = scrapeURL.driver.page_source,
                           itemUrl = item_url, 
                           stockStatus = None,
                           categoryFinder = None, 
                           localNameFinder = "lg-info",
                           managementNumber=None,
                           appDeadline = None,
                           titleFinder = "item_detail",
                           descriptionFinder = "item-description",
                           priceFinder = "price",
                           shipMethod = None,
                           capacityFinder = None,
                           consumption = None,
                           compName=None,
                           imageUrlFinder = "slick-track" )
    except:
        logging.info(f"{threading.current_thread().name}) - Unable to load the element")
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
                logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Next_Page({category}) -Scraped_categories({ListParserClass.total_list}/{len(ScraperCategory.category_list)})")
            except NoSuchElementException:
                logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category}) -Scraped_categories({ListParserClass.total_list}/{len(ScraperCategory.category_list)})")
                with data_lock:
                    for _ in scrapeURL.itemList:
                        DataParserClass.data.append({"URL":_,
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
                                                 "images" : []
                                                 })
                    logging.info(f"{threading.current_thread().name}) -Adding_items({len(scrapeURL.itemList)})  - Total_item({len(DataParserClass.data)})")
                break
        except:
            break
    scrapeURL.driver.quit()
print(f"{threading.current_thread().name}) -Scraping has been started...Site : Furupo (JTB)	Link : https://furu-po.com/")
start = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Scraping has been started...Site : Hometown pallet	Link : https://furu-po.com/")
site=ScraperCategory(LINK)
site.categoryParser(elementTag = "popover")
site.driver.quit()
data = site.sub_category_list
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds for fetching {len(data)} categories")

# data = [
#     {'URL': 'https://furu-po.com/goods_list/1/36/478', 'category': '米・パン_米_コシヒカリ'},
# {'URL': 'https://furu-po.com/goods_list/1/36/479', 'category': '米・パン_米_ひとめぼれ'},
# {'URL': 'https://furu-po.com/goods_list/1/36/480', 'category': '米・パン_米_つや姫'},
# {'URL': 'https://furu-po.com/goods_list/1/36/481', 'category': '米・パン_米_ゆめぴりか'},
# {'URL': 'https://furu-po.com/goods_list/1/36/482', 'category': '米・パン_米_あきたこまち'},
# {'URL': 'https://furu-po.com/goods_list/1/36/483', 'category': '米・パン_米_ヒノヒカリ'},
# {'URL': 'https://furu-po.com/goods_list/1/36/484', 'category': '米・パン_米_はえぬき'},
# {'URL': 'https://furu-po.com/goods_list/1/36/485', 'category': '米・パン_米_ミルキークイーン'},
# {'URL': 'https://furu-po.com/goods_list/1/36/486', 'category': '米・パン_米_さがびより'},
# {'URL': 'https://furu-po.com/goods_list/1/36/487', 'category': '米・パン_米_ササニシキ'},
# {'URL': 'https://furu-po.com/goods_list/1/36/488', 'category': '米・パン_米_ブレンド'},
# {'URL': 'https://furu-po.com/goods_list/1/36/489', 'category': '米・パン_米_にこまる'},
# {'URL': 'https://furu-po.com/goods_list/1/36/490', 'category': '米・パン_米_きぬむすめ'},
# {'URL': 'https://furu-po.com/goods_list/1/36/491', 'category': '米・パン_米_その他米'},
# {'URL': 'https://furu-po.com/goods_list/1/37', 'category': '米・パン_無洗米'},
# {'URL': 'https://furu-po.com/goods_list/1/38', 'category': '米・パン_玄米'},
# {'URL': 'https://furu-po.com/goods_list/1/39/492', 'category': '米・パン_もち米・餅_もち米'},
# {'URL': 'https://furu-po.com/goods_list/1/39/493', 'category': '米・パン_もち米・餅_餅'},
# {'URL': 'https://furu-po.com/goods_list/1/40', 'category': '米・パン_雑穀'},
# {'URL': 'https://furu-po.com/goods_list/1/41/494', 'category': '米・パン_パン_食パン'},
# {'URL': 'https://furu-po.com/goods_list/1/41/495', 'category': '米・パン_パン_菓子パン'},
# {'URL': 'https://furu-po.com/goods_list/1/41/496', 'category': '米・パン_パン_その他パン'},
# {'URL': 'https://furu-po.com/goods_list/1/42/497', 'category': '米・パン_総菜パン・バーガー等_総菜パン'},
# {'URL': 'https://furu-po.com/goods_list/1/42/498', 'category': '米・パン_総菜パン・バーガー等_バーガー'},
# {'URL': 'https://furu-po.com/goods_list/8/100/617', 'category': 'お酒_日本酒_純米大吟醸酒'},
# {'URL': 'https://furu-po.com/goods_list/8/100/619', 'category': 'お酒_日本酒_純米吟醸酒'},
# {'URL': 'https://furu-po.com/goods_list/8/100/621', 'category': 'お酒_日本酒_純米酒'},
# {'URL': 'https://furu-po.com/goods_list/8/101/628', 'category': 'お酒_焼酎_米'},
# {'URL': 'https://furu-po.com/goods_list/31/114/661', 'category': '飲料類_お茶類_玄米茶（飲料）'},
# {'URL': 'https://furu-po.com/goods_list/31/114/665', 'category': '飲料類_お茶類_玄米茶（茶葉・ティーバック）'},
# {'URL': 'https://furu-po.com/goods_list/125/126/789', 'category': '調味料・油_味噌_米味噌'},
# {'URL': 'https://furu-po.com/goods_list/125/127/812', 'category': '調味料・油_たれ・ドレッシング・酢_米酢'}

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
# with concurrent.futures.ThreadPoolExecutor(max_workers=5,thread_name_prefix='Fetching_Item_Data') as executor:
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
# agt_cd = "JTB"
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
