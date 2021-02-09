from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import warnings
from time import sleep


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
            raise RuntimeError ("Error Scrolling...")
    def initializeNextPage(self):
        pass

    def saveData(self):
        pass

    def localNameFinder(self):
        pass
    
    def categoryFinder(self):
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

