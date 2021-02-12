# This is the Scraper code for https://furu-po.com/ website
from web_driver import WebDriver
from time import sleep

class Site1(WebDriver):
    pass

site1= Site1("https://furu-po.com/")
site1.driver.get(site1.url)
site1.displaySiteInfo()
dataResult = []
categorylist = site1.categoryParser(html= site1.driver.page_source, elementTag = "popover")
for data in categorylist:
    print(f"Scraping....{data[0]}")
    site1.driver.get(data[0])
    dataResult = site1.listParser(html = site1.driver.page_source, elementContainer = "itemlist", category=data[1],dataResult = dataResult)
for _ in dataResult:
    print(_)
