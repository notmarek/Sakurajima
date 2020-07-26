import json
from Sakurajima.models import base_models as bm


class RecommendationEntry(object):
    def __init__(self, data_dict, network):
        self.__network = network
        self.title = data_dict.get("title", None)
        """The title of the recommeneded anime."""
        self.episodes_max = data_dict.get("episodes_max", None)
        """The total number of episodes that the recommended anime has."""
        self.type = data_dict.get("type", None)
        """The type of the recommended anime. For example, anime, special or movie."""
        self.anime_id = data_dict.get("detail_id", None)
        """The ID of the recommended anime."""
        self.cover = data_dict.get("cover", None)
        """The URL to the cover image of the recommended anime."""
        self.airing_start = data_dict.get("airing_start", None)
        """The season when the recommended anime started airing."""
        self.recommendations = data_dict.get("recommendations", None)
        """The number of users that have recommened this anime."""
        self.d_status = data_dict.get("d_status", None)
        """The d_status of the anime? If you figure this out please let us know by opening an issue
        on our `repo <https://github.com/veselysps/Sakurajima/issues>`_"""
        self.has_special = data_dict.get("hasSpecial", None)
        """If the recommended anime has a special."""
        self.progress = data_dict.get("progress", None)
        """The user's progress for the recommended anime."""
        self.cur_episodes = data_dict.get("cur_episodes", None)
        """The number of currently aired episodes of the recommended anime."""


    def __repr__(self):
        return f"<RecommendationEntry: {self.title}>"

    def get_anime(self):
        """Gets the Anime object of the anime recommended in the RecommendationEntry.

        :rtype: `Anime <anime.html>`_
        """
        data = {
            "controller": "Anime",
            "action": "getAnime",
            "detail_id": str(self.anime_id),
        }
        return bm.Anime(self.__post(data)["anime"], network=self.__network, api_url=self.__API_URL,)
