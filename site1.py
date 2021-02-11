# This is the Scraper code for https://furu-po.com/ website
from web_driver import WebDriver

class Site1(WebDriver):
    pass

site1= Site1("https://furu-po.com/")
site1.driver.get(site1.url)
site1.displaySiteInfo()
# elementTag is based on the <ul> before the <li>
listcategory = site1.categoryFinder(html= site1.driver.page_source, elementTag = "popover")
site1.driver.close()
