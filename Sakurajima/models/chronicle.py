import requests
import json
import datetime


class ChronicleEntry(object):
    def __init__(self, data_dict, session, api_url):
        self.__session = session
        self.__API_URL = api_url
        self.episode = data_dict.get("episode", None)
        self.anime_id = data_dict.get("id", None)
        self.anime_title = data_dict.get("anime_title", None)
        self.ep_title = data_dict.get("ep_title", None)
        self.chronicle_id = data_dict.get("chronicle_id", None)
        try:
            self.date = datetime.datetime.utcfromtimestamp(data_dict["date"])
        except Exception:
            self.date = None

    def __post(self, data):
        try:
            res = self.__session.post(self.__API_URL, json=data)
            return res.json()
        except Exception as e:
            self.__session.close()
            raise e

    def __repr__(self):
        return f"<ChronicleEntry: {self.chronicle_id}>"

    def remove_chronicle_entry(self):
        data = {
            "controller": "Profile",
            "action": "removeChronicleEntry",
            "chronicle_id": self.chronicle_id,
        }
        return self.__post(data)
