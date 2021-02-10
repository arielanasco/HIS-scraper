from web_driver import WebDriver

site1= WebDriver("https://furu-po.com/")
site1.driver.get(site1.url)
site1.driver.current_url
listcategory = site1.listcategory(html= site1.driver.page_source,elementTag="category")



