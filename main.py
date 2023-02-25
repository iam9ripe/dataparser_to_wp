import io

from wp.schemas import Post
from wp.wordpress import WordPress
from wp.config import *
import requests
import json
import base64
import pprint

wpc = WordPress('https://satellit-spb.ru', 'python', 'zj0s EUAv 2RPB oQFz enqX B8xk')


# resp = wpc.getCategories(page='all', orderby='id', order='asc')
resp = wpc.getMedia(rid=9449)
resp = wpc.getPosts(page='all', orderby='id', order='asc')

with open('./parsing/catalog_new.json','r', encoding='utf8') as file:
    catalog = json.load(file)
host = 'https://plastcase.ru'
for cat in catalog['categories']:
    sm = wpc.createMedia(f'{host}{catalog["categories"][cat]["image"]}')
    scat = wpc.createCategories(name=catalog['categories'][cat]['name'], plugin='acf', pluginData={'foto_categ': sm['id']})
    for itd in catalog['categories'][cat]['items']:
        idata = {
            'categories': [],
            'acf': {'gallery_img': [], 'product_options': [], 'chose_color': []}
        }
        item = catalog['categories'][cat]['items'][itd]
        idata.update({'title': item['model']})
        idata['categories'].append(scat['id'])
        idata.update({'status': 'publish'})
        for image in item['images']:
            md = wpc.createMedia(f'{host}{image}')
            if md and md['id']:
                idata['acf']['gallery_img'].append({'img_gallery_value': md['id']})
            else:
                pass
        if idata['acf']['gallery_img'][0]['img_gallery_value']:
            idata['acf'].update({'main_img': idata['acf']['gallery_img'][0]['img_gallery_value']})
        else:
            pass
        idata['acf'].update({'price_main': item['price']})
        idata['acf'].update({'main_description_block_product': item['description']})
        for key, val in item['acf']['dimensions'].items():
            idata['acf']['product_options'].append({'name_option': key, 'value_option': "".join(str(x)+' x ' for x in val).strip(' x')})
        for key, val in item['acf']['params'].items():
            idata['acf']['product_options'].append({'name_option': key, 'value_option': val})
        for el in item['colors']:
            color = el['color']
            image = el['image']
            if image:
                md = wpc.createMedia(f'{host}{image}')
                match color:
                    case 'Черный': val = '#000000'
                    case 'Красный': val = '#dd3333'
                    case 'Оранжевый': val = '#dd9933'
                    case 'Желтый': val = '#f6ff00'
                    case 'Фиолетовый': val = '#8224e3'
                    case 'Зеленый': val = '#1ba808'
                    case _: val = '#ffffff'
                idata['acf']['chose_color'].append({'name_color': color, 'chose_color_insert': val, 'color_gallery_img': md['id']})

            else:
                pass
        cdp = wpc.createPost(completeFields=idata)

# url = "https://satellit-spb.ru/wp-json/wp/v2/posts/?_fields=acf&acf_format=light"
# url = "https://satellit-spb.ru/wp-json/wp/v2/posts/68"
url = "https://satellit-spb.ru/wp-json/wp/v2/media"

# resp = json.loads(wpc.getPosts(rid=68)[1])
# resp = json.loads(wpc.getPosts(rid=68, page='all', orderby='id', order='asc')[1])
# resp = json.loads(wpc.getCategories(page='all',orderby='id', order='asc')[1])
# url = f"https://satellit-spb.ru/wp-json"
# url = f"https://satellit-spb.ru/wp-json/wp/v2/users/me"
# routes = json.loads(wpc.getData(url=url).text)

# res = requests.get(url)
# url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTYOa3EkC-tEeyFmXVGDO_QoqVd4HXffGehRQ&usqp=CAU'
# url = 'https://klike.net/uploads/posts/2022-12/1670038877_7-2.jpg'
# url = 'https://bit.ly/3R5WQdd'
# res = wpc.createMedia(url=url)
# res = wpc.createEntities(endpoint='categories', name='REST API Новая Категория', slug='rest-api-category', plugin='acf', pluginData={'foto_categ': 144})

# p = {
#     'title': 'Это заголовок тестовой записи',
#     'content': 'Контентент новой запис созданной по апи',
#     'status': 'publish',
#     # 'featured_media': createMedia($imageSrc),
#     'categories':  [3],
#     'meta': {'content_source': 'WordPress REST API tutorial'},
#     'acf':{
#         'price_main': '200',
#         'product_options':[
#             {'name_option': 'Внешние размеры, мм:', 'value_option': '10.1 x 10.2 x 10.15','main_img': 144}
#         ],
#         'gallery_img': [
#             {'img_gallery_value': 70},{'img_gallery_value': 69},{'img_gallery_value': 144},
#         ]
#     }
# }
#
# res = wpc.createPost(completeFields=p)
#
#
# print(post.json())
# DATA = {'acf': {'chose_color': []}}
# # opts = json.loads(requests.options(url, headers=header).text)
# # post = json.loads(requests.post(url, headers=header, json=DATA).text)
#
# # delete = requests.delete(url, headers=header)
# p = {
#     'title': 'Это заголовок тестовой записи',
#     'content': 'Контентент новой запис созданной по апи',
#     'status': 'publish',
#     # 'featured_media': createMedia($imageSrc),
#     'categories':  [3, 6, 14],
#     'meta': {'content_source': 'WordPress REST API tutorial'}
# }
# acf ={
#     'acf': {
#             # {'price_main': '', 'product_options': None, 'chose_color': None, 'main_img': None, 'gallery_img': None, 'main_description_block_product': '', 'main_list_hara': None, 'list_acc': None, 'main_block_cherte': '', 'list_sert': None}
#             'price_main': '1234',
#     }
#
# }
#
#
# url = f"https://satellit-spb.ru/wp-json/wp/v2/posts"
# new_rec = requests.post(url, headers=header, json=p)
# url = f"https://satellit-spb.ru/wp-json/wp/v2/posts/{json.loads(new_rec.text)['id']}"
# # url = f"https://satellit-spb.ru/wp-json/wp/v2/posts/{json.loads(new_rec.text)['id']}?_fields=acf"
# new_patch = requests.post(url, headers=header, json={'acf': post.acf})
# pprint.pprint(json.loads(new_rec.text))
