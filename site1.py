# This is the Scraper code for https://furu-po.com/ website
from web_driver import WebDriver
from time import sleep
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.keys import Keys

class Site1(WebDriver):
    pass

site1= Site1("https://furu-po.com/")
site1.driver.get(site1.url)
site1.displaySiteInfo()
dataResult = []
categorylist = site1.categoryParser(html= site1.driver.page_source, elementTag = "popover")
site1.driver.get(categorylist[0][0])
print(site1.driver.current_url)
# site1.listParser(elementContainer = "itemlist",URL= categorylist[0][0], category=categorylist[0][1])
# # site1.driver.close()
