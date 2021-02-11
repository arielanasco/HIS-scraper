# This is the Scraper code for https://furu-po.com/ website
from web_driver import WebDriver
from time import sleep
from bs4 import BeautifulSoup as bs

class Site1(WebDriver):
    pass

site1= Site1("https://furu-po.com/")
site1.driver.get(site1.url)
site1.displaySiteInfo()
dataResult = []
for data in site1.categoryParser(html= site1.driver.page_source, elementTag = "popover"):
    site1.driver.get(data[0])
    while True:
        sleep(3)
        dataResult.append(site1.listParser(elementContainer = "itemlist",URL= data[0], category=data[1]))
        if site1.initScroll():
            if site1.driver.find_element_by_xpath("//*[@id='form_events']/section/div[2]/div[1]/div/div[2]/div[3]/ul/li[3]/a").click():
                print(site1.driver.current_url)
            else:
                html = bs(site1.driver.page_source, 'html.parser')
                nextTag = html.find(class_ = "next")
                if not nextTag.a:
                    print("No next page")
                    break            
            # if site1.initNextPage(nextButtonName="next",elementTag="class"):
            #     print(site1.driver.current_url) 
            # else:
            #     html = bs(site1.driver.page_source, 'html.parser')
            #     nextTag = html.find(class_ = "next")
            #     if not nextTag.a:
            #         print("No next page")
            #         break
        else:
            raise Exception ("Error initScroll()")
# site1.driver.close()
