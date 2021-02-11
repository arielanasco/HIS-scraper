# This is the Scraper code for https://www.satofull.jp/ website

from web_driver import WebDriver

class Site2(WebDriver):
    pass

site2= Site2("https://www.satofull.jp/")
site2.driver.get(site2.url)
site2.displaySiteInfo()
listcategory = site2.categoryParser(html= site2.driver.page_source, elementTag = "SideBox__list--item")
site2.driver.close()
