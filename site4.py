# This is the Scraper code for https://mifurusato.jp/item_list.html website

from web_driver import WebDriver

class Site4(WebDriver):
    pass

site4= Site4("https://furusato-izumisano.jp/items/ranking.php")
site4.driver.get(site4.url)
site4.driver.current_url
listcategory = site4.categoryFinder(html= site4.driver.page_source, elementTag = "category_list01")
