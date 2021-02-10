# This is the Scraper code for https://mifurusato.jp/item_list.html website

from web_driver import WebDriver

class Site3(WebDriver):
    pass

site3= Site3("https://mifurusato.jp/item_list.html")
site3.driver.get(site3.url)
site3.driver.current_url
listcategory = site3.categoryFinder(html= site3.driver.page_source, elementTag = "l_footer_catefory")
