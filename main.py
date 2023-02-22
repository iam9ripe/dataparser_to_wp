import io

from wp.schemas import Post
from wp.wordpress import WordPress
from wp.config import *
import requests
import json
import base64
import pprint

# url = "https://satellit-spb.ru/wp-json/wp/v2/posts/?_fields=acf&acf_format=light"
# url = "https://satellit-spb.ru/wp-json/wp/v2/posts/68"
url = "https://satellit-spb.ru/wp-json/wp/v2/media"

wpc = WordPress('https://satellit-spb.ru', 'python', 'zj0s EUAv 2RPB oQFz enqX B8xk')
resp = json.loads(wpc.getPosts(page='all', orderby='id', order='asc')[1])
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

p = {
    'title': 'Это заголовок тестовой записи',
    'content': 'Контентент новой запис созданной по апи',
    'status': 'publish',
    # 'featured_media': createMedia($imageSrc),
    'categories':  [3],
    'meta': {'content_source': 'WordPress REST API tutorial'},
    'acf':{
        'price_main': '200',
        'product_options':[
            {'name_option': 'Внешние размеры, мм:', 'value_option': '10.1 x 10.2 x 10.15','main_img': 144}
        ],
        'gallery_img': [
            {'img_gallery_value': 70},{'img_gallery_value': 69},{'img_gallery_value': 144},
        ]
    }
}

res = wpc.createPost(completeFields=p)

try:
    post = Post(**rec)
except Exception as e:
    print(e)
post.id = 999
post.slug = 'jhki'
del post.id
del post.guid
del post.modified
del post.modified_gmt
del post.type
del post.link

post.title.rendered = 'Кейс 999_999'
post.content.rendered = 'Это Кейс под номером 999'

print(post.json())
DATA = {'acf': {'chose_color': []}}
# opts = json.loads(requests.options(url, headers=header).text)
# post = json.loads(requests.post(url, headers=header, json=DATA).text)

# delete = requests.delete(url, headers=header)
p = {
    'title': 'Это заголовок тестовой записи',
    'content': 'Контентент новой запис созданной по апи',
    'status': 'publish',
    # 'featured_media': createMedia($imageSrc),
    'categories':  [3, 6, 14],
    'meta': {'content_source': 'WordPress REST API tutorial'}
}
acf ={
    'acf': {
            # {'price_main': '', 'product_options': None, 'chose_color': None, 'main_img': None, 'gallery_img': None, 'main_description_block_product': '', 'main_list_hara': None, 'list_acc': None, 'main_block_cherte': '', 'list_sert': None}
            'price_main': '1234',
    }

}


url = f"https://satellit-spb.ru/wp-json/wp/v2/posts"
new_rec = requests.post(url, headers=header, json=p)
url = f"https://satellit-spb.ru/wp-json/wp/v2/posts/{json.loads(new_rec.text)['id']}"
# url = f"https://satellit-spb.ru/wp-json/wp/v2/posts/{json.loads(new_rec.text)['id']}?_fields=acf"
new_patch = requests.post(url, headers=header, json={'acf': post.acf})
pprint.pprint(json.loads(new_rec.text))
