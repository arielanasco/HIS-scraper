import queue
import threading
import time
import requests
# Class
class MultiThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print(f"{threading.current_thread().name}")
        process_queue()

# Process thr queue
def process_queue():
    while True:
        try:
            site = my_queue.get(block=False)
        except queue.Empty:
            return
        else:
            get_web(site)
            time.sleep(2)

# function to multiply
def get_web(site):
    x = requests.get(site)
    print(f"{threading.current_thread().name} thread handled {site}:{x.status_code}")


# Input variables
input_values = [
                'https://w3schools.com',
                'https://google.com',
                'https://facebook.com',
                'https://github.com',
                'https://youtube.com',
                'https://apple.com',
                'https://en.wikipedia.org',
                'https://docs.google.com',
                'https://mozilla.org',
                'https://cloudflare.com',
                'https://twitter.com'
                ]

# fill the queue
my_queue = queue.Queue()
for x in input_values:
    my_queue.put(x)
# initializing and starting 3 threads
thread1 = MultiThread('First')
thread2 = MultiThread('Second')
thread3 = MultiThread('Third')


# Start the threads
thread1.start()
thread2.start()
thread3.start()



# Join the threads
thread1.join()
thread2.join()
thread3.join()


# import requests
# from bs4 import BeautifulSoup as bs
# import shutil
# import os 
# from PIL import Image


# # res = requests.get("https://furu-po.com/goods_detail.php?id=664459")
# # html = bs(res.text, 'html.parser')
# # img = html.find(class_="item_info_slider").find_all(class_="slide-item")
# # # img = html.find(class_="slick-track")
# # print(img)
# # for _ in img:
# #     print(_)

# import logging
# logging.basicConfig(format='[%(asctime)s](%(levelname)s@%(message)s', datefmt='%d-%b-%y %H:%M:%S')
# logger = logging.getLogger(__name__)
# logging.debug("This will get logged")
# DataParserClass.data[165]

# for _ in DataParserClass.data:
#     if len(_) == 8:
#         print(f" {_['URL']}    {_['category']} ")
#     else:
#         print(f"{DataParserClass.data.index(_)}  {_['URL']} Detected bug")

# cwd = os.getcwd()
# site_name = os.path.basename(__file__).split(".")[0]


# def save_image_to_file(self,images):
#     for image in images:
#         response = requests.get(image, stream=True)
#         dirname= os.path.join(cwd,'scraper',site_name)
#         if not os.path.exists(dirname):
#             os.makedirs(dirname)
#         dirFile = os.path.join(dirname,product_name)
#         with open(dirFile, 'wb') as out_file:
#             shutil.copyfileobj(response.raw, out_file)
#             img = Image.open(dirFile)    
#         del response

# def download_images(link, category,product_name):
#     print ("Downloading...")
#     response = requests.get(link, stream=True)
#     save_image_to_file(response,category,product_name)

# filename = os.path.join('test\testing1\img_1.jpg')


# for _ in DataParserClass.data:
#     print(f'({_["URL"]}    {_["management_number"]}')


test = set()
ctr = 0
for _ in DataParserClass.data:
    if _["URL"] == "https://www.furusato-tax.jp/product/detail/30366/4680040":
        print(_)
        test = _
