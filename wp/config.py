# SearchTagPerPage = 10
SearchTagPerPage = 100  # large enough to try response all for only sinlge call, max per_page is 100

MaxRetryNum = 10    # RequestsTimeout = 20 # max timeout for requests. Especially for /wp-json/wp/v2/media many time will stuck so add this.
log_filename = 'debug.log'

# def createPostMassFile(self):
#     pass
#     # if mediaFiles:
#     #     resp = self.postData(url=self.apiMedia, mediaFiles=mediaFiles)
#     # else:
#     #
#     # # self.reqSession.headers.update({'Authorization': self.authorization})
#     # self.reqSession.headers.update({'User-Agent': 'WordPress REST API manipulation library v0.1a powered by Python, written by iam9ripe 02/2023'})
#     # self.reqSession.headers.update({'Accept': 'application/json'})
#     # self.reqSession.headers.update({"cache-control": "no-cache"})
#     # self.reqSession.headers.update({'Content-Disposition': 'attachment; filename=%s' % mediaFilename})
#     # mediaFiles = {
#     #     'file': (mediaFilename, io.BytesIO(fdata.content), mediaContentType),
#     #     'caption': 'Первая попытка записи медиафалов в Библиотеку',
#     #     'description': 'Тестовая запись медиафала в Библиотеку',
#     # }
