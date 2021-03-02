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
                                            "profile.managed_default_content_settings.cookies":2,
                                            "profile.managed_default_content_settings.javascript":1,
                                            "profile.managed_default_content_settings.plugins":1,
                                            "profile.managed_default_content_settings.popups":2,
                                            "profile.managed_default_content_settings.geolocation":2,
                                            "profile.managed_default_content_settings.media_stream":2,
                                            })
        self.options.add_argument("--headless")
        self.options.add_argument(f'--user-agent="{sample(self.userAgentList,1)[0]}"')
        self.driver = webdriver.Chrome(options=self.options)

    def get(self):
        t= time.time()
        self.driver.set_page_load_timeout(5)
        try:
            self.driver.get(self.url)
        except TimeoutException:
            self.driver.execute_script("window.stop();")

    def get_page_source(self):
        return self.driver.page_source(self.url)

    def displaySiteInfo(self):
        return f"Target URL: {self.driver.current_url}" , f"User-Agent: {self.driver.execute_script('return navigator.userAgent;')}"

    
    
# class ScraperCategory(WebDriver):
#     categoryList = []

#     def __init__(self, url):
#         self.url = url
#         super().__init__()

#     def categoryParser(self,**kwargs):
#         self.elementTag = kwargs.get("elementTag")
#         self.html = bs(kwargs.get("html"), 'html.parser')
#         self.category = self.html.find(class_=self.elementTag)
#         self.liTag = self.category.li
#         while True:
#             self.categoryData = re.sub(r'\([^()]*\)', '', self.liTag.find("a").get_text())
#             self.categoryData = re.sub(r'\W+', '', self.categoryData)
#             ScraperCategory.categoryList.append([self.liTag.find("a").get("href"),self.categoryData])
#             if self.liTag.find_next_sibling():
#                 self.liTag = self.liTag.find_next_sibling()
#             else:
#                 break

# class ScraperList(WebDriver):
#     isNotActive = True
#     data = []

#     def __init__(self, url):
#         self.url = url
#         self.itemList = []
#         super().__init__()

#     def listParser(self,html,elementContainer):
#         self.elementContainer = elementContainer
#         self.html = bs(html, 'html.parser')
#         self.container = self.html.find(class_=self.elementContainer)
#         self.ChildElement = self.container.find_next()
#         while True:
#             self.itemList.append(self.ChildElement.find("a").get("href"))
#             if self.ChildElement.find_next_sibling():
#                 self.ChildElement = self.ChildElement.find_next_sibling()
#             else:
#                 break