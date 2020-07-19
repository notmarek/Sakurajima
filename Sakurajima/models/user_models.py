import requests
import json
from Sakurajima.models import base_models as bm
from Sakurajima.models.chronicle import ChronicleEntry


class UserAnimeListEntry(object):
    def __init__(self, data_dict, network, api_url):
        self.__network = network
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

    def get_anime(self):
        data = {
            "controller": "Anime",
            "action": "getAnime",
            "detail_id": str(self.anime_id),
        }
        return bm.Anime(self.__post(data)["anime"], network=self.__network, api_url=self.__API_URL,)

    def __repr__(self):
        return f"<AnimeListEntry: {self.title}>"


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


class Friend(object):
    def __init__(self, network, data_dict):
        self.__network = network
        self.username = data_dict.get("username", None)
        self.user_id = data_dict.get("userid", None)
        self.cover_img = data_dict.get("cover", None)
        self.friends_since = data_dict.get("date", None)

    def __repr__(self):
        return f"<Friend {self.username}>"

    def unfriend(self):
        data = {
            "controller": "Profile",
            "action": "removeFriend",
            "friend_id": self.user_id,
        }
        return self.__network.post(data)

    def get_overview(self):
        data = {
            "controller": "Profile",
            "action": "getOverview",
            "profile_id": self.user_id,
        }
        return UserOverview(self.__network.post(data)["overview"])

    def get_chronicle(self, page=1):
        data = {
            "controller": "Profile",
            "action": "getChronicle",
            "profile_id": self.user_id,
            "page": page,
        }
        return [
            ChronicleEntry(data_dict, self.__network, self.__network.API_URL)
            for data_dict in self.__network.post(data)["chronicle"]
        ]


class FriendRequestIncoming(object):
    def __init__(self, network, data_dict):
        self.__network = network
        self.username = data_dict.get("username", None)
        self.user_id = data_dict.get("userid", None)
        self.cover_img = data_dict.get("cover", None)
        self.date = data_dict.get("date", None)

    def accept(self):
        data = {
            "controller": "Profile",
            "action": "acceptRequest",
            "friend_id": self.user_id,
        }
        return self.__network.post(data)["success"]

    def decline(self):
        data = {
            "controller": "Profile",
            "action": "rejectRequest",
            "friend_id": self.user_id,
        }
        return self.__network.post(data)["success"]

    def __repr__(self):
        return f"<FriendRequestIncoming: {self.username}>"


class FriendRequestOutgoing(object):
    def __init__(self, network, data_dict):
        self.__network = network
        self.username = data_dict.get("username", None)
        self.user_id = data_dict.get("userid", None)
        self.cover_img = data_dict.get("cover", None)
        self.date = data_dict.get("date", None)

    def withdraw(self):
        data = {
            "controller": "Profile",
            "action": "withdrawRequest",
            "friend_id": self.user_id,
        }
        return self.__network.post(data)

    def __repr__(self):
        return f"<FriendRequestOutgoing: {self.username}>"