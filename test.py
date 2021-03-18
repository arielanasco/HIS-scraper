import requests
from bs4 import BeautifulSoup as bs
import shutil
import os 
from PIL import Image


# res = requests.get("https://furu-po.com/goods_detail.php?id=664459")
# html = bs(res.text, 'html.parser')
# img = html.find(class_="item_info_slider").find_all(class_="slide-item")
# # img = html.find(class_="slick-track")
# print(img)
# for _ in img:
#     print(_)

import logging
logging.basicConfig(format='[%(asctime)s](%(levelname)s@%(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logging.debug("This will get logged")
DataParserClass.data[165]

for _ in DataParserClass.data:
    if len(_) == 8:
        print(f" {_['URL']}    {_['category']} ")
    else:
        print(f"{DataParserClass.data.index(_)}  {_['URL']} Detected bug")

cwd = os.getcwd()
site_name = os.path.basename(__file__).split(".")[0]


def save_image_to_file(self,images):
    for image in images:
        response = requests.get(image, stream=True)
        dirname= os.path.join(cwd,'scraper',site_name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        dirFile = os.path.join(dirname,product_name)
        with open(dirFile, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
            img = Image.open(dirFile)    
        del response

def download_images(link, category,product_name):
    print ("Downloading...")
    response = requests.get(link, stream=True)
    save_image_to_file(response,category,product_name)

filename = os.path.join('test\testing1\img_1.jpg')


for _ in DataParserClass.data:
    print(f"({_["URL"]}    {_["management_number"]})
