import requests
import json
from Sakurajima.models import base_models as bm


class UserAnimeListEntry(object):
    def __init__(self, data_dict, headers, cookies, api_url):
        self.__headers = headers
        self.__cookies = cookies
        self.__API_URL = api_url
        self.title = data_dict.get("title", None)
        self.episodes_max = data_dict.get("episodes_max", None)
        self.type = data_dict.get("type", None)
        self.cover = data_dict.get("cover", None)
        self.anime_id = data_dict.get("details_id", None)
        self.progress = data_dict.get("progress", None)
        self.airing_start = data_dict.get("airing_start", None)
        self.cur_episodes = data_dict.get("cur_episodes", None)
        if data_dict.get("completed", None) == 1:
            self.status = "completed"
        elif data_dict.get("planned_to_watch", None) == 1:
            self.status = "planned_to_watch"
        elif data_dict.get("on_hold", None) == 1:
            self.status = "on_hold"
        elif data_dict.get("dropped", None) == 1:
            self.status = "dropped"

    def __post(self, data):
        with requests.post(
            self.__API_URL, headers=self.__headers, json=data, cookies=self.__cookies
        ) as url:
            return json.loads(url.text)

    def get_anime(self):
        data = {
            "controller": "Anime",
            "action": "getAnime",
            "detail_id": str(self.anime_id),
        }
        return bm.Anime(
            self.__post(data)["anime"],
            headers=self.__headers,
            cookies=self.__cookies,
            api_url=self.__API_URL,
        )

    def __repr__(self):
        return f"<AnimeListEntry : {self.title}>"


class UserOverview(object):
    def __init__(self, data_dict):
        self.anime = UserOverviewType(data_dict["anime"])
        self.special = UserOverviewType(data_dict["special"])
        self.movie = UserOverviewType(data_dict["movie"])
        self.hentai = UserOverviewType(data_dict["hentai"])
        self.stats = UserOverviewStats(data_dict["stats"])
        self.mine = data_dict.get("mine", None)
        self.username = data_dict.get("username", None)
        self.title = data_dict.get("title", None)
        self.admin = data_dict.get("admin", None)
        self.staff = data_dict.get("staff", None)
        self.cover = data_dict.get("cover", None)
        self.friend = data_dict.get("friend", None)

    def __repr__(self):
        return f"<UserOverView: {self.username}>"


class UserOverviewType(object):
    def __init__(self, data_dict):
        self.total = data_dict.get("total", None)
        self.episodes = data_dict.get("episodes", None)
        self.icon = data_dict.get("icon", None)


class UserOverviewStats(object):
    def __init__(self, data_dict):
        self.total = data_dict.get("total", None)
        self.total_episodes = data_dict.get("total_episodes", None)
        self.watched_hours = data_dict.get("watched_hours", None)
        self.watched_days = data_dict.get("watched_days", None)
        self.mean_score = data_dict.get("mean_score", None)
        self.ratings = data_dict.get("ratings", None)
