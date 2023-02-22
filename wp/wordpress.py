import io
import random
import string
from datetime import datetime
import logging
import re
import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import base64
import wp.config as cfg


class WordPress(object):

    def __init__(self, host, login, password):
        # authentications settings
        self.host = host
        self.user = login
        self.password = password
        self.authorization = b'Basic ' + base64.b64encode(f'{self.user}:{self.password}'.encode('utf8'))

        # endpoints
        self.apiEndpoint = self.host + '/wp-json'
        self.apiMedia = self.host + "/wp-json/wp/v2/media"  # https://developer.wordpress.org/rest-api/reference/media/
        self.apiPosts = self.host + "/wp-json/wp/v2/posts"  # https://developer.wordpress.org/rest-api/reference/posts/
        self.apiCategories = self.host + "/wp-json/wp/v2/categories"  # https://developer.wordpress.org/rest-api/reference/categories/#create-a-category
        self.apiTags = self.host + "/wp-json/wp/v2/tags"  # https://developer.wordpress.org/rest-api/reference/tags/#create-a-tag

        # request library parameters set:
        # headers
        self.default_headers = dict()
        self.default_headers.update({'User-Agent': 'WordPress REST API manipulation library v0.1a powered by Python, written by iam9ripe 02/2023'})
        self.default_headers.update({'Accept': 'application/json'})
        self.default_headers.update({'Authorization': self.authorization})
        self.default_headers.update({"cache-control": "no-cache"})
        # session
        # requests.adapters.DEFAULT_RETRIES = 10
        self.reqSession = requests.Session()
        self.MaxRetryNum = cfg.MaxRetryNum
        self.reqAdapter = HTTPAdapter(max_retries=Retry(connect=self.MaxRetryNum, backoff_factor=0.5))
        self.reqSession.mount('http://', self.reqAdapter)
        self.reqSession.mount('https://', self.reqAdapter)
        self.reqSession.headers.update(self.default_headers)
        # proxy
        # self.requestsProxies = requestsProxies  # {'http': 'http://127.0.0.1:58591', 'https': 'http://127.0.0.1:58591'}

        self.Utils = Utils()

    #
    # create (post) - метод который создает сущность
    #

    def createPost(self, date=None, date_gmt=None, slug=None, status=None, password=None, title=None, content=None, author=None, excerpt=None, featured_media=None,
                   comment_status=None, ping_status=None, format=None, meta=None, sticky=False, template=None, categories=None, tags=None, plugin=None, pluginData=None,
                   completeFields=None):
        postsFields = {}
        if date is not None: postsFields.update({'date': str(date)})  # Дата публикации записи (по часовому поясу сайта).
        if date_gmt is not None: postsFields.update({'date_gmt': str(date_gmt)})  # Дата публикации записи, по GMT.
        if slug is not None: postsFields.update({'slug': str(slug)})  # Буквенно-цифровой идентификатор для записи, уникальный для ее типа.
        if status is not None and status in ['publish', 'future', 'draft', 'pending', 'private', 'acf-disabled']: postsFields.update(
            {'status': str(status)})  # Именованный статус записи.
        if password is not None: postsFields.update({'password': str(password)})  # Пароль для защиты содержания и отрывка.
        if title is not None: postsFields.update({'title': str(title)})  # Название записи.
        if content is not None: postsFields.update({'content': str(content)})  # Содержимое записи.
        if author is not None: postsFields.update({'author': int(author)})  # ID автора записи.
        if excerpt is not None: postsFields.update({'excerpt': excerpt})  # Отрывок записи.
        if featured_media is not None: postsFields.update({'featured_media': int(featured_media)})  # ID избранного изображения записи.
        if comment_status is not None and comment_status in ['open', 'closed']: postsFields.update({'comment_status': str(comment_status)})  # Открыты ли комментарии для записи.
        if ping_status is not None and ping_status in ['open', 'closed']: postsFields.update({'ping_status': str(ping_status)})  # Принимает ли запись уведомления.
        if format is not None and format in ['standard', 'aside', 'chat', 'gallery', 'link', 'image', 'quote', 'status', 'video', 'audio']: postsFields.update(
            {'format': str(format)})  # Формат записи.
        if meta is not None: postsFields.update({'meta': str(meta)})  # Мета поля.
        if sticky is not None: postsFields.update({'sticky': bool(sticky)})  # Считать ли запись прилепленной или нет.
        if template is not None: postsFields.update({'template': str(template)})  # Файл темы используемый для показа записи. (по сути тема)
        if categories is not None: postsFields.update({'categories': categories})  # Элементы назначенные объекту в таксономии category. (тип список из номеров категорий )
        if tags is not None: postsFields.update({'tags': tags})  # Элементы назначенные объекту в таксономии post_tag. (тип список из номеров категорий )
        if plugin is not None and plugin == 'acf':
            postsFields.update({'acf': {}})
            postsFields['acf'].update(pluginData)
        if completeFields is not None:
            postsFields.update(completeFields)

        return self.createEntities(endpoint='posts', postsFields=postsFields)

    def createMedia(self, url):
        if url is not None:
            if url.split('http'):
                fdata = self.Utils.getData(url=url)
                if fdata.status_code in range(200, 299):
                    mediaContentType = fdata.headers['Content-Type']
                    if len(mediaContentType.split('text/html')) > 1:
                        logging.debug(f'Тип загружаемого элемента не соответствует типу MediaFiles:{mediaContentType}')
                        return False
                    mediaContent = fdata.content
                    fileType = mediaContentType.split('/')[1]
                    if fileType.lower() == 'jpeg' and fileType not in url: fileType = 'jpg'
                    if fileType in url:
                        fileName = url.split(f'.{fileType}')[0].split("/")[-1]
                    else:
                        fileName = ''.join(random.choice(string.hexdigits.lower()) for x in range(32))
                    mediaFilename = f'{fileName}.{fileType}'
                else:
                    logging.debug(f'мы сделали 5 попыток но, не смогли загрузить медиафайл из следущего пути:{url}')
                    return False
            self.reqSession.headers.clear()
            self.reqSession.headers.update(self.default_headers)
            self.reqSession.headers.update({'Content-Type': mediaContentType})
            self.reqSession.headers.update({'Content-Disposition': 'attachment; filename=%s' % mediaFilename})
            return self.createEntities(url, endpoint='media')
        else:
            logging.debug(f'переменная url пуста, url - обязательный параметр.')

    def createCategories(self, name=None, slug=None, parent=0, meta=None, plugin=None, pluginData=None):
        if name is not None:
            catFields = {
                'name': str(name),
                'slug': str(slug) if meta else None,
                'parent': int(parent),
                'meta': str(meta) if meta else None,
            }
            if plugin is not None:
                if plugin == 'acf':
                    pluginFields = {'acf': {}}
                    pluginFields['acf'].update(pluginData)
                    catFields.update(pluginFields)
                else:
                    logging.debug(f'WordPress REST API manipulation library v0.1a не поддерживает плагины кроме ACF - Advance Custom Fields (PRO).')
            return self.createEntities(endpoint='categories', categoriesFields=catFields)
        else:
            logging.debug(f'переменная name пуста, name - имя категории, параметр обязательный.')

    def createTags(self):
        pass

    def createEntities(self, url=None, endpoint=None, postsFields=None, mediaContent=None, categoriesFields=None, tagsFields=None, customHeaders=None):
        if endpoint is not None:
            if endpoint.lower() == 'posts' or endpoint.lower() == 'post':
                if postsFields is not None:
                    if 'Content-Type' in self.reqSession.headers.keys(): del self.reqSession.headers['Content-Type']
                    if 'Content-Disposition' in self.reqSession.headers.keys(): del self.reqSession.headers['Content-Disposition']
                    self.reqSession.headers.update({'Accept': 'application/json'})
                    resp = self.postData(url=self.apiPosts, jsonFields=postsFields)
                    if resp.status_code not in range(200, 299): return False
                    return json.loads(resp.content)
                else:
                    logging.debug(f'переменная postFields пуста, postFields - обязательный параметр, и требуется для создания записи типа Post.')
            elif endpoint.lower() == 'media':
                if mediaContent is not None:
                    if customHeaders is None:
                        resp = self.postData(url=self.apiMedia, mediaContent=mediaContent)
                    else:
                        resp = self.postData(url=self.apiMedia, mediaContent=mediaContent, customHeaders=customHeaders)
                    if resp.status_code not in range(200, 299): return False
                    return json.loads(resp.content)
                else:
                    logging.debug(f'переменная mediaContent пуста, mediaContent - обязательный параметр, и требуется для создания записи типа Media.')
            elif endpoint.lower() == 'categories':
                if categoriesFields is not None:
                    if customHeaders is None:
                        self.reqSession.headers.clear()
                        self.reqSession.headers.update(self.default_headers)
                        resp = self.postData(url=self.apiCategories, jsonFields=categoriesFields)
                    else:
                        resp = self.postData(url=self.apiCategories, jsonFields=categoriesFields, customHeaders=customHeaders)
                    if resp.status_code not in range(200, 299): return False
                    return json.loads(resp.content)
                else:
                    logging.debug(f'переменная categoriesFields пуста, categoriesFields - обязательный параметр, и требуется для создания записи типа Categories.')
            elif endpoint.lower() == 'tags':
                if tagsFields is not None:
                    if customHeaders is None:
                        self.reqSession.headers.clear()
                        self.reqSession.headers.update(self.default_headers)
                        resp = self.postData(url=self.apiPosts, jsonFields=tagsFields)
                    else:
                        resp = self.postData(url=self.apiPosts, jsonFields=tagsFields, customHeaders=customHeaders)
                    if resp.status_code not in range(200, 299): return False
                    return json.loads(resp.content)
                else:
                    logging.debug(f'переменная tagsFields пуста, tagsFields - обязательный параметр, и требуется для создания записи типа Tags.')
            else:
                logging.debug(f'запрошено создание записи по неизвестной конечной точке:{endpoint}')

    def postData(self, url, mediaContent=None, customHeaders=None, jsonFields=None):
        if customHeaders is None:
            return self.reqSession.post(url=url, data=mediaContent, json=jsonFields)
        else:
            return self.reqSession.post(url=url, data=mediaContent, headers=customHeaders, json=jsonFields)

    #
    #  get - метод который  получает запрашивает данные по сущности, или сущностям
    #
    def getPosts(self, url=None, rid=None, plugin=None, page=None, perpage=None, offset=None, order=None, orderby=None):
        status, respText, links = self.getEntities(url=url, rid=rid, endpoint='post', page=page, perpage=perpage, offset=offset, order=order, orderby=orderby)
        return status, respText, links

    def getMedia(self, url=None, rid=None, plugin=None, page=None, perpage=None, offset=None, order=None, orderby=None):
        status, respText, links = self.getEntities(url=url, rid=rid, endpoint='media', page=page, perpage=perpage, offset=offset, order=order, orderby=orderby)
        return status, respText, links

    def getCategories(self, url=None, rid=None, plugin=None, page=None, perpage=None, offset=None, order=None, orderby=None):
        status, respText, links = self.getEntities(url=url, rid=rid, endpoint='categories', page=page, perpage=perpage, offset=offset, order=order, orderby=orderby)
        return status, respText, links

    def getTags(self, url=None, rid=None, plugin=None, page=None, perpage=None, offset=None, order=None, orderby=None):
        status, respText, links = self.getEntities(url=url, rid=rid, endpoint='tags', page=page, perpage=perpage, offset=offset, order=order, orderby=orderby)
        return status, respText, links

    def getEntities(self, url=None, rid=None, endpoint=None, plugin=None, page=None, perpage=None, offset=None, order=None, orderby=None, ):
        all_pages = False
        if url == None:
            if endpoint == None:
                url = self.apiPosts
            elif endpoint.lower() == 'posts' or endpoint.lower() == 'post':
                url = self.apiPosts
            elif endpoint.lower() == 'media':
                url = self.apiMedia
            elif endpoint.lower() == 'categories':
                url = self.apiCategories
            elif endpoint.lower() == 'tags':
                url = self.apiTags
            else:
                logging.debug(f'запрошено получение данных у неизвестной конечной точки:{endpoint}')

        if rid is not None:
            if str(rid).isnumeric():
                url += f'/{rid}'
            else:
                logging.debug(f'указан не верный формат ID записи, запись может быть только цифровым значением:{rid}')

        if page is not None:
            if page.lower() == 'all':
                all_pages = True
                if '?' in url:
                    url += f'&per_page={100}'
                else:
                    url += f'?per_page={100}'
            else:
                if str(page).isnumeric():
                    if '?' in url:
                        url += f'&page={page}'
                    else:
                        url += f'?page={page}'
                else:
                    logging.debug(f'указан неверный формат ID записи:{rid}, запись может быть только цифровым значением.')

            if perpage is not None:
                if str(perpage).isnumeric():
                    if '?' in url:
                        url += f'&per_page={perpage}'
                    else:
                        url += f'?per_page={perpage}'
                else:
                    logging.debug(f'указан не верный формат ID записи, запись может быть только цифровым значением:{rid}')

            if offset is not None:
                if str(perpage).isnumeric():
                    if '?' in url:
                        url += f'&offset={offset}'
                    else:
                        url += f'?offset={offset}'
                else:
                    logging.debug(f'указан не верный формат ID записи, запись может быть только цифровым значением:{rid}')

        if plugin is not None:
            if plugin.lower() == 'acf':
                if '?' in url:
                    url += '&_fields=acf'
                else:
                    url += f'?_fields=acf'
            else:
                logging.debug(f'запрошено получение данных у неизвестного плагина:{plugin}')

        if order is not None:
            if order in ['asc', 'desc']:
                if '?' in url:
                    url += f'&order={order}'
                else:
                    url += f'?order={order}'
            else:
                logging.debug(f'установлен неизвестнвй тип order в getEntities:{order}')

        if orderby is not None:
            if orderby in ['date', 'relevance', 'id', 'include', 'title', 'slug']:
                if '?' in url:
                    url += f'&orderby={orderby}'
                else:
                    url += f'?orderby={orderby}'
            else:
                logging.debug(f'установлен неизвестнвй тип orderby в getEntities:{orderby}')

        if all_pages == True:
            status, respText, links, resp = self.Utils.processResponce(self.getData(url=url))
            # total = (int(resp.headers['X-WP-Total']) // 100) + 1
            totalResult = ''
            while status or links['next']['url']:
                totalResult += f'{respText.strip("[]")},'
                if 'next' in links.keys():
                    status, respText, links = self.getEntities(url=links['next']['url'], page=page, perpage=perpage, offset=offset, order=order, orderby=orderby)
                else:
                    break
            return status, f'[{totalResult.rstrip(",")}]', links
        else:
            status, respText, links, resp = self.Utils.processResponce(self.getData(url=url))
            return status, respText, links

    def getData(self, url, headers=None):
        if headers == None:
            return self.reqSession.get(url=url)
        else:
            return self.reqSession.get(url=url, headers=headers)

    #
    #  update (PUT) - метод который обновляет целиком всю сущность, т.е. он его целиком перезавписывает. Все, что не будет указано, будет затерто
    #
    def updatePosts(self):
        pass

    def updateMedia(self):
        pass

    def updateCategories(self):
        pass

    def updateTags(self):
        pass

    def updateACF(self):
        pass

    #
    #  patch - метод который обновляет только те сущности которые указаны, не затрагивая все остальные
    #
    def patchPosts(self):
        pass

    def patchMedia(self):
        pass

    def patchCategories(self):
        pass

    def patchTags(self):
        pass

    def patchEntities(self, rid=None, endpoint=None, postsFields=None, mediaContent=None, categoriesFields=None, tagsFields=None, customHeaders=None):

        def req_data(url=None, jsonFields=None, customHeaders=None):
            if customHeaders is not None:
                return self.reqSession.post(url=url, json=jsonFields, headers=customHeaders)
            else:
                self.reqSession.headers.clear()
                self.reqSession.headers.update(self.default_headers)
                return self.reqSession.post(url=url, json=jsonFields)

        if rid == None:
            logging.debug(f'в параметрах процедуры patchEntities не указан номер записи который нужно изменить, id записи, это обязателный параметр.')
            return False
        if endpoint is not None:
            if endpoint.lower() == 'posts' or endpoint.lower() == 'post':
                if postsFields is not None:
                    resp = req_data(self.apiPosts, jsonFields=postsFields, customHeaders=customHeaders)
                    if resp.status_code not in range(200, 299): return False
                    return json.loads(resp.content)
                else:
                    logging.debug(f'переменная postFields пуста, postFields - обязательный параметр, и требуется для создания записи типа Post.')
            elif endpoint.lower() == 'media':
                if mediaContent is not None:
                    if customHeaders is None:
                        resp = self.postData(url=self.apiMedia, mediaContent=mediaContent)
                    else:
                        resp = self.postData(url=self.apiMedia, mediaContent=mediaContent, customHeaders=customHeaders)

                    if resp.status_code not in range(200, 299): return False
                    return json.loads(resp.content)
                else:
                    logging.debug(f'переменная mediaContent пуста, mediaContent - обязательный параметр, и требуется для создания записи типа Media.')
            elif endpoint.lower() == 'categories':
                if categoriesFields is not None:
                    resp = req_data(url=self.apiCategories, jsonFields=categoriesFields, customHeaders=customHeaders)
                    if resp.status_code not in range(200, 299): return False
                    return json.loads(resp.content)
                else:
                    logging.debug(f'переменная categoriesFields пуста, categoriesFields - обязательный параметр, и требуется для создания записи типа Categories.')
            elif endpoint.lower() == 'tags':
                if tagsFields is not None:
                    resp = req_data(url=self.apiTags, jsonFields=tagsFields, customHeaders=customHeaders)
                    if resp.status_code not in range(200, 299): return False
                    return json.loads(resp.content)
                else:
                    logging.debug(f'переменная tagsFields пуста, tagsFields - обязательный параметр, и требуется для создания записи типа Tags.')
            else:
                logging.debug(f'запрошено создание записи по неизвестной конечной точке:{endpoint}')

    def patchData(self, url, mediaContent=None, customHeaders=None, jsonFields=None):
        if customHeaders == None:
            return self.reqSession.post(url=url, data=mediaContent, json=jsonFields)
        else:
            return self.reqSession.post(url=url, data=mediaContent, headers=customHeaders, json=jsonFields)


class Utils(object):
    def __init__(self):
        self.logfile = cfg.log_filename
        logging.basicConfig(filename=self.logfile, encoding='utf-8', level=logging.DEBUG)

    def processResponce(self, responce):
        if responce.status_code in range(200, 299):
            logging.debug(f'Получен ответ:[ Код:{responce.status_code}; Ответ:{responce.text.encode("utf8")}\n')
            return True, responce.text, responce.links, responce
        else:
            logging.debug(f'Получен ответ:[ Код:{responce.status_code}; Ответ:{responce.text.encode("utf8")}\n')
            return False, responce.text, responce.links, responce

    def getData(self, url, headers=None):
        # requests.adapters.DEFAULT_RETRIES = 5
        session = requests.session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[x for x in range(500, 599)],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))
        if headers == None:
            session.headers.update({'User-Agent': 'WordPress REST API manipulation library v0.1a powered by Python, written by iam9ripe 02/2023'})
            session.headers.update({'Accept': '*/*'})
            resp = session.get(url=url)
            session.close()
            return resp
        else:
            resp = session.get(url=url, headers=headers)
            session.close()
            return resp
