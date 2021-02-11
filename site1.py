# This is the Scraper code for https://furu-po.com/ website
from web_driver import WebDriver
from time import sleep
class Site1(WebDriver):
    pass

site1= Site1("https://furu-po.com/")
site1.driver.get(site1.url)
site1.displaySiteInfo()
site1.categoryParser(html= site1.driver.page_source, elementTag = "popover")
List = site1.listParser()

site1.driver.close()
