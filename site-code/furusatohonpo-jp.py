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
from selenium.common.exceptions import NoSuchElementException,TimeoutException
import logging
import  concurrent.futures
from bs4 import BeautifulSoup as bs
import re
from datetime import datetime
import mysql.connector as connect
import os 
""" This section declares all the variables used """
LINK = "https://furusatohonpo.jp"
date = datetime.now().strftime("%Y%m%d")
script_name = os.path.splitext(os.path.basename(__file__))[0]

logging.basicConfig(filename=f"/home/ec2-user/prj_his_furusato_scrape/logs/{script_name}_{date}.log",filemode='a',level=logging.INFO, format='[%(asctime)s](%(levelname)s@%(message)s', datefmt='%d-%b-%y %H:%M:%S')
data_lock = threading.Lock()

class ScraperData(WebDriver):
    item_list = set()

    def __init__(self, url):
        self.url =url
        super().__init__(url)

    def dataParser(self,**kwargs):
        self.driver.get(self.url)
        self.element_tag = kwargs.get("element_tag")
        ctr = 0
        while True:
            # self.driver.implicitly_wait(5)
            time.sleep(3)
            # element = WebDriverWait(self.driver, 5).until(
            # EC.presence_of_element_located((By.CLASS_NAME, "c-itemList__item ")))
            self.html = bs(self.driver.page_source, 'html.parser')
            self.parent =  self.html.find(class_=self.element_tag)
            self.group_items =  self.parent.find_all("li")
            for _ in self.group_items:
                self.data = "https://furusatohonpo.jp"+_.find("a").get("href")
                if self.data not in ScraperData.item_list:
                    ScraperData.item_list.add(self.data)
            try:
                nextButton = self.driver.find_element_by_class_name("c-pagination")
                nextButton = nextButton.find_element_by_class_name("c-pagination__next")
                nextButton.send_keys(Keys.ENTER)
                logging.info(f"{threading.current_thread().name}) -Next_Page({self.driver.current_url})")
            except NoSuchElementException:
                logging.info(f"{threading.current_thread().name}) -Exiting...")
                break
        self.driver.quit()



class DataParserClass(WebDriver):
    category_list = []
    category_set =set()
    data = []
    totalData = 0
    def __init__(self, url):
        self.url = url
        type(self).totalData +=1
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
        self.appDeadline =None  

            
    def dataParser(self,html,itemUrl,categoryFinder,localNameFinder,titleFinder,descriptionFinder,priceFinder,shipMethod,capacityFinder,compName,imageUrlFinder):
        self.html = bs(html, 'html.parser')
        self.priceFinder = self.html.find(class_=priceFinder).find("span").get_text()
        if "～" in self.priceFinder:
            self.priceFinder = []
            self.capacityFinder = []
            self.temp = self.html.find_all(class_="p-detailAddCart__info")
            for _ in self.temp:
                self.priceChecker = _.find(class_="p-detailAddCart__ttl").find("span").get_text()
                self.capacityChecker =_.get_text().replace(self.priceChecker,"")
                if self.capacityChecker == " ":
                    self.capacityChecker = None
                self.capacityFinder.append(self.capacityChecker)
                self.priceChecker = self.priceChecker.replace("円","")
                self.priceChecker = self.priceChecker.replace(",","")
                self.priceChecker = re.sub(r'\s+', '', self.priceChecker)
                self.priceFinder.append(int(self.priceChecker))

        else:
            self.priceFinder = self.html.find(class_=priceFinder).find("span").get_text()
            # self.priceFinder = re.sub(r'\s+', '', self.priceFinder)

            self.capacityFinder = self.html.find(class_=capacityFinder).get_text().replace(self.priceFinder+str("円"),"")
            self.priceFinder = int(self.priceFinder.replace(",",""))
            # self.capacityFinder = re.sub(r'\s+', '', self.capacityFinder)
            if self.capacityFinder == " ":
                self.capacityFinder = None
        self.categoryFinder = self.html.find(class_=categoryFinder).find_all("li")
        self.parent_category = ""
        for i,_ in enumerate(self.categoryFinder[1:-1]):
            self.temp = _.find("a").get_text()
            self.temp = re.sub(r'のふるさと納税一覧', '', self.temp)
            # self.temp = re.sub(r'\s+', '', self.temp)
            if (i == (len(self.categoryFinder[1:-1]) - 1)):
                self.parent_category += self.temp
            else:
                self.parent_category +=self.temp+"_"
        self.categoryFinderLink = "https://furusatohonpo.jp"+self.categoryFinder[-2].find("a").get("href")
        self.categoryFinder = self.parent_category
        with data_lock:
            if self.categoryFinder not in DataParserClass.category_set:
                DataParserClass.category_list.append({"URL":self.categoryFinderLink,"category":self.categoryFinder})
                DataParserClass.category_set.add(self.categoryFinder)

        self.about = self.html.find(class_="p-detailInfo")
        self.about = self.about.find_all("tr")
        for _ in self.about:
            self.th = _.find("th").get_text()
            # self.th = re.sub(r'\s+', '', self.th)
            if re.match("配送方法",self.th):
                try:
                    self.shipMethod = _.find(shipMethod).get_text()
                    self.shipMethod = re.sub(r'\s+', '', self.shipMethod)
                except:
                    self.shipMethod = None
            if re.match("事業者名",self.th):
                try:
                    self.compName = _.find(compName).get_text()
                    self.compName = re.sub(r'\s+', '', self.compName)
                except:
                    self.compName = None

        try:
            self.stockStatus = self.html.find(class_=stockStatus).find("span").get_text()
            # self.stockStatus =  re.sub(r'\s+', '', self.stockStatus)
        except:
            self.stockStatus =  None
            
        try:
            self.localNameFinder = self.html.find(class_=localNameFinder).get_text()
            # self.localNameFinder =  re.sub(r'\s+', '', self.localNameFinder)
        except:
            self.localNameFinder = None
        try:
            self.titleFinder = self.html.find(class_=titleFinder).get_text()
            # self.titleFinder = re.sub(r'\s+', '', self.titleFinder)
        except:
            self.titleFinder = None
        try:
            self.descriptionFinder = self.html.find(class_=descriptionFinder).get_text()
            # self.descriptionFinder = re.sub(r'\s+', '', self.descriptionFinder)
        except:
            self.descriptionFinder = None

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
            if type(self.priceFinder)== list and type(self.capacityFinder)== list:
                for count, price in enumerate(self.priceFinder):
                    DataParserClass.data.append({"URL":itemUrl+str(f"#{count+1}"),
                                            "category":self.categoryFinder,
                                            "stock_status": self.stockStatus,
                                            "local_name" : self.localNameFinder,
                                            "management_number" :self.managementNumber,
                                            "app_deadline": self.appDeadline,
                                            "title" : self.titleFinder,
                                            "description": self.descriptionFinder,
                                            "price" : price,
                                            "ship_method": self.shipMethod,
                                            "capacity" :self.capacityFinder[count],
                                            "consumption": self.consumption,
                                            "comp_name" : self.compName,
                                            "images" :self.imageList
                                            })

            else:
                DataParserClass.data.append({"URL":itemUrl,
                                            "category":self.categoryFinder,
                                            "stock_status": self.stockStatus,
                                            "local_name" : self.localNameFinder,
                                            "management_number" :self.managementNumber,
                                            "app_deadline": self.appDeadline,
                                            "title" : self.titleFinder,
                                            "description": self.descriptionFinder,
                                            "price" : self.priceFinder,
                                            "ship_method": self.shipMethod,
                                            "capacity" :self.capacityFinder,
                                            "consumption": self.consumption,
                                            "comp_name" : self.compName,
                                            "images" :self.imageList
                                            })
def DataCollectorFunction(data):
    item_url = data
    scrapeURL = DataParserClass(item_url)
    scrapeURL.driver.get(scrapeURL.url)
    logging.info(f"{threading.current_thread().name}) -Scraped_items({DataParserClass.totalData}/{len(ScraperData.item_list)}) -Fetching({item_url})")
    try:
        time.sleep(5)
        scrapeURL.dataParser(html = scrapeURL.driver.page_source,
                           itemUrl = item_url,
                           categoryFinder = "c-contents", 
                           localNameFinder = "p-detailName__municipality",
                           titleFinder = "p-detailName__ttl",
                           descriptionFinder = "p-detailDescription__txt",
                           priceFinder = "p-detailName__price",
                           shipMethod = "td",
                           capacityFinder = "p-detailAddCart__info",
                           compName = "td",
                           imageUrlFinder = "slick-track")
    except:
        logging.info(f"{threading.current_thread().name}) - Unable to load the element")
    finally:
        scrapeURL.driver.quit()


print(f"{threading.current_thread().name}) -Scraping has been started...Site : Furusato Honpo	Link : https://furusatohonpo.jp/")
start = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Scraping has been started...Site : Furusato Honpo	Link : https://furusatohonpo.jp/")
# site=ScraperData("https://furusatohonpo.jp/donate/s/?")
site=ScraperData("https://furusatohonpo.jp/donate/s/?categories=5")
site.dataParser(element_tag="c-itemList")
data=list(site.item_list)
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} for fetching {len(data)} URLs")

unique_data = set()
for _ in data:
    if _ not in unique_data:
        unique_data.add(_)
    else:
        index = data.index(_)
        data.pop(index)
        logging.info(f"{threading.current_thread().name} -Pre Cleaning ... Duplicate URL detected ")

start = time.perf_counter()
with concurrent.futures.ThreadPoolExecutor(max_workers=5,thread_name_prefix='Fetching_Item_Data') as executor:
    futures = [executor.submit(DataCollectorFunction, datum) for datum in data]
    for future in concurrent.futures.as_completed(futures):
        if future.result():
            logging.info(f"{threading.current_thread().name}) -{future.result()}")
final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  scrape  {len(DataParserClass.data)} items data")

unique_data = set()
for _ in DataParserClass.data:
    if _['URL'] not in unique_data:
        unique_data.add(_['URL'])
    else:
        index = DataParserClass.data.index(_)
        DataParserClass.data.pop(index)
        logging.info(f"{threading.current_thread().name} -Post Cleaning ... Duplicate URL detected ")

start = time.perf_counter()
agt_cd = "FHP"
mydb = connect.connect(host="localhost",user="user",password="password",database="his_furusato")
mycursor = mydb.cursor()
for  datum in DataParserClass.category_list:
    try:
        mycursor.execute("INSERT INTO m_agt_catgy (agt_catgy_url,agt_catgy_nm,agt_cd)VALUES (%s,%s,%s)",(datum["URL"],datum["category"],agt_cd))
        mydb.commit()
    except connect.errors.DataError as error:
        logging.info(f"{threading.current_thread().name}) -Data failed to be saved because {error} {datum['URL']} {datum['category']}")    
    except connect.errors.IntegrityError as error:
        logging.info(f"{threading.current_thread().name}) -Data failed to be saved because {error} {datum['URL']}{datum['category']}")

def val(item,item_type):
    if item_type == "app_deadline":
        try:
            item = item[:200]
        except:
            item = None

    if item_type == "comp_name":
        try:
            item = item[:30]
        except:
            item = None    
    return item

for  datum in DataParserClass.data:
    try:
        mycursor.execute("INSERT INTO t_agt_mchan (agt_mchan_url,agt_city_nm,agt_mchan_cd,mchan_nm,mchan_desc,appli_dline,price,capacity,mchan_co,agt_cd) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (datum["URL"],datum["local_name"],datum["management_number"],datum["title"],datum["description"],val(datum["app_deadline"],"app_deadline"),datum["price"],datum["capacity"],val(datum["comp_name"],"comp_name"),agt_cd))
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
    except connect.errors.DataError as error:
        logging.warning(f"{threading.current_thread().name}) -Data failed to be saved because {error} ") 
        logging.warning(f'{datum["URL"]},{datum["local_name"]},{datum["management_number"]},{datum["title"]},{datum["description"]},{val(datum["app_deadline"],"app_deadline")},{datum["price"]},{datum["capacity"]},{val(datum["comp_name"],"comp_name")},{agt_cd}')
    except connect.errors.IntegrityError as error:
        logging.warning(f"{threading.current_thread().name}) -Data failed to be saved because {error} ")
        logging.warning(f'{datum["URL"]},{datum["local_name"]},{datum["management_number"]},{datum["title"]},{datum["description"]},{val(datum["app_deadline"],"app_deadline")},{datum["price"]},{datum["capacity"]},{val(datum["comp_name"],"comp_name")},{agt_cd}')

final = time.perf_counter()
logging.info(f"{threading.current_thread().name}) -Took {round((final-start),2)} seconds to  save  {len(DataParserClass.data)} items data")

