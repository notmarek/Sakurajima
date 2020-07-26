import requests
import json
import datetime

class Media(object):
    """Contains media entries for categories like openings, endings and OSTs"""

    def __init__(self, data_dict, network, anime_id):
        self.__network = network
        self.anime_id = anime_id
        """The ID of the anime to which the media belons."""
        self.theme_songs = [
            MediaEntry(data, self.__network, self.__API_URL) for data in data_dict.get("Theme Songs", [])
        ]
        """Theme songs for the anime."""
        self.openings = [MediaEntry(data, self.__network) for data in data_dict.get("Openings", [])]
        """Opening songs for the anime."""
        self.endings = [MediaEntry(data, self.__network) for data in data_dict.get("Endings", [])]
        """Ending songs for the anime."""
        self.osts = [MediaEntry(data, self.__network) for data in data_dict.get("OSTs", [])]
        """The official sound tracks for the anime."""
    
    def __repr__(self):
        return f"<Media for Anime: {self.anime_id}>"


class MediaEntry(object):
    """Represents a single media entry and contains all the relevant data related
    to the entry like media_id and favorite status."""

    def __init__(self, data_dict, network):
        self.__network = network
        self.title = data_dict.get("media_title", None)
        """The title of the media."""
        self.type = data_dict.get("media_type", None)
        """The type of the media, example opening, ending etc"""
        self.value = data_dict.get("media_value", None)
        self.favorites = data_dict.get("media_favorites", None)
        """The number of users who have favorited the media."""
        self.is_favorited = data_dict.get("media_hasFaved", None)
        """If the user has favorited the media."""
        self.id = data_dict.get("media_id", None)
        """The ID of the media."""
        self.occurence = data_dict.get("media_occurence", None)
        self.thumbnail = data_dict.get("media_thumb", None)
        """The url to the thumbnail of the media."""

    def __repr__(self):
        return f"<Media Entry {self.title}>"

    def favorite_media(self):
        """Marks the media as favorite.

        :return: True if the operation is successful, False if an error occured.
        :rtype: bool
        """
        data = {"controller": "Media", "action": "favMedia", "media_id": str(self.id)}
        return self.__network.post(data)["success"]


class UserMedia(object):
    def __init__(self, data_dict, network):
        self.__network = network
        self.title = data_dict.get("title", None)
        """The title of the media."""
        self.media_id = data_dict.get("media_id", None)
        """The ID of the media."""
        try:
            self.date = datetime.datetime.utcfromtimestamp(data_dict["date"])
            """The date the media was created."""
        except:
            self.date = None

    def __repr__(self):
        return f"UserMedia: {self.title}"
