from web_driver import ScraperCategory
import time
import threading

start = time.perf_counter()
site1= ScraperCategory("https://furu-po.com/")
site1.driver.get(site1.url)
site1.displaySiteInfo()
site1.categoryParser(html= site1.driver.page_source, elementTag = "popover")
final = time.perf_counter()
for _ in site1.categoryList:
   print(_)




