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


for _ in DataParserClass.data:
    if len(_) > 8:
        print("Detected bug")
    else:
        print(f"{_['URL']}    {_['category']}   {_['title']}  {_['local_name']} ")

# cwd = os.getcwd()
# site_name = os.path.basename(__file__).split(".")[0]


# def save_image_to_file(response,category,product_name):
#     dirname= os.path.join(cwd,site_name,product_name)
#     if not os.path.exists(dirname):
#         os.makedirs(dirname)
#     dirFile = os.path.join(dirname,product_name)
#     print (dirFile)
#     with open(dirFile, 'wb') as out_file:
#         shutil.copyfileobj(response.raw, out_file)
#         img = Image.open(dirFile)    
#         print (img.size)

# def download_images(link, category,product_name):
#     print ("Downloading...")
#     response = requests.get(link, stream=True)
#     save_image_to_file(response,category,product_name)
#     del response

# download_images("https://img.furusato-tax.jp/cdn-cgi/image/width=520,height=323/img/x/product/details/20200713/sd1_0e40bfca39974cbbf35002453f8d4e91e7ed22a0.jpg","fruits","img_1.jpg")
# print(site_name)

# site-name/category/item-data/imgaes_list


# filename = os.path.join('test\testing1\img_1.jpg')
