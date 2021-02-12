# This is the Scraper code for https://furu-po.com/ website
from web_driver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    if site1.initScroll():
        print("Scrolling down...")
    else:
        print("Already scrolled down")
    while True:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, "itemlist"))
        WebDriverWait(site1.driver, 3).until(element_present)
        dataResult = site1.listParser(html = site1.driver.page_source, elementContainer = "itemlist", category=data[1],dataResult = dataResult)
        try: 
            nextButton = site1.driver.find_element_by_xpath("//*[@id='form_events']/section/div[2]/div[1]/div/div[2]/div[3]/ul/li[3]/a")
            nextButton.send_keys(Keys.ENTER):
            print(f"Scraping {site1.driver.current_url}")
        except NoSuchElementException::
            print(f"Done scraping for category {data[1]}")
            break


# for _ in dataResult:
#     print(_)


# https://furu-po.com/goods_list/280