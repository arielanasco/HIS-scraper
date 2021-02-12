# This is the Scraper code for https://furu-po.com/ website
from web_driver import WebDriver
from time import sleep
from selenium.webdriver.common.keys import Keys

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
    while True:
        dataResult = site1.listParser(html = site1.driver.page_source, elementContainer = "itemlist", category=data[1],dataResult = dataResult)
        if site1.driver.find_element_by_xpath("//*[@id='form_events']/section/div[2]/div[1]/div/div[2]/div[3]/ul/li[3]/a").send_keys(Keys.ENTER):
            print(f"Scraping {site1.driver.current_url}")
        else:
            break
            print(f"Done scraping for category {data[1]}")
# for _ in dataResult:
#     print(_)
