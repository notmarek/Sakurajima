import requests
import json
from Sakurajima.models import base_models as bm
from Sakurajima.models.chronicle import ChronicleEntry
import datetime


class UserAnimeListEntry(object):
    """A UserAnimeListEntry represents a single show on a user's aniwatch.me 
    anime list.
    """
    def __init__(self, data_dict, network):
        self.__network = network
        self.title = data_dict.get("title", None)
        """The title of the anime."""
        self.episodes_max = data_dict.get("episodes_max", None)
        """The total number of episodes the anime has."""
        self.type = data_dict.get("type", None)
        """The type of the show. For example, the type can anime, special or movie etc."""
        self.cover = data_dict.get("cover", None)
        """The URL to the cover image of the anime."""
        self.anime_id = data_dict.get("details_id", None)
        """The ID of the anime."""
        self.progress = data_dict.get("progress", None)
        """The total number of episodes that the user has watched for this anime."""
        self.airing_start = data_dict.get("airing_start", None)
        """The season the anime started airing."""
        self.cur_episodes = data_dict.get("cur_episodes", None)
        """The total number of episodes that have already aired."""
        if data_dict.get("completed", None) == 1:
            self.status = "completed"
            """The watch status of the anime."""
        elif data_dict.get("planned_to_watch", None) == 1:
            self.status = "planned_to_watch"
        elif data_dict.get("on_hold", None) == 1:
            self.status = "on_hold"
        elif data_dict.get("dropped", None) == 1:
            self.status = "dropped"

    def get_anime(self):
        """Gets the Anime object of the entry.

        :rtype: Anime
        """
        data = {
            "controller": "Anime",
            "action": "getAnime",
            "detail_id": str(self.anime_id),
        }
        return bm.Anime(self.__post(data)["anime"], network=self.__network, api_url=self.__API_URL,)

    def __repr__(self):
        return f"<AnimeListEntry: {self.title}>"


class UserOverview(object):
    """The user's overview. This includes things like the total number of shows 
    watched by type, the user's title and the URL of the user's cover."""
    def __init__(self, data_dict):
        self.anime = UserOverviewWatchType(data_dict["anime"])
        """UserOverviewWatchType object for the animes."""
        self.special = UserOverviewWatchType(data_dict["special"])
        """UserOverviewWatchType object for the specials."""
        self.movie = UserOverviewWatchType(data_dict["movie"])
        """UserOverviewWatchType object for the movies."""
        self.hentai = UserOverviewWatchType(data_dict["hentai"])
        """UserOverviewWatchType object for the hentais."""
        self.stats = UserOverviewStats(data_dict["stats"])
        """The UserOverviewStats object that represents the user's watch stats.
        This includes things like the total number hours watched etc."""
        self.mine = data_dict.get("mine", None)
        self.username = data_dict.get("username", None)
        """The user's aniwatch.me username."""
        self.title = data_dict.get("title", None)
        """The user's title on aniwatch.me"""
        self.admin = data_dict.get("admin", None)
        """If the user is an administrator."""
        self.staff = data_dict.get("staff", None)
        """If the user is a staff."""
        self.cover = data_dict.get("cover", None)
        """The URL to the user's profile cober image."""
        self.friend = data_dict.get("friend", None)
        """The total number of friends that the user has."""

    def __repr__(self):
        return f"<UserOverView: {self.username}>"


class UserOverviewWatchType(object):
    """A generic class that holds data regarding the shows watched of a particular type."""
    def __init__(self, data_dict):
        self.total = data_dict.get("total", None)
        """The total number of shows watched that belong to a particular type."""
        self.episodes = data_dict.get("episodes", None)
        """The total number of episodes watched that belong to a particuler type"""
        self.icon = data_dict.get("icon", None)


class UserOverviewStats(object):
    """Holds data regarding the watch stats of a user."""
    def __init__(self, data_dict):
        self.total = data_dict.get("total", None)
        """The total number of shows that the user has watched, this includes
        all categories like anime, movie annd special etc."""
        self.total_episodes = data_dict.get("total_episodes", None)
        """The total number of episodes that the user has watched. Includes 
        episodes from all categories."""
        self.watched_hours = data_dict.get("watched_hours", None)
        """The total watch time of a user in hours."""
        self.watched_days = data_dict.get("watched_days", None)
        """The total watch time of a user in days."""
        self.mean_score = data_dict.get("mean_score", None)
        """The mean score that the user has given to different shows"""
        self.ratings = data_dict.get("ratings", None)
        """The total number of shows that the user has rated."""


class Friend(object):
    """Represents a user's friend on aniwatch.me"""
    def __init__(self, network, data_dict):
        self.__network = network
        self.username = data_dict.get("username", None)
        self.user_id = data_dict.get("userid", None)
        self.cover_img = data_dict.get("cover", None)
        try:
            self.friends_since = datetime.datetime.utcfromtime(data_dict.get("date", None))
        except:
            self.friends_since = None
    
    def __repr__(self):
        return f"<Friend {self.username}>"

    def unfriend(self):
        """Removes the friend from the user's profile.

        :return: True if the operation is successful, False if an error occured.
        :rtype: bool
        """
        data = {
            "controller": "Profile",
            "action": "removeFriend",
            "friend_id": self.user_id,
        }
        return self.__network.post(data)["success"]

    def get_overview(self):
        """Gets the friend's aniwatch.me overview. 

        :return: A UserOverview object that has data regarding things like total
                 watch time, mean score and total shows watched etc.
        :rtype: `UserOverview <user_overview>`
        """
        data = {
            "controller": "Profile",
            "action": "getOverview",
            "profile_id": self.user_id,
        }
        return UserOverview(self.__network.post(data)["overview"])

    def get_chronicle(self, page=1):
        """Gets the friend's chronicle. A chronicle tracks a user's watch history.

        :param page: The page of the chronicle that you want to get, defaults to 1
        :type page: int, optional
        :return: A list of ChronicleEntry objects.
        :rtype: list[ChronicleEntry]
        """
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