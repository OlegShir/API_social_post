import requests, json
from io import BytesIO


class VK:

    def __init__(self, API_TOKEN: str):
        self.access_token = API_TOKEN
        self.groud_id = '205154596'
        self.version = '5.81'
        
    def photos_get_wall_upload_server(self):
        '''Возвращает адрес сервера для загрузки фотографии на стену'''
        
        url = 'https://api.vk.com/method/photos.getWallUploadServer'

        request = requests.post(url, data={
                                            'group_id': self.groud_id,
                                            'access_token': self.access_token,
                                            'v': self.version
                                     }
        )
        upload_url = json.loads(request.text)['response']['upload_url']

        return upload_url

    def photos_post_server(self, photo_url: str):
        '''Возвращает параметры сервера для загрузки фотографий'''

        upload_url = self.photos_get_wall_upload_server()
        request_photo = requests.post(upload_url, files={
                                                        'photo': ('photo.jpg',\
                                                         BytesIO(requests.get(photo_url).content), 'image/png')
                                                  }
        )
        server = json.loads(request_photo.text)

        return server

    def photos_save_wall_photo(self, server: str):
        '''Сохраняет фотографии после успешной загрузки на URI, полученный методом photos.getWallUploadServer'''

        url = 'https://api.vk.com/method/photos.saveWallPhoto?'

        request_id = requests.post(url, data = {
                                                'group_id': self.groud_id,
                                                'access_token': self.access_token,
                                                'photo': server['photo'],
                                                'hash': server['hash'],
                                                'server': server['server'],
                                                'v': self.version
                                        }
        )
        id_photo = json.loads(request_id.text)['response'][0]['id']
        owner_id =  json.loads(request_id.text)['response'][0]['owner_id']
        
        return id_photo, owner_id

    def wall_post(self, photo: str, caption: str):
        '''Позволяет создать запись на стене, предложить запись на стене публичной страницы, опубликовать существующую отложенную запись'''

        try:
            id_photo, owner_id = self.photos_save_wall_photo(self.photos_post_server(photo))

            url = 'https://api.vk.com/method/wall.post' 

            requests.post(url, data={
                                'owner_id': f'-{self.groud_id}',
                                'from_group': 1,
                                'message': caption,
                                'attachments': f'photo{owner_id}_{id_photo}',
                                'access_token': self.access_token,
                                'signed': 0,
                                'v': self.version
                                    }
            )
        except Exception as error: 
            print(f'При публикации события на стене ВКонтакте возникла ошибка:\n{error.__class__.__name__}')

    def utils_get_short_link(self, long_url:str):
        '''Позволяет получить URL, сокращенный с помощью vk.cc'''

        url ='https://api.vk.com/method/utils.getShortLink'

        respone_url = requests.post(url, data={
                                                'url': long_url,
                                                'access_token': self.access_token,
                                                'v': self.version
                                            }
        ) 

        short_url = json.loads(respone_url.text)['response']['short_url']

        return short_url
    
    def groups_get_by_id(self, fields='members_count'):
        '''Возвращает информацию о заданном сообществе или о нескольких сообществах.'''

        url ='https://api.vk.com/method/groups.getById'

        request_to_server = requests.post(url, data={
                                                'group_id': self.groud_id,
                                                'fields': fields,
                                                'access_token': self.access_token,
                                                'v': self.version,
                                                
                                            }
        ) 

        respone_server = json.loads(request_to_server.text)

        return respone_server['response'][0]['members_count']

if __name__ == '__main__':
    pass