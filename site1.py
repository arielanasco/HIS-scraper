# This is the Scraper code for https://furu-po.com/ website
from web_driver import WebDriver

class Site1(WebDriver):
    pass

site1= Site1("https://furu-po.com/")
site1.driver.get(site1.url)
site1.driver.current_url
listcategory = site1.categoryFinder(html= site1.driver.page_source, elementTag = "popover")
