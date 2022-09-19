import requests, json
from datetime import datetime as dt


class IG:

    def __init__(self, API_TOKEN: str, FB_TOKEN_PAGE: str, app_secret: str) -> None:
        
        self.API_TOKEN = API_TOKEN
        self.FB_TOKEN_PAGE = FB_TOKEN_PAGE
        self.app_secret = app_secret
        self.main_URL = 'https://graph.facebook.com/v10.0'
        # получаем идентификатор страницы Facebook
        self.page_id = self.get_page_id()
        # получаем идентификатор учетной записи Instagram
        self.ig_user_id  = self.get_ig_user_id()

    def get_page_id(self):
        """Возвращается идентификатор страницы Facebook, подключенной к учетной записи Instagram
        {page-id}"""
        try:
            request_page_user = f'{self.main_URL}/me/accounts?access_token={self.API_TOKEN}'
            response_page_user = requests.get(request_page_user)
        
            page_user = json.loads(response_page_user.text)
            id = page_user['data'][0]['id']
            return id

        except Exception as error:
            print(f'При получении идентификатора страницы Facebook возникла ошибка:\n{error.__class__.__name__}: {error}')

    
    def get_ig_user_id(self):
        """Возвращается идентификатор учетной записи Instagram
        {ig_user_id}"""
        try:
            request_ig_user = f'{self.main_URL}/{self.page_id}?fields=instagram_business_account&access_token={self.API_TOKEN}'
            response_ig_user = requests.get(request_ig_user)
        
            ig_user = json.loads(response_ig_user.text)
            id = ig_user['instagram_business_account']['id']
            return id
        
        except Exception as error:
            print(f'При получении идентификатора учетной записи Instagram возникла ошибка:\n{error.__class__.__name__}: {error}')


    def debug_token_data_access(self, expiration_days = 10):
        """Проверяет срок действия токена API Graph. Возвращает TRUE, 
           если срок окончания действия (expiration_days) более 10 дней. 
           Если менее 3 дней - False"""
        try:
            request_debug_token = f'https://graph.facebook.com/debug_token?input_token={self.API_TOKEN}&access_token={self.API_TOKEN}'
            response_debug_token = requests.get(request_debug_token)

            json_debug_token = json.loads(response_debug_token.text)
        
            data_access_expires_at = json_debug_token['data']['data_access_expires_at']
            self.app_id = json_debug_token['data']['app_id']
        
            data_access = (dt.fromtimestamp(data_access_expires_at)-dt.now()).days

            return True if data_access > expiration_days else False
        
        except Exception as error:
            print(f'При проверке срока действия токена API Graph возникла ошибка:\n{error.__class__.__name__}: {error}')
    
    def get_long_lived_access_token(self):
        """Производит обмен краткосрочного токена на долгосрочный 
           или продляет долгосрочный токен API Graph.->
           Возвращает новое значение токена API Graph"""
        try:
            request_long_lived_token = f'{self.main_URL}/oauth/access_token?grant_type=fb_exchange_token&client_id={self.app_id}&client_secret={self.app_secret}&fb_exchange_token={self.API_TOKEN}'
            response_long_lived_token = requests.get(request_long_lived_token)

            long_lived_token = json.loads(response_long_lived_token.text)
            access_token = long_lived_token['access_token']
            
            # переопределяем токен
            self.API_TOKEN = access_token

            return access_token
        
        except Exception as error:
            print(f'При обмене(продлении) токена API Graph возникла ошибка:\n{error.__class__.__name__}: {error}')
        

    def get_ig_content_publishing_limit(self):
        """Возвращается текущее использование публикации контента пользователем Instagram за сутки (max - 25)"""
        try:
            request_publishing_limit = f'{self.main_URL}/{self.ig_user_id}/content_publishing_limit?access_token={self.API_TOKEN}'
            response_publishing_limit = requests.get(request_publishing_limit)
        
            publishing_limit = json.loads(response_publishing_limit.text)
            quota_usage = publishing_limit['data'][0]['quota_usage']

            return quota_usage
                
        except Exception as error:
            print(f'При определении текущего лимита использования публикаций Instagram возникла ошибка:\n{error.__class__.__name__}: {error}')
            
    def ig_content_publishing(self, image_url:str, caption: str):
        """Производит публикацию поста в Instagram"""
            
        request_container_id = f'{self.main_URL}/{self.ig_user_id}/media?'
    
        payload = {
            'image_url': image_url,
            'caption': caption,
            'access_token': self.API_TOKEN
        }
        response_container_id = requests.post(request_container_id, data=payload)
        json_container_id = json.loads(response_container_id.text)
        
        try:
            container_id = json_container_id['id']
        except:
            error_id = json_container_id['error']['message']
            # для статистики 
            print(f'При публикации поста возникла ошибка: {error_id}')
            return
        
        request_media_publish = f'{self.main_URL}/{self.ig_user_id}/media_publish?creation_id={container_id}&access_token={self.API_TOKEN}'
        requests.post(request_media_publish)

    def fb_content_publishing(self, photo: str, caption: str):
        """Производит публикацию поста в Facebook"""
        try:

            request_content_publishing = f'https://graph.facebook.com/{self.page_id}/photos?'

            response_content_publishing = requests.post(request_content_publishing, data={
                                                        'url': photo,
                                                        'caption': caption,
                                                        'access_token': self.FB_TOKEN_PAGE
                                                        }
            )

            json_request_content_publishing = json.loads(response_content_publishing.text)
            json_request_content_publishing['id']
        
        except Exception as error:
            print(f'При публикации поста в Facebook возникла ошибка:\n{error.__class__.__name__}: {error}')

    def get_followers(self, fields='followers_count'):
        """Получение количества подписчиков в Insagram.
           Также для Instagram возможны поля: biography, id, ig_id, followers_count, follows_count, media_count, name,
           profile_picture_url, username, website;
           для FB - https://developers.facebook.com/docs/graph-api/reference/page/"""

        def respone_ig_and_fb(id_page_ig_and_fb):

            request_container_id = f'{self.main_URL}/{id_page_ig_and_fb}'

            payload = {
                'fields' : fields,
                'access_token': self.API_TOKEN
            }

            response_container_id = requests.get(request_container_id, params=payload)

            return json.loads(response_container_id.text)[fields]

        ig_follower = respone_ig_and_fb(self.ig_user_id)
        fb_follower = respone_ig_and_fb(self.page_id)

        return ig_follower, fb_follower

if __name__ == '__main__':
    pass