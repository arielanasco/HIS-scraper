from web_driver import WebDriver

site1= WebDriver("https://furu-po.com/")
site1.driver.get(site1.url)
site1.driver.current_url
listcategory = site1.categoryFinder(html= site1.driver.page_source, elementTag = "popover")

site2= WebDriver("https://www.satofull.jp/")
site2.driver.get(site2.url)
site2.driver.current_url
listcategory = site2.categoryFinder(html= site2.driver.page_source, elementTag = "SideBox__list--item")
class="l_footer_catefory"


site3= WebDriver("https://mifurusato.jp/item_list.html")
site3.driver.get(site3.url)
site3.driver.current_url
listcategory = site3.categoryFinder(html= site3.driver.page_source, elementTag = "l_footer_catefory")

for _ in listcategory:
    print(_)