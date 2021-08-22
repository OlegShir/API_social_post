import json, requests, hashlib
from io import BytesIO


class OK_api:

    def __init__(self, access_token: str, session_secret_key: str, public_key_app: str, id_group: str) -> None:
        self.gid = id_group
        self.api_server = 'https://api.ok.ru/fb.do'
        self.SSK = session_secret_key
        self.PKA = public_key_app
        self.access_token = access_token

    def mediatopic_post(self, photo_url: str, caption: str) -> None:
        """Производит публикацию поста в группе. Публикация медиатопика, 
           который может содержать множество вложенных объектов"""

        #получаем токен-индификатор фото
        photo_token = self.photos_get_upload_url(photo_url)

        #формируем JSON информацию о контенте медиатопика
        attachment = {
                        'media': [
                          {
                            'type': 'text',
                            'text': caption
                          },
                          {
                            'type': 'photo',
                            'list': [
                              { 
                                'id': photo_token
                              }
                            ]
                          }
                        ],
                        "onBehalfOfGroup": "true",
                    "disableComments": "false"
        }

        attachment_json =  json.dumps(attachment)

        #подготавливаем аргументы запроса в соответствии с https://apiok.ru/dev/methods/rest/mediatopic/mediatopic.post
        payload = {
            'application_key': self.PKA,
            'method': 'mediatopic.post',
            'type': 'GROUP_THEME',
            'gid': self.gid,
            'access_token': self.access_token,
            'attachment': attachment_json,
        }
        #формируем подпись
        payload = self.add_mb5_sig(payload)
        
        send_mediatopic_post = requests.post(self.api_server, data=payload)

    def photos_get_upload_url(self, photo_url: str) -> str:
        """Метод запускает процесс добавления фото и возвращает его токен, 
           который должен использоваться для фактической загрузки фотографий"""

        #подготавливаем аргументы запроса в соответствии с https://apiok.ru/dev/methods/rest/photosV2/photosV2.getUploadUrl
        payload = {
            'application_key': self.PKA,
            'method': 'photosV2.getUploadUrl',
            'gid': self.gid,
            'count': '1',
            'access_token': self.access_token,
        }
        #формируем подпись
        payload = self.add_mb5_sig(payload)
        #добавляем подпись в запрос
        #payload['sig'] = sig

        info_request_to_server = requests.post(self.api_server, data=payload)
        respon_from_server_json = json.loads(info_request_to_server.text)
        #получаем идентификатор фото при его загрузки на сервер ОК
        photo_id = respon_from_server_json['photo_ids'][0]
        #получаем адрес для загрузки фото на сервер ОК
        upload_url = respon_from_server_json['upload_url']
        #загружаем фото на сервер ОК (вариант для сетевого расположения фото)
        send_photo_to_server = requests.post(upload_url, files={
                                                                'pic1': ('photo.jpg',\
                                                                 BytesIO(requests.get(photo_url).content), 'image/png'
                                                                        )
                                                                }
        )
        respon_server = json.loads(send_photo_to_server.text)
        #получаем токен-индификатор фото на сервере ОК
        token_photo =  respon_server['photos'][photo_id]['token']

        return token_photo

    def group_get_counters(self, counterTypes='members'):
      """Возвращает основные счётчики объектов группы - количество членов группы, фотографий, фотоальбомов и т.п."""

      #подготавливаем аргументы запроса в соответствии с https://apiok.ru/dev/methods/rest/group/group.getCounters
      payload = {
        'application_key': self.PKA,
        'access_token': self.access_token,
        'method': 'group.getCounters',
        'group_id': self.gid,
        'counterTypes': counterTypes,
      }

      #формируем подпись
      payload = self.add_mb5_sig(payload)

      info_request_to_server = requests.post(self.api_server, data=payload)
      respon_from_server_json = json.loads(info_request_to_server.text)

      return respon_from_server_json['counters']['members']
      
    def add_mb5_sig(self, dictionary: dict) -> dict:
        """Метод производит расчет подписи запроса API OK в соостветствии с https://apiok.ru/dev/methods/
           и добавляет подпись в запрос"""
        #копируем словарь для возможности его безопасного изменения 
        signature_data = dictionary.copy()
        #убираем из списка параметров session_key/access_token при наличии
        [signature_data.pop(key, '') for key in ['session_key', 'access_token']]
        #параметры сортируются лексикографически по ключам
        lexicograph = sorted(signature_data.items())
        #создаем хранилище
        string_payload = ''
        #параметры соединяются в формате ключ=значение
        for pair in lexicograph:
            string_payload = f'{string_payload}{pair[0]}={pair[1]}'

        #sig = MD5(значения_параметров + session_secret_key);           
        sig = hashlib.md5(f'{string_payload}{self.SSK}'.encode()).hexdigest()
        #добавляем подпись в запрос
        dictionary['sig'] = sig

        return dictionary

if __name__ == '__main__':
    pass
    