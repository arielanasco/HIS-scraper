from web_driver import ScraperCategory,ScraperList
import time
import threading


def ItemCollector(url_category):
   scrapeURL = ScraperList(url_category)
   scrapeURL.driver.get(scrapeURL.url)
   print(scrapeURL.driver.title)

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
url = ["https://furu-po.com/","https://google.com","https://mifurusato.jp/item_list.html"]
start = time.perf_counter()
t1 = threading.Thread(target = ItemCollector ,args=(url[0],))
t2 = threading.Thread(target = ItemCollector ,args=(url[1],))
t3 = threading.Thread(target = ItemCollector ,args=(url[2],))
t1.start()
t2.start()
t3.start()
t1.join()
t2.join()
t3.join()
final = time.perf_counter()
print(f"Took {round((final-start),2)} to complete to thread ")

