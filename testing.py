from web_driver import WebDriver
import time
import threading
start = time.perf_counter()
class Site1(WebDriver):
   isActive = False
   data = []

   def __init__(self,url):
      super().__init__(url)
   def Test(self, url_category):
      print(url_category)
      self.driver.get(url_category)
      
site1= Site1("https://furu-po.com/")
site1.driver.get(site1.url)
site1.displaySiteInfo()

categorylist = site1.categoryParser(html= site1.driver.page_source, elementTag = "popover")
finish = time.perf_counter()
for _ in categorylist:
   print(_)
print(f"Took {round((finish-start),2)} to complete the script")

url = ["https://furu-po.com/","https://gooogle.com","https://mifurusato.jp/item_list.html"]

t1 = threading.Thread(target = site1.Test ,args=(url[0],))
t2 = threading.Thread(target = site1.Test ,args=(url[1],))
t1.start()
t2.start()
t1.join()
t2.join()
print("Successed!")
