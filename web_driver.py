# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import TimeoutException,NoSuchElementException
# from bs4 import BeautifulSoup as bs
# from time import sleep
# import pandas as pd
# import json
# import hashlib
# from datetime import datetime as stamp
# from datetime import timedelta
# import datetime
# from datetime import date
# from datetime import time
# from sqlalchemy import create_engine
# import mysql.connector as connect
# import warnings
# import sys
class WebDriver:
    def __init__(self,url):
        self.url = url
    
    def displaySiteInfo(self):
        print(f"Scraping {self.url} ...")

    def initializeBrowser(self):
        pass

    def nextPageChecker(self):
        pass

    def saveData(self):
        pass

    def localNameFinder(self):
        pass
    
    def categoryFinder(self):
        pass

    def titleFinder(self):
        pass
    def descriptionFinder(self):
        pass

    def priceFinder(self):
        pass

    def capacityFinder(self):
        pass

    def imageUrlFinder(self):
        pass

