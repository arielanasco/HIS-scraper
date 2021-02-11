# This is the Scraper code for https://mifurusato.jp/item_list.html website
from web_driver import WebDriver
from bs4 import BeautifulSoup as bs
import re

class Site4(WebDriver):
    def categoryFinder(self,**kwargs):
        self.collector = []
        self.elementTag = kwargs.get("elementTag")
        self.html = bs(kwargs.get("html"), 'html.parser')
        self.container = self.html.find(class_="category_list01")
        self.category = self.container.find(class_=self.elementTag)
        self.liTag = self.category.li
        while True:
            # self.categoryData = re.sub(r'\([0-9]*\)', '', self.liTag.find("a").get_text())
            self.categoryData = re.sub(r'\([^()]*\)', '', self.liTag.find("a").get_text())
            self.categoryData = re.sub(r'\W+', '', self.categoryData)
            self.collector.append([self.liTag.find("a").get("href"),self.categoryData])
            if self.liTag.find_next_sibling():
                self.liTag = self.liTag.find_next_sibling()
            else:
                break
        return self.collector

site4= Site4("https://furusato-izumisano.jp/items/ranking.php")
site4.driver.get(site4.url)
site4.displaySiteInfo()
listcategory = site4.categoryFinder(html= site4.driver.page_source, elementTag = "slide-child")
site4.driver.close()