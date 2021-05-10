"""

Site : ANA's hometown tax payment	
Link : https://furusato.ana.co.jp/	

"""
import web_driver_1
import time
import threading 
import logging
import  concurrent.futures
from bs4 import BeautifulSoup as bs
import mysql.connector as connect
from datetime import datetime
import os
import re
""" This section declares all the variables used """
LINK = "https://furusato.ana.co.jp/products/list.php"
date = datetime.now().strftime("%Y%m%d")
script_name = os.path.splitext(os.path.basename(__file__))[0]


logging.basicConfig(filename=f"/home/ec2-user/prj_his_furusato_scrape/logs/{script_name}_{date}.log",filemode='a',level=logging.INFO, format='[%(asctime)s](%(levelname)s@%(message)s', datefmt='%d-%b-%y %H:%M:%S')
data_lock = threading.Lock()

class ScraperCategory(web_driver_1.WebDriver):
    category_list = []
    temp = []

    def __init__(self):
        super().__init__()

    def categoryParser(self,**kwargs):
        self.elementTag = kwargs.get("elementTag")
        self.html = bs(kwargs.get("html"), 'html.parser')
        self.category_container_ = self.html.find(class_="gNavContainer1")
        self.category_container = self.category_container_.find_all(class_=self.elementTag)
        self.parent_container = self.category_container_.find_all(class_="gnav_detail_medium_contents")
        for _ in self.parent_container:
            self.parent_li = _.find_all("li")
            self.holder = []
            for base in self.parent_li[2:]:
                self.holder.append(base.get_text())
            ScraperCategory.temp.append({"main":self.parent_li[0].get_text(),"base":self.holder})


        for category in  self.category_container:
            category_ = category.find_all("li")
            if len(category_) > 2 :
                for _ in category_[2:]:
                    # self.categoryData = re.sub(r'\([^()]*\)', '', _.find("a").get_text())
                    self.categoryData =  _.find("a").get_text()
                    for parent in ScraperCategory.temp:
                        if category_[0].get_text() in parent["base"]:
                            self.categoryData = parent["main"]+"_"+category_[0].get_text()+"_"+self.categoryData
                    ScraperCategory.category_list.append({"URL":_.find("a").get("href"),"category":self.categoryData})
            else:
                # self.categoryData = re.sub(r'\([^()]*\)', '', category_[-1].find("a").get_text())
                self.categoryData = category_[-1].find("a").get_text()
                for parent in ScraperCategory.temp:
                    if category_[0].get_text() in parent["base"]:
                        self.categoryData = parent["main"]+"_"+category_[0].get_text()
                ScraperCategory.category_list.append({"URL":category_[-1].find("a").get("href"),"category":self.categoryData}) 

class ListParserClass(web_driver_1.WebDriver):
    total_list = 0

    def __init__(self):
        self.item_list = []
        type(self).total_list +=1
        super().__init__()

    def listParser(self,html,elementContainer):
        self.elementContainer = elementContainer
        self.html = bs(html, 'html.parser')
        self.container = self.html.find(id="main_column")
        self.container = self.container.find(class_=self.elementContainer)
        self.ChildElement = self.container.find_next()
        while True:
            self.item_list.append(self.ChildElement.find("div").get("data-product-url"))
            if self.ChildElement.find_next_sibling():
                self.ChildElement = self.ChildElement.find_next_sibling()
            else:
                break

class DataParserClass(web_driver_1.WebDriver):
    data = []
    total_data = 0
    total_list = 0

    def __init__(self):
        self.item_list = []
        type(self).total_list +=1
        type(self).total_data +=1
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
        self.table = self.html.find(class_="as-tbset")
        self.th = self.table.find_all("th")
        self.td = self.table.find_all("td")
        for _ in self.th:
            self.dt_ = _.get_text()
            if re.match("内容量",self.dt_):
                try:
                    self.capacityFinder = self.td[self.th.index(_)].get_text()
                    # self.capacityFinder =  re.sub('\s+', '', self.capacityFinder)
                    if self.capacityFinder == " ":
                        self.capacityFinder = None
                except:
                    self.capacityFinder = None 

            if re.match("賞味期限",self.dt_):
                try:
                    self.consumption = self.td[self.th.index(_)].get_text()
                    # self.consumption =  re.sub('\s+', '', self.consumption)
                    if self.consumption == " ":
                        self.consumption = None
                except:
                    self.consumption = None
            if re.match("事業者名",self.dt_): 
                try:
                    self.compName = self.td[self.th.index(_)].get_text()
                    # self.compName =  re.sub('\s+', '', self.compName)
                    if self.compName == " ":
                        self.compName = None
                except:
                    self.compName = None

        try:
            self.stockStatus = self.html.find(class_=stockStatus).find("span").get_text()
            # self.stockStatus = re.sub('\s+', '', self.stockStatus)
            if self.stockStatus == " ":
                self.stockStatus = None
        except:
            self.stockStatus =  None
        try:
            self.localNameFinder = self.html.find(class_=localNameFinder).get_text()
            # self.localNameFinder = re.sub(r'\s+', '', self.localNameFinder)
            if self.stockStatus == " ":
                self.stockStatus = None
        except:
            self.localNameFinder = None
        # try:
        #     self.managementNumber =""
        #     print(self.html.find(class_=titleFinder).get_text())
        #     for _ in self.html.find(class_=titleFinder).get_text():
        #         if _ == " ":
        #             break
        #         self.managementNumber += _
        #     self.managementNumber = re.sub(r'\s+', '', self.managementNumber)
        # except:
        #     self.managementNumber =  None 

        try:
            self.titleFinder = self.html.find(class_=titleFinder).get_text()
            # self.titleFinder = re.sub(r'\s+', '', self.titleFinder)
            self.titleFinder = self.titleFinder.replace(self.localNameFinder,"")
            if self.titleFinder == " ":
                self.titleFinder = None
        except:
            self.titleFinder = None
        try:
            self.descriptionFinder = self.html.find(class_=descriptionFinder).get_text()
            # self.descriptionFinder = re.sub(r'\s+', '', self.descriptionFinder)
            if self.descriptionFinder == " ":
                self.descriptionFinder = None
        except:
            self.descriptionFinder = None
        try:
            self.priceFinder = self.html.find(class_=priceFinder).get_text()
            self.priceFinder = re.sub(r'\s+', '', self.priceFinder)
            self.priceFinder = int(self.priceFinder.replace(",",""))
        except:
            self.priceFinder = None
        try:
            self.imageUrlFinder = self.html.find(class_="as-detail_wrap").find(class_=imageUrlFinder).find_all("li")
            self.imageList = []
            for _ in self.imageUrlFinder:
                self.imageList.append("https://furusato.ana.co.jp"+_.find("img").get("src")) 
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
    scrapeURL = DataParserClass()
    logging.info(f"{threading.current_thread().name}) -Scraped_items({DataParserClass.total_data -1 }/{len(DataParserClass.data)}) -Fetching({item_url})")
    try:
        html = scrapeURL.get(item_url).text
        time.sleep(3)
        scrapeURL.dataParser(html = html,
                           itemUrl = item_url,
                           stockStatus = "stock",
                           categoryFinder = None,
                           localNameFinder = "as-item_pref_detail",
                           managementNumber = None,
                           appDeadline = None,
                           titleFinder = "as-item_name_detail",
                           descriptionFinder = "as-txarea_m",
                           priceFinder = "as-pl_m",
                           shipMethod = None,
                           capacityFinder = None,
                           consumption = None,
                           compName = None,
                           imageUrlFinder = "as-main" )
    except:
        logging.info(f"{threading.current_thread().name}) - Unable to load the element")


def ItemLinkCollector(data):
    element_container = "as-flex_left"
    url_category=data["URL"]
    category=data["category"]
    scrapeURL = ListParserClass()
    logging.info(f"{threading.current_thread().name}) -Scraping([{category}]{url_category})")
    while True:
        html =scrapeURL.get(url_category).text
        time.sleep(3)
        scrapeURL.listParser(html =html, elementContainer = element_container)
        html_ = bs(html, 'html.parser')
        nextButton = html_.find(class_="pager_links")
        nextButton = nextButton.find_all(class_="pager_link")
        url_category_ = LINK+nextButton[-1].find("a").get("href")
        if url_category != url_category_ and len(nextButton) > 1 :
            url_category = url_category_
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Next_Page({category}) -Scraped_categories({ListParserClass.total_list}/{len(ScraperCategory.category_list)})")
        else:
            logging.info(f"{threading.current_thread().name}) -Active_thread({int(threading.activeCount())-1}) -Exiting({category}) -Scraped_categories({ListParserClass.total_list}/{len(ScraperCategory.category_list)})")
            with data_lock:
                for _ in scrapeURL.item_list:
                    DataParserClass.data.append({"URL":"https://furusato.ana.co.jp"+_,
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

print(f"{threading.current_thread().name}) -Scraping has been started...Site : ANA's hometown tax payment	Link : https://furusato.ana.co.jp/")
start = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Scraping has been started...Site : Hometown pallet	Link : https://tokyu-furusato.jp/")
site=ScraperCategory()
site.categoryParser(html= site.get(LINK).text, elementTag = "gnav_detail_contents")
data=site.category_list
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds for fetching {len(data)} categories")
# data =[
#     {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9_%E7%B1%B3_%E7%B2%BE%E7%B1%B3&sort=number5%2CNumber1%2CScore', 'category': '米・穀物_米_精米'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9_%E7%B1%B3_%E7%84%A1%E6%B4%97%E7%B1%B3&sort=number5%2CNumber1%2CScore', 'category': '米・穀物_米_無洗米'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9_%E7%B1%B3_%E7%8E%84%E7%B1%B3&sort=number5%2CNumber1%2CScore', 'category': '米・穀物_米_玄米'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9_%E7%B1%B3_%E3%82%B3%E3%82%B7%E3%83%92%E3%82%AB%E3%83%AA&sort=number5%2CNumber1%2CScore', 'category': '米・穀物_米_コシヒカリ'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9_%E7%B1%B3_%E3%81%B2%E3%81%A8%E3%82%81%E3%81%BC%E3%82%8C&sort=number5%2CNumber1%2CScore', 'category': '米・穀物_米_ひとめぼれ'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9_%E7%B1%B3_%E3%81%A4%E3%82%84%E5%A7%AB&sort=number5%2CNumber1%2CScore', 'category': '米・穀物_米_つや姫'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9_%E7%B1%B3_%E3%82%86%E3%82%81%E3%81%B4%E3%82%8A%E3%81%8B&sort=number5%2CNumber1%2CScore', 'category': '米・穀物_米_ゆめぴりか'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9_%E7%B1%B3_%E3%81%82%E3%81%8D%E3%81%9F%E3%81%93%E3%81%BE%E3%81%A1&sort=number5%2CNumber1%2CScore', 'category': '米・穀物_米_あきたこまち'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9_%E7%B1%B3_%E3%83%92%E3%83%8E%E3%83%92%E3%82%AB%E3%83%AA&sort=number5%2CNumber1%2CScore', 'category': '米・穀物_米_ヒノヒカリ'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9_%E7%B1%B3_%E3%81%AF%E3%81%88%E3%81%AC%E3%81%8D&sort=number5%2CNumber1%2CScore', 'category': '米・穀物_米_はえぬき'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9_%E7%B1%B3_%E3%83%9F%E3%83%AB%E3%82%AD%E3%83%BC%E3%82%AF%E3%82%A4%E3%83%BC%E3%83%B3&sort=number5%2CNumber1%2CScore', 'category': '米・穀物_米_ミルキークイーン'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9_%E7%B1%B3_%E3%81%95%E3%81%8C%E3%81%B3%E3%82%88%E3%82%8A&sort=number5%2CNumber1%2CScore', 'category': '米・穀物_米_さがびより'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9_%E7%B1%B3_%E3%82%B5%E3%82%B5%E3%83%8B%E3%82%B7%E3%82%AD&sort=number5%2CNumber1%2CScore', 'category': '米・穀物_米_ササニシキ'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9_%E7%B1%B3_%E3%81%BB%E3%81%8B%E3%81%AE%E7%B1%B3&sort=number5%2CNumber1%2CScore', 'category': '米・穀物_米_ほかの米'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9_%E3%81%BB%E3%81%8B%E3%81%AE%E7%A9%80%E7%89%A9%E5%8A%A0%E5%B7%A5%E5%93%81_%E9%A4%85&sort=number5%2CNumber1%2CScore', 'category': '米・穀物_ほかの穀物加工品_餅'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E5%AE%9A%E6%9C%9F%E4%BE%BF_%E7%B1%B3%28%E5%AE%9A%E6%9C%9F%E4%BE%BF%29&sort=number5%2CNumber1%2CScore', 'category': '定期便_米(定期便)'},
# {'URL': 'https://furusato.ana.co.jp/products/list.php?limit=30&s4=%E6%96%B0%E5%9E%8B%E3%82%B3%E3%83%AD%E3%83%8A%E8%A2%AB%E5%AE%B3%E6%94%AF%E6%8F%B4_%E9%A3%9F%E5%93%81%E6%94%AF%E6%8F%B4_%E7%B1%B3%E3%83%BB%E7%A9%80%E7%89%A9&sort=number5%2CNumber1%2CScore', 'category': '新型コロナ被害支援_食品支援_米・穀物'}

# ]
# start = time.perf_counter()
# with concurrent.futures.ThreadPoolExecutor(max_workers=5,thread_name_prefix='Fetching_URL') as executor:
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
# agt_cd = "ANA"
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


