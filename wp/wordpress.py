import base64
import json
import logging
import random
import string
from datetime import datetime

from requests import Session, exceptions as REX
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
        self.reqSession = Session()
        self.MaxRetryNum = 100
        self.reqAdapter = HTTPAdapter(
            max_retries=Retry(connect=self.MaxRetryNum, backoff_factor=0.5, status_forcelist=[x for x in range(500, 599)], method_whitelist=["GET", "POST", "PUT", "PATCH"], ))
        self.reqSession.mount('http://', self.reqAdapter)
        self.reqSession.mount('https://', self.reqAdapter)
        self.reqSession.headers.update(self.default_headers)
        # proxy
        # self.requestsProxies = requestsProxies  # {'http': 'http://127.0.0.1:58591', 'https': 'http://127.0.0.1:58591'}

        self.Utils = Utils()

    ################################################################################################################################################
    # create (post) - метод который создает сущность                                                                                               #
    ################################################################################################################################################

    def createPost(self, date=None, date_gmt=None, slug=None, status=None, password=None, title=None, content=None, author=None, excerpt=None, featured_media=None, comment_status=None,
                   ping_status=None, format=None, meta=None, sticky=False, template=None, categories=None, tags=None, plugin=None, pluginData=None, completeFields=None):

        postsFields = {}
        if completeFields is not None:
            postsFields.update(completeFields)
        else:
            if date is not None: postsFields.update({'date': str(date)})  # Дата публикации записи (по часовому поясу сайта).
            if date_gmt is not None: postsFields.update({'date_gmt': str(date_gmt)})  # Дата публикации записи, по GMT.
            if slug is not None: postsFields.update({'slug': str(slug)})  # Буквенно-цифровой идентификатор для записи, уникальный для ее типа.
            if status is not None and status in ['publish', 'future', 'draft', 'pending', 'private', 'acf-disabled']: postsFields.update({'status': str(status)})  # Именованный статус записи.
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
        return self.createEntities(endpoint='posts', postsFields=postsFields)

    def createMedia(self, url):
        if url is not None:
            if url.split('http'):
                fdata = self.proccessData(url=url, method='get')
                if fdata:
                    mediaContentType = fdata.headers['Content-Type']
                    if len(mediaContentType.split('text/html')) > 1:
                        logging.debug(f'{datetime.utcnow()}: Тип загружаемого элемента не соответствует типу MediaFiles:{mediaContentType}')
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
                    logging.debug(f'{datetime.utcnow()}: мы сделали 5 попыток но, не смогли загрузить медиафайл из следущего пути:{url}')
                    return False
            else:
                # тут нужно написать функцию сичтывания фалас диска
                pass
            self.reqSession.headers.clear()
            self.reqSession.headers.update(self.default_headers)
            self.reqSession.headers.update({'Content-Type': mediaContentType})
            self.reqSession.headers.update({'Content-Disposition': 'attachment; filename=%s' % mediaFilename})
            return self.createEntities(url, endpoint='media', mediaContent=mediaContent)
        else:
            logging.debug(f'{datetime.utcnow()}: переменная url пуста, url - обязательный параметр.')

    def createCategories(self, name=None, description=None, slug=None, parent=0, meta=None, plugin=None, pluginData=None):
        if name is not None:
            catFields = {
                'name': str(name),
                'description': str(description),
                'slug': str(slug) if meta else None,
                'parent': int(parent),
                'meta': str(meta) if meta else None,
            }
            if plugin and plugin == 'acf':
                pluginFields = {'acf': {}}
                pluginFields['acf'].update(pluginData)
                catFields.update(pluginFields)
            else:
                logging.debug(f'{datetime.utcnow()}: WordPress REST API manipulation library v0.1a пока не поддерживает плагины кроме ACF - Advance Custom Fields (PRO).')
            return self.createEntities(endpoint='categories', categoriesFields=catFields)
        else:
            logging.debug(f'{datetime.utcnow()}: переменная name пуста, name - имя категории, параметр обязательный.')

    def createTags(self):
        pass

    def createEntities(self, url=None, endpoint=None, postsFields=None, mediaContent=None, categoriesFields=None, tagsFields=None, customHeaders=None):
        def make_headers():
            self.reqSession.headers.clear()
            self.reqSession.headers.update(self.default_headers)

        resp = False
        match endpoint.lower():
            case 'post' | 'posts':
                if postsFields is not None:
                    make_headers()
                    resp = self.proccessData(url=self.apiPosts, jsonFields=postsFields, method='post')
                else:
                    logging.debug(f'{datetime.utcnow()}: переменная postFields пуста, postFields - обязательный параметр, и требуется для создания записи типа Post.')
            case 'media':
                if mediaContent is not None:
                    resp = self.proccessData(url=self.apiMedia, mediaContent=mediaContent, method='post')
                else:
                    logging.debug(f'{datetime.utcnow()}: переменная mediaContent пуста, mediaContent - обязательный параметр, и требуется для создания записи типа Media.')
            case 'categories':
                if categoriesFields is not None:
                    make_headers()
                    resp = self.proccessData(url=self.apiCategories, jsonFields=categoriesFields, customHeaders=customHeaders, method='post')
                else:
                    logging.debug(f'переменная categoriesFields пуста, categoriesFields - обязательный параметр, и требуется для создания записи типа Categories.')
            case 'tags':
                if tagsFields is not None:
                    make_headers()
                    resp = self.proccessData(url=self.apiPosts, jsonFields=tagsFields, customHeaders=customHeaders, method='post')
                else:
                    logging.debug(f'{datetime.utcnow()}: переменная tagsFields пуста, tagsFields - обязательный параметр, и требуется для создания записи типа Tags.')
            case _:
                logging.debug(f'{datetime.utcnow()}: запрошено создание записи по неизвестной конечной точке:{endpoint}')

        if not resp: return False
        return json.loads(resp.content)

    ################################################################################################################################################
    #  get - метод который  получает запрашивает данные по сущности, или сущностям                                                                 #
    ################################################################################################################################################
    def getPosts(self, url=None, rid=None, plugin=None, page=None, perpage=None, offset=None, order=None, orderby=None):
        return self.getEntities(url=url, rid=rid, endpoint='post', page=page, perpage=perpage, offset=offset, order=order, orderby=orderby)

    def getMedia(self, url=None, rid=None, plugin=None, page=None, perpage=None, offset=None, order=None, orderby=None):
        return self.getEntities(url=url, rid=rid, endpoint='media', page=page, perpage=perpage, offset=offset, order=order, orderby=orderby)

    def getCategories(self, url=None, rid=None, plugin=None, page=None, perpage=None, offset=None, order=None, orderby=None):
        return self.getEntities(url=url, rid=rid, endpoint='categories', page=page, perpage=perpage, offset=offset, order=order, orderby=orderby)

    def getTags(self, url=None, rid=None, plugin=None, page=None, perpage=None, offset=None, order=None, orderby=None):
        return self.getEntities(url=url, rid=rid, endpoint='tags', page=page, perpage=perpage, offset=offset, order=order, orderby=orderby)

    def getEntities(self, url=None, rid=None, endpoint=None, plugin=None, page=None, perpage=None, offset=None, order=None, orderby=None, ):
        def make_url(url=None, rid=None, endpoint=None, plugin=None, page=None, perpage=None, offset=None, order=None, orderby=None):
            all_pages = False
            if url == None:
                match endpoint.lower():
                    case 'posts' | 'post':
                        url = self.apiPosts
                    case 'media':
                        url = self.apiMedia
                    case 'categories':
                        url = self.apiCategories
                    case 'tags':
                        url = self.apiTags
                    case None:
                        url = self.apiPosts
                    case _:
                        logging.debug(f'{datetime.utcnow()}: запрошено получение данных у неизвестной конечной точки:{endpoint}')
            if rid is not None:
                if str(rid).isnumeric():
                    url += f'/{rid}'
                else:
                    logging.debug(f'{datetime.utcnow()}: указан не верный формат ID записи, запись может быть только цифровым значением:{rid}')
            if page is not None:
                if page.lower() == 'all':
                    all_pages = True
                    url += f'&per_page={100}' if '?' in url else f'?per_page={100}'
                else:
                    if str(page).isnumeric():
                        url += f'&page={page}' if '?' in url else f'?page={page}'
                    else:
                        logging.debug(f'{datetime.utcnow()}: указан неверный формат ID записи:{rid}, запись может быть только цифровым значением.')
                if perpage is not None:
                    if str(perpage).isnumeric():
                        url += f'&per_page={perpage}' if '?' in url else f'?per_page={perpage}'
                    else:
                        logging.debug(f'{datetime.utcnow()}: указан не верный формат perpage записи, запись может быть только цифровым значением:{perpage}')
                if offset is not None:
                    if str(perpage).isnumeric():
                        url += f'&offset={offset}' if '?' in url else f'?offset={offset}'
                    else:
                        logging.debug(f'{datetime.utcnow()}: указан не верный формат offset записи, запись может быть только цифровым значением:{offset}')
            if plugin is not None:
                if plugin.lower() == 'acf':
                    url += '&_fields=acf' if '?' in url else f'?_fields=acf'
                else:
                    logging.debug(f'{datetime.utcnow()}: запрошено получение данных у неизвестного плагина:{plugin}')
            if order is not None:
                if order in ['asc', 'desc']:
                    url += f'&order={order}' if '?' in url else f'?order={order}'
                else:
                    logging.debug(f'{datetime.utcnow()}: установлен неизвестнвй тип order в getEntities:{order}')
            if orderby is not None:
                if orderby in ['date', 'relevance', 'id', 'include', 'title', 'slug']:
                    url += f'&orderby={orderby}' if '?' in url else f'?orderby={orderby}'
                else:
                    logging.debug(f'{datetime.utcnow()}: установлен неизвестнвй тип orderby в getEntities:{orderby}')
            return url, all_pages

        url, all_pages = make_url(url=url, rid=rid, endpoint=endpoint, plugin=plugin, page=page, perpage=perpage, offset=offset, order=order, orderby=orderby)
        if all_pages == True:
            resp = self.proccessData(url=url, method='get')
            totalResult = []
            while resp.status_code or resp.links['next']['url']:
                totalResult.extend(json.loads(resp.text))
                if 'next' in resp.links.keys():
                    url, all_pages = make_url(url=resp.links['next']['url'], page=page, perpage=perpage, offset=offset, order=order, orderby=orderby)
                    resp = self.proccessData(url=url, method='get')
                else:
                    break
            return json.loads(json.dumps(totalResult))
        else:
            return json.loads(self.proccessData(url=url, method='get').text)

    ################################################################################################################################################
    #  update (PUT) - метод который обновляет целиком всю сущность, т.е. он его целиком перезавписывает. Все, что не будет указано, будет затерто  #
    ################################################################################################################################################
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

    ################################################################################################################################################
    #  patch - метод который обновляет только те сущности которые указаны, не затрагивая все остальные                                             #
    ################################################################################################################################################
    def patchPosts(self):
        pass

    def patchMedia(self):
        pass

    def patchCategories(self, cid=None, name=None, description=None, slug=None, parent=0, meta=None, plugin=None, pluginData=None):

        pass

    def patchTags(self):
        pass

    def patchEntities(self, rid=None, endpoint=None, postsFields=None, mediaContent=None, categoriesFields=None, tagsFields=None, customHeaders=None):
        def make_headers():
            self.reqSession.headers.clear()
            self.reqSession.headers.update(self.default_headers)

        resp = False
        if rid == None:
            logging.debug(f'{datetime.utcnow()}: в параметрах процедуры Wordpress::patchEntities не указан номер записи который нужно изменить, id записи, это обязателный параметр.')
            return False
        match endpoint.lower():
            case 'post' | 'posts':
                if endpoint.lower() == 'posts' or endpoint.lower() == 'post':
                    if postsFields is not None:
                        make_headers()
                        resp = self.proccessData(url=self.apiPosts, jsonFields=postsFields, customHeaders=customHeaders, method='patch')
                    else:
                        logging.debug(f'{datetime.utcnow()}: переменная postFields пуста, postFields - обязательный параметр, и требуется для создания записи типа Post.')
            case 'media':
                if mediaContent is not None:
                    if customHeaders is None:
                        resp = self.proccessData(url=self.apiMedia, mediaContent=mediaContent, method='patch')
                    else:
                        resp = self.proccessData(url=self.apiMedia, mediaContent=mediaContent, customHeaders=customHeaders, method='patch')
                else:
                    logging.debug(f'{datetime.utcnow()}: переменная mediaContent пуста, mediaContent - обязательный параметр, и требуется для создания записи типа Media.')
            case 'categories':
                if categoriesFields is not None:
                    make_headers()
                    resp = self.proccessData(url=self.apiCategories, jsonFields=categoriesFields, customHeaders=customHeaders, method='patch')
                else:
                    logging.debug(f'{datetime.utcnow()}: переменная categoriesFields пуста, categoriesFields - обязательный параметр, и требуется для создания записи типа Categories.')
            case 'tags':
                if tagsFields is not None:
                    make_headers()
                    resp = self.proccessData(url=self.apiTags, jsonFields=tagsFields, customHeaders=customHeaders, method='patch')
                else:
                    logging.debug(f'{datetime.utcnow()}: переменная tagsFields пуста, tagsFields - обязательный параметр, и требуется для создания записи типа Tags.')
            case _:
                logging.debug(f'{datetime.utcnow()}: запрошено создание записи по неизвестной конечной точке:{endpoint}')

        if not resp: return False
        return json.loads(resp.content)

    def proccessData(self, url, mediaContent=None, customHeaders=None, jsonFields=None, method=None):
        try:
            match method:
                case 'get' | None:
                    if customHeaders is None:
                        self.reqSession.headers.clear()
                        self.reqSession.headers.update(self.default_headers)
                        resp = self.reqSession.get(url=url)
                    else:
                        resp = self.reqSession.get(url=url, headers=customHeaders)
                case 'post':
                    if customHeaders is None:
                        resp = self.reqSession.post(url=url, data=mediaContent, json=jsonFields)
                    else:
                        resp = self.reqSession.post(url=url, data=mediaContent, headers=customHeaders, json=jsonFields)
                case 'put':
                    if customHeaders is None:
                        resp = self.reqSession.put(url=url, data=mediaContent, json=jsonFields)
                    else:
                        resp = self.reqSession.put(url=url, data=mediaContent, headers=customHeaders, json=jsonFields)
                case 'patch':
                    if customHeaders is None:
                        resp = self.reqSession.patch(url=url, data=mediaContent, json=jsonFields)
                    else:
                        resp = self.reqSession.patch(url=url, data=mediaContent, headers=customHeaders, json=jsonFields)
                case _:
                    logging.debug(f'{datetime.utcnow()}: неизвестный метов в Wordpress::processData:{str(method)}')
                    resp = False
            if resp and resp.status_code not in range(200, 299):
                logging.debug(f'{datetime.utcnow()}: неожиданный ответ сервера код:{resp.status_code}; сообщение:{json.loads(resp.text)}')
                return False
            return resp
        except (REX.Timeout, REX.ConnectionError, REX.ConnectTimeout, REX.RetryError) as e:
            logging.debug(f'{datetime.utcnow()}: произошел сбой (Exception):{e}')
            self.proccessData(url=url, mediaContent=mediaContent, customHeaders=customHeaders, jsonFields=jsonFields)


class Utils(object):
    def __init__(self):
        self.logfile = cfg.log_filename
        logging.basicConfig(filename=self.logfile, encoding='utf-8', level=logging.DEBUG)

    def processResponce(self, responce):
        if responce.status_code in range(200, 299):
            logging.debug(f'{datetime.utcnow()}: Получен ответ:[ Код:{responce.status_code}; Ответ:{str(responce.text)}]\n')
            return True, responce.text, responce.links, responce
        else:
            logging.debug(f'{datetime.utcnow()}: Получен ответ:[ Код:{responce.status_code}; Ответ:{str(responce.text)}]\n')
            return False, responce.text, responce.links, responce
