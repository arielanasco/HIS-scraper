from web_driver import WebDriver


class Site1(WebDriver):
   pass
site1= Site1("https://furu-po.com/")
site1.driver.get(site1.url)
site1.displaySiteInfo()

categorylist = site1.categoryParser(html= site1.driver.page_source, elementTag = "popover")

for _ in categorylist:
   print(_)