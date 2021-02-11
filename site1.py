# This is the Scraper code for https://furu-po.com/ website
from web_driver import WebDriver
from time import sleep
class Site1(WebDriver):
    pass

site1= Site1("https://furu-po.com/")
site1.driver.get(site1.url)
site1.displaySiteInfo()
for data in site1.categoryFinder(html= site1.driver.page_source, elementTag = "popover"):         # elementTag is based on the <ul> before the <li>
    #site1.driver.get(data[0])                                                                     # data = [["https://site1.com", "category"]..["https://site2.com", "category2"]]
    #sleep(3)
    print(data[0])

site1.driver.close()
