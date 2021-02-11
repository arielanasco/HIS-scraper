from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import warnings
from time import sleep
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from random import sample 



class WebDriver:
    self.userAgentList = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393"
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
    self.warnings.filterwarnings('ignore')
    def __init__(self,url):
        self.url = url
        self.driver = webdriver.Chrome(options=self.options)

    def displaySiteInfo(self):
        print(f"Target URL: {self.driver.current_url}")
        print(f"User-Agent: {self.driver.execute_script('return navigator.userAgent;')}")

    def initScroll(self):
        try:
            self.lenOfPage = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            self.match = False
            while (self.match == False):
                self.lastCount = self.lenOfPage
                sleep(3)
                self.lenOfPage = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if self.lastCount == self.lenOfPage:
                    self.match = True
            return True
        except :
            return False

    def initNextPage(self,nextButtonName,elementTag="name"):
        self.elementTag = elementTag
        self.nextButtonName = nextButtonName
        if self.elementTag == "name":
            self.driver.find_element_by_name(self.nextButtonName).send_keys(Keys.ENTER)
            return True
        if self.elementTag == "class":
            self.driver.find_element_by_class_name(self.nextButtonName).send_keys(Keys.ENTER)
            return True
        if self.elementTag == "id":
            self.driver.find_element_by_id(self.nextButtonName).send_keys(Keys.ENTER)
            return True
        return False

    def categoryFinder(self,**kwargs):
        self.collector = []
        self.elementTag = kwargs.get("elementTag")
        self.html = bs(kwargs.get("html"), 'html.parser')
        self.category = self.html.find(class_=self.elementTag)
        self.liTag = self.category.li
        while True:
            self.categoryData = re.sub(r'\([0-9]*\)', '', self.liTag.find("a").get_text())
            self.categoryData = re.sub(r'\W+', '', self.categoryData)
            self.collector.append([self.liTag.find("a").get("href"),self.categoryData])
            if self.liTag.find_next_sibling():
                self.liTag = self.liTag.find_next_sibling()
            else:
                break
        return self.collector

    def saveData(self):
        pass

    def localNameFinder(self):
        pass

    def titleFinder(self):
        pass
    def descriptionFinder(self):
        pass

    def priceFinder(self):
        pass

    def capacityFinder(self):
        pass

    def imageUrlFinder(self):
        pass

