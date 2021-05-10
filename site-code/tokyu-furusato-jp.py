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
import mysql.connector as connect
from datetime import datetime
import os
""" This section declares all the variables used """
LINK = "https://tokyu-furusato.jp/goods/result"
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
        self.category_container = self.html.find(class_=self.elementTag)
        self.liTag = self.category_container.li
        while True:
            self.subcat = self.liTag.find_all("li")
            self.parent = self.liTag.find("label").find("span").get_text()
            self.parent = self.parent[:self.parent.index('（')]
            for _ in self.subcat:
                self.categoryData = _.find("span").get_text()
                self.categoryData = self.categoryData[:self.categoryData.index('（')]
                self.link = _.find("input").get("value")
                ScraperCategory.category_list.append({"URL":"https://tokyu-furusato.jp/goods/result?limit=&order=1&chk_sub_ctg%5B%5D="+self.link,"category":self.parent+"_"+self.categoryData})
            if self.liTag.find_next_sibling():
                self.liTag = self.liTag.find_next_sibling()
            else:
                break

class ListParserClass(WebDriver):
    total_list = 0

    def __init__(self, url):
        self.url = url
        type(self).total_list +=1
        self.item_list = []
        super().__init__(url)

    def listParser(self,html,elementContainer):
        self.elementContainer = elementContainer
        self.html = bs(html, 'html.parser')
        self.container = self.html.find(class_="section_search")
        self.container = self.container.find(class_=self.elementContainer)
        self.ChildElement = self.container.find_next()
        while True:
            self.item_list.append(self.ChildElement.find("a").get("href"))
            if self.ChildElement.find_next_sibling():
                self.ChildElement = self.ChildElement.find_next_sibling()
            else:
                break

class DataParserClass(web_driver_1.WebDriver):
    data = []
    total_data = 0

    def __init__(self, url):
        self.url = url
        type(self).total_data +=1
        self.item_list = []
        super().__init__()
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
        self.about = self.html.find(class_="itembox-data")
        self.dt = self.about.find_all("dt")
        self.dd = self.about.find_all("dd")
        for _ in self.dt:
            self.dt_ = _.get_text()
            if re.match("内容",self.dt_): 
                try:
                    self.capacityFinder = self.dd[self.dt.index(_)].get_text()
                    # self.capacityFinder = re.sub('\s+', '', self.capacityFinder)
                    if self.capacityFinder == " ":
                        self.capacityFinder = None
                except:
                    self.capacityFinder = None
            if re.match("提供元",self.dt_): 
                try:
                    self.compName = self.dd[self.dt.index(_)].get_text()
                    # self.compName = re.sub('\s+', '', self.compName)
                    if self.compName == " ":
                        self.compName = None
                except:
                    self.compName = None
        try:
            self.guide = self.html.find(class_="guidelist")
            self.dt = self.guide.find_all("dt")
            self.dd = self.guide.find_all("dd")
            for _ in self.dt:
                self.dt_ = _.get_text()
                if re.match("配送",self.dt_): 
                    self.shipMethod = self.dd[self.dt.index(_)].get_text()
                    # self.shipMethod = re.sub('\s+', '', self.shipMethod)
                    if self.shipMethod == " ":
                        self.shipMethod = None
        except:
            self.shipMethod = None

        try:
            self.localNameFinder = self.html.find(class_=localNameFinder).find("em",{"class":"text_area"}).get_text()
            # self.localNameFinder =  re.sub('\s+', '', self.localNameFinder)
            if self.localNameFinder == " ":
                self.localNameFinder = None
        except:
            self.localNameFinder =  None

        try:
            self.managementNumber = self.html.find(class_=managementNumber).get_text()
            self.managementNumber = self.managementNumber.replace("ID：","")
            # self.managementNumber = re.sub(r'\s+', '', self.managementNumber)
            if "【" in self.managementNumber:
                self.managementNumber = self.managementNumber[:self.managementNumber.index("】")].replace("【","")
            elif self.managementNumber == " ":
                self.managementNumber = None
        except:
            self.managementNumber =  None 

        try:
            self.titleFinder = self.html.find(class_=titleFinder).find_all("li")[-1].get_text()
            # self.titleFinder =  re.sub('\s+', '', self.titleFinder)
            if self.titleFinder == " ":
                self.titleFinder = None        
        except:
            self.titleFinder = None
        try:
            self.descriptionFinder = self.html.find(class_=descriptionFinder).find("p").get_text()
            # self.descriptionFinder =  re.sub('\s+', '', self.descriptionFinder)
            if self.descriptionFinder == " ":
                self.descriptionFinder = None
        except:
            self.descriptionFinder = None
        try:
            self.priceFinder = self.html.find(class_=priceFinder).find("dd").get_text()
            self.priceFinder = self.priceFinder.replace("円","")
            self.priceFinder = int(self.priceFinder.replace(",",""))
        except:
            self.priceFinder = None
        try:
            self.imageUrlFinder = self.html.find(class_=imageUrlFinder).find_all("img")
            self.imageList = []
            for _ in self.imageUrlFinder:
                self.imageList.append(_.get("src"))      
        except:
            self.imageList = []
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
    logging.info(f"{threading.current_thread().name}) -Scraped_items({DataParserClass.total_data}/{len(DataParserClass.data)}) -Fetching({item_url})")
    try:
        time.sleep(3)
        scrapeURL.dataParser(html = scrapeURL.get(item_url).text,
                           itemUrl = item_url,
                           stockStatus =None,
                           categoryFinder = None, 
                           localNameFinder = "heading_page",
                           managementNumber="itembox-id",
                           appDeadline = None,
                           titleFinder = "topicpath",
                           descriptionFinder = "section_block",
                           shipMethod=None,
                           priceFinder = "itembox-price",
                           capacityFinder = "itembox-data",
                           consumption = None,
                           compName =None,
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
        item_list = WebDriverWait(scrapeURL.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, element_container)))
        scrapeURL.listParser(html =scrapeURL.driver.page_source, elementContainer = element_container)
        try:
            lenPagination = scrapeURL.driver.find_element_by_xpath("//*[@id='top']/main/div[1]/ul")
            lenPagination = lenPagination.find_elements_by_class_name("pagination-item")
            nxtbtn = lenPagination[-1].find_element_by_class_name("pagination-link").get_attribute("href")
            if nxtbtn[-1] == "#":
                logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category}) -Scraped_categories({ListParserClass.total_list}/{len(ScraperCategory.category_list)})")
                with data_lock:
                    for _ in scrapeURL.item_list:
                        DataParserClass.data.append({"URL":_,
                                                 "category":category,
                                                 "stock_status": None,
                                                 "local_name" : None,
                                                 "management_number" :None,
                                                 "app_deadline": None,
                                                 "title" : None,
                                                 "description": None,
                                                 "price" : 0,
                                                 "ship_method": None,
                                                 "capacity" :None,
                                                 "consumption": None,
                                                 "comp_name" : None,
                                                 "images" : None
                                                 })                   
                logging.info(f"{threading.current_thread().name}) -Adding_items({len(scrapeURL.item_list)})  -Total_item({len(DataParserClass.data)})")
                break
            else:
                logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Next_Page({category}) -Scraped_categories({ListParserClass.total_list}/{len(ScraperCategory.category_list)})")
                lenPagination[-1].find_element_by_tag_name("a").send_keys(Keys.ENTER)
        except NoSuchElementException:
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category}) -Scraped_categories({ListParserClass.total_list}/{len(ScraperCategory.category_list)})")
            with data_lock:
                for _ in scrapeURL.item_list:
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
                                                 "images" : None
                                                 })
                logging.info(f"{threading.current_thread().name}) -Adding_items({len(scrapeURL.item_list)})  -Total_item({len(DataParserClass.data)})")
            break
    scrapeURL.driver.quit()

print(f"{threading.current_thread().name}) -Scraping has been started...Site : Hometown pallet	Link : https://tokyu-furusato.jp/")
start = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Scraping has been started...Site : Hometown pallet	Link : https://tokyu-furusato.jp/")
site=ScraperCategory(LINK)
site.categoryParser(elementTag ="dropdownlist")
data=site.category_list
site.driver.quit()
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  fetch  {len(data)} categories")

# data =[
# {'URL': 'https://tokyu-furusato.jp/goods/result?limit=&order=1&chk_sub_ctg%5B%5D=6', 'category': '米・パン_米'},
# {'URL': 'https://tokyu-furusato.jp/goods/result?limit=&order=1&chk_sub_ctg%5B%5D=7', 'category': '米・パン_無洗米'},
# {'URL': 'https://tokyu-furusato.jp/goods/result?limit=&order=1&chk_sub_ctg%5B%5D=8', 'category': '米・パン_もち米・餅'},
# {'URL': 'https://tokyu-furusato.jp/goods/result?limit=&order=1&chk_sub_ctg%5B%5D=9', 'category': '米・パン_パン'},
# {'URL': 'https://tokyu-furusato.jp/goods/result?limit=&order=1&chk_sub_ctg%5B%5D=10', 'category': '米・パン_その他米・パン類'}
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
# agt_cd = "FPL"
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