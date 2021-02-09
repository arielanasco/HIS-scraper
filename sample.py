from web_driver import WebDriver

site2= WebDriver("https://furu-po.com/")
site2.driver.get(site1.url)
site1.displaySiteInfo()
site1.initializeScroll()

