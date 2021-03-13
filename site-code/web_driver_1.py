import requests
from random import sample
class WebDriver:
    def __init__(self):
        self.userAgentList = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
        "Mozilla/5.0 CK={} (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0"
        ]
        self.requests = requests
        self.headers = {"User-Agent": f"{sample(self.userAgentList,1)[0]}","Content-Type": "text/html"}
    
    def get(self,url):
        with requests.session() as s:
            self.html = s.get(url, headers = self.headers)
        return self.html             

    def displaySiteInfo(self):
        return f"User-Agent: {self.headers}"