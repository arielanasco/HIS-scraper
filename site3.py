# This is the Scraper code for https://mifurusato.jp/item_list.html website
from web_driver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs

class Site3(WebDriver):
    def listParser(self,html,elementContainer,category,dataResult):
        self.itemList = dataResult
        self.category = category
        self.elementContainer = elementContainer
        self.html = bs(html, 'html.parser')
        # self.container = self.html.find('div', attrs ={'id':self.elementContainer})
        self.container_ =  self.html.find('ul', attrs ={'class':'item_list l_grid_row'})
        self.ChildElement = self.container_.find_next()
        print(self.ChildElement)
        while True:
            self.itemList.append([self.ChildElement.find("a").get("href"),self.category])
            if self.ChildElement.find_next_sibling():
                self.ChildElement = self.ChildElement.find_next_sibling()
            else:
                break    
        return self.itemList
        
site3= Site3("https://mifurusato.jp/item_list.html")
site3.driver.get(site3.url)
site3.displaySiteInfo()
dataResult = []
categorylist = site3.categoryParser(html= site3.driver.page_source, elementTag = "l_footer_catefory")
for data in categorylist:
    print(f"Scraping....{data[0]}")
    site3.driver.get(data[0])
    if site3.initScroll():
        print("Scrolling down...")
    else:
        print("Already scrolled down")
    while True:
        element_present = EC.presence_of_element_located((By.ID, "list"))
        WebDriverWait(site3.driver, 3).until(element_present)
        dataResult = site3.listParser(html = site3.driver.page_source, elementContainer = "list", category=data[1], dataResult = dataResult)
        try: 
            nextButton = site3.driver.find_element_by_xpath("//*[@id='list']/div[2]/span[6]/a")
            nextButton.send_keys(Keys.ENTER)
            print(f"Scraping {site3.driver.current_url}")
        except NoSuchElementException:
            print(f"Done scraping for category {data[1]}")
            break
        if len(dataResult) == 100:
            break
    print(f"Collected URL: {len(dataResult)}")
    if len(dataResult) == 100:
        break

site3.driver.close()