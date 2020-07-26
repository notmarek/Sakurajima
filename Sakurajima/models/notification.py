import requests
import json
import datetime


class Notification(object):
    def __init__(self, data_dict, network):
        self.__network = network
        self.data_dict = data_dict
        self.id = data_dict.get("id", None)
        """The ID of the notification."""
        self.type = data_dict.get("type", None)
        """The notification type, example if the notification is for a recently aired anime."""
        self.mode = data_dict.get("mode", None)
        self.content = data_dict.get("content", None)
        """The content or the body of the notification."""
        try:
            self.time = datetime.datetime.utcfromtimestamp(data_dict.get("time", None))
            """The time the notification was issued."""
        except Exception:
            self.time = data_dict.get("time", None)
        self.seen = data_dict.get("seen", None)
        """The "seen" status of the notification."""
        self.href_blank = data_dict.get("href_blank", None)
        """If the notification has an associated URL."""
        self.href = data_dict.get("href", None)
        """The URL associated with the notification. If the nottification is for a 
        recently aired episode, this is the URL to that episode."""

    def get_dict(self):
        return self.data_dict

    def toggle_seen(self):
        """Toggles the "seen" status of the notification.

        :return: True if the operation is successful, False if an error occured.
        :rtype: bool
        """         
        data = {
            "controller": "Profile",
            "action": "toggleNotificationSeen",
            "id": self.id,
        }
        return self.__network.post(data)["success"]

    def delete(self):
        """Deletes the notification from the user's account.

        :return: True if the operation is successful, False if an error occured.
        :rtype: bool
        """
        data = {"controller": "Profile", "action": "deleteNotification", "id": self.id}
        return self.__network.post(data)["success"]

    def __repr__(self):
        return f"<Notification ID: {self.id}, Date: {self.time}>"
