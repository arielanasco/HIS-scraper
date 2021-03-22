from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import warnings
from time import sleep
from bs4 import BeautifulSoup as bs
import re
from random import sample 
from selenium.common.exceptions import TimeoutException
import time

import requests
from bs4 import BeautifulSoup as bs
import shutil
import os 
from PIL import Image

import mysql.connector as connect


class WebDriver:
    warnings.filterwarnings('ignore')

    def __init__(self,url):
        self.url = url
        self.userAgentList = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
        "Mozilla/5.0 CK={} (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0"
        ]
        self.options = Options()
        self.options.add_argument('--no-sandbox')
        self.options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images":2,
                                            "profile.default_content_setting_values.notifications":2,
                                            "profile.managed_default_content_settings.stylesheets":2,
                                            "profile.managed_default_content_settings.javascript":1,
                                            "profile.managed_default_content_settings.plugins":1,
                                            "profile.managed_default_content_settings.popups":2,
                                            "profile.managed_default_content_settings.geolocation":2,
                                            "profile.managed_default_content_settings.media_stream":2,
                                            })

                                            #"profile.managed_default_content_settings.cookies":2,

        self.options.add_argument("--headless")
        self.options.add_argument(f'--user-agent="{sample(self.userAgentList,1)[0]}"')
        self.driver = webdriver.Chrome(options=self.options)

    def displaySiteInfo(self):
        return f"Target URL: {self.driver.current_url}" , f"User-Agent: {self.driver.execute_script('return navigator.userAgent;')}"



# class SaveData:
#     img_dir_list = []

#     def __init__(self):
#         self.mydb = connect.connect(host="localhost",user="user",password="password",database="his_furusato")


#     def query_db_save_catgy(self,data,agt_cd):
#         self.mycursor = self.mydb.cursor()
#         for  datum in data:
#             self.mycursor.execute("INSERT INTO m_agt_catgy (agt_catgy_url,agt_catgy_nm,agt_cd)VALUES (%s,%s,%s)",(datum["URL"],datum["category"],agt_cd))
#         self.mydb.commit()

#     def query_db_save_item(self,data,agt_cd,cwd,site_name):
#         self.mycursor = self.mydb.cursor()
#         for  datum in data:
#             print("Saving to database")
#             self.mycursor.execute("INSERT INTO t_agt_mchan (agt_mchan_url,agt_city_nm,agt_mchan_cd,mchan_nm,mchan_desc,appli_dline,price,capacity,mchan_co,agt_cd) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
#             (datum["URL"],datum["local_name"],datum["management_number"],datum["title"],datum["description"],datum["app_deadline"],datum["price"],datum["capacity"],datum["comp_name"],agt_cd))
#             self.mydb.commit()
#             if type(datum["category"]) == list:
#                 for cat in datum["category"][:8]:
#                     self.mycursor.execute("UPDATE  t_agt_mchan SET agt_catgy_nm%s = %s  WHERE agt_mchan_url = %s",(datum['category'].index(cat)+1,cat,datum["URL"]))
#             else:
#                 self.mycursor.execute("UPDATE  t_agt_mchan SET agt_catgy_nm1 = %s WHERE agt_mchan_url = %s",(datum["category"],datum["URL"]))
#             for img_link in datum["images"]:
#                 print("Downnload  images")
#                 self.response = requests.get(img_link, stream=True)
#                 self.dir_name= os.path.join(cwd,"scraper",site_name,datum["category"],datum["title"])
#                 if not os.path.exists(self.dir_name):
#                     os.makedirs(self.dir_name)
#                 self.img_link = img_link.split("/")
#                 self.dir_file = os.path.join(self.dir_name,self.img_link[-1])
#                 with open(self.dir_file, 'wb') as out_file:
#                     shutil.copyfileobj(self.response.raw, out_file)
#                 del self.response
#                 self.img_dir_list.append(self.dir_file)        
#             for  img in self.img_dir_list[:5]:
#                 print("Saving  images")
#                 self.mycursor.execute("UPDATE  t_agt_mchan SET mchan_img_url%s = %s  WHERE agt_mchan_url = %s",(img_dir_list.index(img)+1,img,datum["URL"]))
#             self.mydb.commit()
#             self.img_dir_list = []

