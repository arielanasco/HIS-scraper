from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import warnings

class WebDriver:
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    warnings.filterwarnings('ignore')

    def __init__(self,url):
        self.url = url
    
    def displaySiteInfo(self):
        print(f"Scraping {self.url} ...")

    def initializeBrowser(self):
        self.driver.get(self.url)
        return self.driver.title()

    def nextPageChecker(self):
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

