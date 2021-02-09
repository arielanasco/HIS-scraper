from web_driver import WebDriver

site1= WebDriver("https://google.com/")
site1.displaySiteInfo()
driver = site1.initializeBrowser()
print(driver.title)