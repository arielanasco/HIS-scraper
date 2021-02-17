from web_driver import WebDriver
import time
import threading
start = time.perf_counter()
class Site1(WebDriver):
   categorylist = []
   isActive = False
   data = []

   def __init__(self, url):
      self.url = url
      super().__init(url)



site1= Site1("https://furu-po.com/")
site1.driver.get(site1.url)
site1.displaySiteInfo()
# def main:      
#    site1= Site1("https://furu-po.com/")
#    site1.driver.get(site1.url)
#    site1.displaySiteInfo()

# finish = time.perf_counter()
# for _ in categorylist:
#    print(_)
# print(f"Took {round((finish-start),2)} to complete the script")

# url = ["https://furu-po.com/","https://gooogle.com","https://mifurusato.jp/item_list.html"]

# t1 = threading.Thread(target = Test ,args=(url[0],))
# t2 = threading.Thread(target = Test ,args=(url[1],))
# t1.start()
# t2.start()
# t1.join()
# t2.join()
# print("Successed!")
