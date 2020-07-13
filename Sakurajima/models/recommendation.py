import json
from Sakurajima.models import base_models as bm


class RecommendationEntry(object):
    def __init__(self, data_dict, session, api_url):
        self.__session = session
        self.__API_URL = api_url
        self.title = data_dict.get("title", None)
        self.episodes_max = data_dict.get("episodes_max", None)
        self.type = data_dict.get("type", None)
        self.anime_id = data_dict.get("detail_id", None)
        self.cover = data_dict.get("cover", None)
        self.airing_start = data_dict.get("airing_start", None)
        self.recommendations = data_dict.get("recommendations", None)
        self.d_status = data_dict.get("d_status", None)
        self.has_special = data_dict.get("hasSpecial", None)
        self.progress = data_dict.get("progress", None)
        self.cur_episodes = data_dict.get("cur_episodes", None)

    def __post(self, data):
        try:
            res = self.__session.post(self.__API_URL, json=data)
            return res.json()
        except Exception as e:
            self.__session.close()
            raise e

    def __repr__(self):
        return f"<RecommendationEntry: {self.title}>"

    def get_anime(self):
        data = {
            "controller": "Anime",
            "action": "getAnime",
            "detail_id": str(self.anime_id),
        }
        return bm.Anime(self.__post(data)["anime"], session=self.__session, api_url=self.__API_URL,)
