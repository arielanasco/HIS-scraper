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
        try:
            self.driver.get(self.url)
            print(self.driver.current_url)
        except:
            raise RuntimeError('Error initializing the webdriver')

    def initializeScroller(self):
        # # this will scroll down until the end of pages  so that all pages tag will be fetched
        # lenOfPage = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        # match = False
        # while (match == False):
        #     lastCount = lenOfPage
        #     sleep(3)
        #     lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        #     print(now_checker(),"INFO:SEARCHING PAGES")
        #     if lastCount == lenOfPage:
        #         match = True
        #         print(now_checker(),"INFO:SEARCHED COMPLETED")
        pass
    
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

