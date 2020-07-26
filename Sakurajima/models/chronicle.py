import requests
import json
import datetime


class ChronicleEntry(object):
    """A chronicle tracks a user's watch history. A chronicle maybe specific to a single
    series or it maybe a more general user chronicle. A ChronicleEntry object represents
    a single in entry in a chronicle."""
    def __init__(self, data_dict, network, api_url):
        self.__network = network
        self.__API_URL = api_url
        self.episode = data_dict.get("episode", None)
        """The episode number of the watched episode."""
        self.anime_id = data_dict.get("id", None)
        """The ID of the anime that the chronicle entry relates to."""
        self.anime_title = data_dict.get("anime_title", None)
        """The title of the anime that the chronicle entry relates to."""
        self.ep_title = data_dict.get("ep_title", None)
        """The title of the episode that the chronicle entry relates to."""
        self.chronicle_id = data_dict.get("chronicle_id", None)
        """The ID of the chronicle entry."""
        try:
            self.date = datetime.datetime.utcfromtimestamp(data_dict["date"])
            """The date the chronicle entry was created."""
        except Exception:
            self.date = None

    def __repr__(self):
        return f"<ChronicleEntry: {self.chronicle_id}>"

    def remove_chronicle_entry(self):
        """Removes the entry from the user's chronicle.

        :return: True if the operation is successful, False if an error occured.
        :rtype: bool
        """
        data = {
            "controller": "Profile",
            "action": "removeChronicleEntry",
            "chronicle_id": self.chronicle_id,
        }
        return self.__network.post(data)["success"]
