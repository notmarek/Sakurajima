import requests
import json
from . base_models import Anime

class RecommendationEntry(object):
    def __init__(self, data_dict, headers, cookies, api_url):
        self.headers = headers
        self.cookies = cookies
        self.API_URL = api_url
        self.title = data_dict.get('title', None)
        self.episodes_max = data_dict.get('episodes_max', None)
        self.type = data_dict.get('type', None)
        self.anime_id = data_dict.get('detail_id', None)
        self.cover = data_dict.get('cover', None)
        self.airing_start = data_dict.get('airing_start', None)
        self.recommendations = data_dict.get('recommendations', None)
        self.d_status = data_dict.get('d_status', None)
        self.has_special = data_dict.get('hasSpecial', None)
        self.progress = data_dict.get('progress', None)
        self.cur_episodes = data_dict.get('cur_episodes', None)

    def __post(self, data):
        with requests.post(self.API_URL, headers=self.headers, json=data, cookies=self.cookies) as url:
            return json.loads(url.text)

    def __repr__(self):
        return f'<RecommendationEntry: {self.title}>'
    
    def get_anime(self):
        data = {"controller": "Anime", "action": "getAnime", "detail_id": str(self.anime_id)}
        return Anime(self.__post(data)['anime'], headers=self.headers, cookies = self.cookies, api_url=self.API_URL)
