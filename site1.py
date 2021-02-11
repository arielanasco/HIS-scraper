# This is the Scraper code for https://furu-po.com/ website
from web_driver import WebDriver
from time import sleep
from bs4 import BeautifulSoup as bs

class Site1(WebDriver):
    pass

site1= Site1("https://furu-po.com/")
site1.driver.get(site1.url)
site1.displaySiteInfo()
data = []
for data in site1.categoryParser(html= site1.driver.page_source, elementTag = "popover")
    site1.driver.get(data[0])
    while True:
        sleep(3)
        data.append(site1.listParser(elementContainer = "itemlist"))
        if site1.initScroll():
            if initNextPage(nextButtonName="next",elementTag="class"):
                print(site1.driver.current_url) 
            else:
                html = bs(site1.driver.page_source, 'html.parser')
                nextTag = html.find(class_ = "next")
                    if !nextTag.a:
                        print("No next page")
                        break
        else:
            raise Exception ("Error initScroll()")
# site1.driver.close()
