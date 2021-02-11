# This is the Scraper code for https://www.satofull.jp/ website

from web_driver import WebDriver

class Site2(WebDriver):
    pass

site2= Site2("https://www.satofull.jp/")
site2.displaySiteInfo()
site2.driver.get(site2.url)
listcategory = site2.categoryFinder(html= site2.driver.page_source, elementTag = "SideBox__list--item")