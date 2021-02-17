from web_driver import Scraper
import time
import threading

def main():
   start = time.perf_counter()
   site1= Scraper("https://furu-po.com/")
   site1.driver.get(site1.url)
   site1.displaySiteInfo()
   final = time.perf_counter()


if __name__ == "__main__":
   main()




