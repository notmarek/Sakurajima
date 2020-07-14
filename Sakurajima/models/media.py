import requests
import json


class Media(object):
    """Contains media entries for categories like openings, endings and OSTs"""

    def __init__(self, data_dict, network, api_url, anime_id):
        self.__network = network
        self.__API_URL = api_url
        self.anime_id = anime_id
        self.theme_songs = [
            MediaEntry(data, self.__network, self.__API_URL) for data in data_dict.get("Theme Songs", [])
        ]
        self.openings = [MediaEntry(data, self.__network, self.__API_URL) for data in data_dict.get("Openings", [])]
        self.endings = [MediaEntry(data, self.__network, self.__API_URL) for data in data_dict.get("Endings", [])]
        self.osts = [MediaEntry(data, self.__network, self.__API_URL) for data in data_dict.get("OSTs", [])]

    def __repr__(self):
        return f"<Media for Anime: {self.anime_id}>"


class MediaEntry(object):
    """Represents a single media entry and contains all the relevant data related
    to the entry like media_id and favorite status."""

    def __init__(self, data_dict, network, api_url):
        self.__network = network
        self.API_URL = api_url
        self.title = data_dict.get("media_title", None)
        self.type = data_dict.get("media_type", None)
        self.value = data_dict.get("media_value", None)
        self.favorites = data_dict.get("media_favorites", None)
        self.is_favorited = data_dict.get("media_hasFaved", None)
        self.id = data_dict.get("media_id", None)
        self.occurence = data_dict.get("media_occurence", None)
        self.thumbnail = data_dict.get("media_thumb", None)

    def __repr__(self):
        return f"<Media Entry {self.title}>"

    def favorite_media(self):
        """Marks the media as a favotite"""
        data = {"controller": "Media", "action": "favMedia", "media_id": str(self.id)}
        return self.__network.post(data)["success"]


class UserMedia(object):
    def __init__(self, data_dict, network, api_url):
        self.__network = network
        self.API_URL = api_url
        self.title = data_dict.get("title", None)
        self.media_id = data_dict.get("media_id", None)
        try:
            self.date = date_time.utcfromtimestamp(data_dict["date"])
        except:
            self.date = None

    def __repr__(self):
        return f"UserMedia: {self.title}"
