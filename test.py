import requests
import shutil
import os 
from PIL import Image


cwd = os.getcwd()
site_name = os.path.basename(__file__).split(".")[0]


def save_image_to_file(response,category,product_name):
    dirname= os.path.join(cwd,site_name,category,product_name)
    print(dirname)
    print(not os.path.isfile(os.path.join(dirname,product_name)))
    # if not os.path.isfile(os.path.join(dirname,product_name)):
    #     os.mkdir(dirname)
    with open(os.path.join(dirname,product_name), 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)


def download_images(link, category,product_name):
    print ("Downloading...")
    response = requests.get(link, stream=True)
    save_image_to_file(response,category,product_name)
    del response

download_images("https://furu-po.com/img/brank.gif","fruits","img_1.jpg")
# print(site_name)

# site-name/category/item-data/imgaes_list


# filename = os.path.join('test\testing1\img_1.jpg')
img = Image.open("test\\testing1\\img_1.jpg")
print (img.size)