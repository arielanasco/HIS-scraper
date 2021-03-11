import requests
from bs4 import BeautifulSoup as bs


res = requests.get("https://www.furusato-tax.jp/product/detail/01607/5049841")
html = bs(res.text, 'html.parser')
img = html.find(class_="city-title").get_text()
print(img)
# for _ in img:
#     print(_)

# import shutil
# import os 
# from PIL import Image


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
# # print(site_name)

# # site-name/category/item-data/imgaes_list


# # filename = os.path.join('test\testing1\img_1.jpg')
