from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import warnings
from time import sleep
from bs4 import BeautifulSoup as bs

class WebDriver:
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})
    # options.add_argument("--headless")
    warnings.filterwarnings('ignore')
    driver = webdriver.Chrome(options=options)

    def __init__(self,url):
        self.url = url

    def displaySiteInfo(self):
        print(f"Target URL: {self.driver.current_url}")

    def initializeScroll(self):
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

    def initializeNextPage(self,nextButtonName,elementTag="name"):
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

    def categoryFinder(self,*args, **kwargs):
        self.elementTag = elementTag
        self.html = bs(html, 'html.parser')
        self.container = self.html.find()

        # if self.elementTag == "class":
        #     self.container = self.driver.find_element_by_class_name(elementContainerValue)
        #     self.compiled = self.container.find_elements_by_tag_name(elementIndividual)            
        #     # container = self.driver.find_element_by_class_name(elementContainerValue)
            # self.container = self.container.find_elements_by_tag_name(elementIndividual)

    def saveData(self):
        pass

    def localNameFinder(self):
        pass
    
    def listParser(self):
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

