import requests
from random import sample
import time
class WebDriver:
    def __init__(self):
        self.userAgentList = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
        "Mozilla/5.0 CK={} (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0"
        ]
        self.headers = {"User-Agent": f"{sample(self.userAgentList,1)[0]}","Content-Type": "text/html","keep_alive":"False"}
        self.proxies = {"http": "http://13.230.110.97:8888" ,'https': 'http://13.230.110.97:8888',}
    
    def get(self,url):
        with requests.session() as s:
            s.headers = self.headers
            s.proxies = self.proxies
            self.html = requests.get(url,headers = self.headers,proxies = self.proxies)
        return self.html


# scrapeURL =WebDriver()
# for _ in range(20):
#     scrapeURL.get("http://169.254.169.254/latest/meta-data/public-ipv4").text
#     time.sleep(3)
