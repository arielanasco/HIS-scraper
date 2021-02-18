from web_driver import ScraperCategory,ScraperList
import time
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

def ItemCollector(url_category):
   scrapeURL = ScraperList(url_category)
   scrapeURL.driver.get(scrapeURL.url)
   print(scrapeURL.driver.title)
   while True:
      try:
         itemlist = WebDriverWait(scrapeURL.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "itemlist"))
         )
         itemList = scrapeURL.listParser(html = scrapeURL.driver.page_source, elementContainer = "itemlist", category=url_category)
         try: 
            nextButton = scrapeURL.driver.find_element_by_xpath("//*[@id='form_events']/section/div[2]/div[1]/div/div[2]/div[3]/ul/li[3]/a")
            nextButton.send_keys(Keys.ENTER)
            print("Next page detected")
         except NoSuchElementException:
            print("No next page detected")
            while True:
               if scrapeURL.isNotActive:
                  scrapeURL.isNotActive = False
                  for _ in itemList:
                     scrapeURL.data.append(_)
                  break
            break
      except:
         scrapeURL.driver.quit()
         raise Exception (" Unable to locate the element")

start = time.perf_counter()
site1= ScraperCategory("https://furu-po.com/")
site1.driver.get(site1.url)
site1.displaySiteInfo()
site1.categoryParser(html= site1.driver.page_source, elementTag = "popover")
site1.driver.close()
final = time.perf_counter()

for _ in site1.categoryList:
   print(_)

print(f"Took {round((final-start),2)} to complete scraping")

url = ["https://furu-po.com/goods_list/280","https://furu-po.com/goods_list/7","https://mifurusato.jp/item_list.html"]
start = time.perf_counter()
t1 = threading.Thread(target = ItemCollector ,args=(url[0],))
t2 = threading.Thread(target = ItemCollector ,args=(url[1],))
t1.start()
t2.start()
t1.join()
t2.join()
final = time.perf_counter()
print(f"Took {round((final-start),2)} to complete to thread ")

