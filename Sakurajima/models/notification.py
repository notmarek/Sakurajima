import requests
import json
import datetime


class Notification(object):
    def __init__(self, data_dict, session, api_url):
        self.__session = session
        self.__API_URL = api_url
        self.data_dict = data_dict
        self.id = data_dict.get("id", None)
        self.type = data_dict.get("type", None)
        self.mode = data_dict.get("mode", None)
        self.content = data_dict.get("content", None)
        try:
            self.time = datetime.datetime.utcfromtimestamp(data_dict.get("time", None))
        except Exception:
            self.time = data_dict.get("time", None)
        self.seen = data_dict.get("seen", None)
        self.href_blank = data_dict.get("href_blank", None)
        self.href = data_dict.get("href", None)

    def __post(self, data):
        with self.__session.post(self.__API_URL, json=data) as url:
            return json.loads(url.text)

    def get_dict(self):
        return self.data_dict

    def toggle_seen(self):
        data = {
            "controller": "Profile",
            "action": "toggleNotificationSeen",
            "id": self.id,
        }
        return self.__post(data)["success"]

    def delete(self):
        data = {"controller": "Profile", "action": "deleteNotification", "id": self.id}
        return self.__post(data)["success"]

    def __repr__(self):
        return f"<Notification ID: {self.id}, Date: {self.time}>"
