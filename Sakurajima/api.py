import requests
import json
import base64
import random
from urllib.parse import unquote
from Sakurajima.models import (
    Anime,
    RecommendationEntry,
    Relation,
    AniWatchEpisode,
    Episode,
    ChronicleEntry,
    UserAnimeListEntry,
    UserMedia,
    UserOverview,
    AniwatchStats,
    Notification,
    WatchListEntry,
    Media,
)
from Sakurajima.models.user_models import Friend, FriendRequestIncoming, FriendRequestOutgoing
from Sakurajima.utils.episode_list import EpisodeList
from Sakurajima.utils.network import Network


class Sakurajima:

    """
    Sakurajima at its core, is a wrapper around the aniwatch.me API. However,
    it does include some additional functionality, namely the ability to download 
    episodes of your favorite anime in your prefered quality. 

    Sakurajima requires you to have an aniwatch account. It requires you to provide 
    your username, your user ID and your auth token. For instructions on how to get
    those, checkout `this 
    <https://github.com/veselysps/Sakurajima/wiki/How-to-get-username,-user-ID,-authorization-token.>`_ wiki.  
    """

    def __init__(
        self, username=None, userId=None, authToken=None, proxies=None, endpoint="https://aniwatch.me/api/ajax/APIHandle"
    ):

        self.API_URL = endpoint
        self.network = Network(username, userId, authToken, proxies, endpoint)

    @classmethod
    def using_proxy(
        cls, proxy_file=None, username=None, userId=None, authToken=None, endpoint="https://aniwatch.me/api/ajax/APIHandle"
        ):
        """An alternate constructor that reads a file containing a list of proxies
        and chooses a random proxy to use with Sakurajima.

        :param username: The username of the user, defaults to None
        :type username: str, optional
        :param userId: The user ID of the user, defaults to None
        :type userId: int, optional
        :param authToken: The auth token of the user, defaults to None
        :type authToken: str, optional
        :param proxy_file: The file containing the list of proxies, defaults to None
        :type proxy_file: [type], optional
        :param endpoint: [description], defaults to "https://aniwatch.me/api/ajax/APIHandle"
        :type endpoint: str, optional
        :return: A Sakurajima object configured to use a proxy.
        :rtype: Sakurajima
        """
        with open(proxy_file, "r") as proxy_file_handle:
            proxies = proxy_file_handle.readlines()
        proxy = random.choice(proxies).replace("\n", "")
        return cls(username, userId, authToken, {"https": proxy})            
    
    @classmethod
    def from_cookie(cls, cookie_file):
        """An alternate constructor that reads a cookie file and automatically extracts
        the data neccasary to initialize Sakurajime

        :param cookie_file: The file containing the cookie.
        :type cookie_file: str
        :rtype: :class:`Sakurajima`
        """
        with open(cookie_file, "r") as cookie_file_handle:
            cookie = json.loads(unquote(cookie_file_handle.read()))
        return cls(cookie["username"], cookie["userid"], cookie["auth"])

    def get_episode(self, episode_id, lang="en-US"):
        """Gets an AniWatchEpisode by its episode ID.

        :param episode_id: The episode ID of the episode you want to get.
        :type episode_id: int
        :param lang: Language of the episode you want to get, defaults to "en-US"
                    (English Subbed)
        :type lang: str, optional
        :return: An AniWatchEpisode object which has data like streams and lamguages. 
        :rtype: :class:`AniWatchEpisode`
        """
        data = {
            "controller": "Anime",
            "action": "watchAnime",
            "lang": lang,
            "ep_id": episode_id,
            "hoster": "",
        }
        return AniWatchEpisode(self.network.post(data), episode_id)

    def get_episodes(self, anime_id: int):
        """Gets an EpisodeList object which contains all the
        available episodes of a given anime.

        :param anime_id: The ID of the anime whose episodes you want.
        :type anime_id: int
        :return: An EpisodeList object. An EpisodeList is very similar to a normal list,
                 you can access item on a specific index the same way you would do for
                 a normal list. Check out the EpisodeList documentation for further details.
        :rtype: :class:`EpisodeList`
        """
        data = {
            "controller": "Anime",
            "action": "getEpisodes",
            "detail_id": str(anime_id),
        }
        return EpisodeList(
            [
                Episode(data_dict, self.network, self.API_URL, anime_id)
                for data_dict in self.network.post(data)["episodes"]
            ]
        )

    def get_anime(self, anime_id: int):
        """Gets an anime by its ID.

        :param anime_id: ID of the anime you want to get.
        :type anime_id: int
        :return: An Anime object that has all the relevant details regarding
                 a single anime like title, description, score, number of episodes etc.
        :rtype: Anime
        """
        data = {"controller": "Anime", "action": "getAnime", "detail_id": str(anime_id)}
        return Anime(self.network.post(data)["anime"], network=self.network, api_url=self.API_URL,)

    def get_recommendations(self, anime_id: int):
        """Gets a list of recommendations for an anime.

        :param anime_id: The ID of the anime whose recommendation you want to get.
        :type anime_id: int
        :return: A list of ReccomendationEntry object where each object represents a 
                 single recommendation.
        :rtype: list[RecommendationEntry]
        """
        data = {
            "controller": "Anime",
            "action": "getRecommendations",
            "detail_id": str(anime_id),
        }
        return [
            RecommendationEntry(data_dict, self.network)
            for data_dict in self.network.post(data)["entries"]
        ]

    def get_relation(self, relation_id: int):
        """Gets the relations of an anime by its relation ID.

        :param relation_id: Relation ID of the anime whose relations you want to get.
        :type relation_id: int
        :return: A Relation object that contains all the details of a relation.
        :rtype: Relation
        """
        data = {
            "controller": "Relation",
            "action": "getRelation",
            "relation_id": relation_id,
        }
        return Relation(self.network.post(data)["relation"])

    def get_seasonal_anime(self, index="null", year="null"):
        """Gets current seasonal animes.

        :param index: [description], defaults to "null"
        :type index: str, optional
        :param year: [description], defaults to "null"
        :type year: str, optional
        :return: A list of  Anime objects.  
        :rtype: list[Anime]
        """
        data = {
            "controller": "Anime",
            "action": "getSeasonalAnime",
            "current_index": index,
            "current_year": year,
        }
        return [Anime(data_dict, self.network, self.API_URL) for data_dict in self.network.post(data)["entries"]]

    def get_latest_releases(self):
        """Gets the latest anime releases. This includes currently airing 
        animes.

        :return: List of Anime objects. 
        :rtype: list[Anime]
        """
        data = {"controller": "Anime", "action": "getLatestReleases"}
        return [Anime(data_dict, self.network, self.API_URL) for data_dict in self.network.post(data)["entries"]]

    def get_latest_uploads(self):
        """Gets latest uploads on "aniwatch.me". This includes animes that are not airing 
        currently.

        :return: A list of Anime objects.
        :rtype: list[Anime]
        """
        data = {"controller": "Anime", "action": "getLatestUploads"}
        return [Anime(data_dict, self.network, self.API_URL) for data_dict in self.network.post(data)["entries"]]

    def get_latest_anime(self):
        """Gets the latest animes on "aniwatch.me"

        :return: A list of Anime objects.
        :rtype: list[Anime]
        """
        data = {"controller": "Anime", "action": "getLatestAnime"}
        return [Anime(data_dict, self.network, self.API_URL) for data_dict in self.network.post(data)["entries"]]

    def get_random_anime(self):
        """Gets a random anime from the aniwatch.me library.

        :return: An Anime object representing a random anime.
        :rtype: Anime
        """
        data = {"controller": "Anime", "action": "getRandomAnime"}
        return Anime(self.network.post(data)["entries"][0], self.network, self.API_URL)

    def get_airing_anime(self, randomize=False):
        """Gets currently airing anime arranged according to weekdays.

        :param randomize: [description],
                          defaults to False
        :type randomize: bool, optional
        :return: A dictionary with weekdays as keys and corresponding list of Anime
                 objects as values. 
        :rtype: dict
        """
        data = {
            "controller": "Anime",
            "action": "getAiringAnime",
            "randomize": randomize,
        }
        airing_anime_response = self.network.post(data)["entries"]
        airing_anime = {}
        for day, animes in airing_anime_response.items():
            airing_anime[day] = [Anime(anime_dict, self.network, self.API_URL) for anime_dict in animes]
        return airing_anime

    def get_popular_anime(self, page=1):
        """Gets all time popular anime.

        :param page: Page number of the popularity chart that you want, defaults to 1
        :type page: int, optional
        :return: A list of Anime objects
        :rtype: list[Anime]
        """
        data = {"controller": "Anime", "action": "getPopularAnime", "page": page}
        return [Anime(data_dict, self.network, self.API_URL) for data_dict in self.network.post(data)["entries"]]

    def get_popular_seasonal_anime(self, page=1):
        """Gets popular anime of the current season.

        :param page: Page number of the popularity chart that you want, defaults to 1
        :type page: int, optional
        :return: A list of Anime objects.
        :rtype: list[Anime]
        """
        data = {"controller": "Anime", "action": "getPopularSeasonals", "page": page}
        return [Anime(data_dict, self.network, self.API_URL) for data_dict in self.network.post(data)["entries"]]

    def get_popular_upcoming_anime(self, page=1):
        """Gets popular anime that have not started airing yet.

        :param page: Page number of the popularity chart that you want, defaults to 1
        :type page: int, optional
        :return: A list of Anime objects.
        :rtype: list[Anime]
        """
        data = {"controller": "Anime", "action": "getPopularUpcomings", "page": page}
        return [Anime(data_dict, self.network, self.API_URL) for data_dict in self.network.post(data)["entries"]]

    def get_hot_anime(self, page=1):
        # TODO inspect this to figure out a correct description.
        data = {"controller": "Anime", "action": "getHotAnime", "page": page}
        return [Anime(data_dict, self.network, self.API_URL) for data_dict in self.network.post(data)["entries"]]

    def get_best_rated_anime(self, page=1):
        """Gets the highest rated animes on "aniwatch.me". 

        :param page: Page number of the popularity chart that you want, defaults to 1
        :type page: int, optional
        :return: A list of Anime objetcs.
        :rtype: list[Anime]
        """
        data = {"controller": "Anime", "action": "getBestRatedAnime", "page": page}
        return [Anime(data_dict, self.network, self.API_URL) for data_dict in self.network.post(data)["entries"]]

    def add_recommendation(self, anime_id: int, recommended_anime_id: int):
        """Submit a recommendation for an anime.

        :param anime_id: The ID of the anime where you want to submit the recommendation.
        :type anime_id: int
        :param recommended_anime_id: The ID of the anime that you want to recommend.
        :type recommended_anime_id: int
        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Anime",
            "action": "addRecommendation",
            "detail_id": str(anime_id),
            "recommendation": str(recommended_anime_id),
        }
        return self.network.post(data)

    def get_stats(self):
        """Gets the aniwatch.me site stats. This includes things like the total
        number of streams of a given quality, total users, total number of anime, movie, 
        special entries in the aniwatch.me library.

        :return: An AniwatchStats object which wraps all the relevant statistics.
        :rtype: AniwatchStats
        """
        data = {"controller": "XML", "action": "getStatsData"}
        return AniwatchStats(self.network.post(data))

    def get_user_overview(self, user_id):
        """Gets a brief user overview which includes stats like total hours watched,
        total number of animes completed etc. 
        :param user_id: The id of the target user
        :type user_id: int, str
        :return: An UserOverview object that wraps all the relevant details 
                 regarding the given user. 
        :rtype: UserOverview
        """
        data = {
            "controller": "Profile",
            "action": "getOverview",
            "profile_id": str(user_id),
        }
        return UserOverview(self.network.post(data)["overview"])

    def get_user_chronicle(self, user_id, page=1):
        """Gets the user's chronicle. A chronicle tracks a user's watch history.
        :param user_id: The id of the target user
        :type user_id: int, str
        :param page: The page number of the chronicle that you 
                     want, defaults to 1
        :type page: int, optional
        :return: A list of ChronicleEntry objects, each object wraps all the 
                 information related to an entry like episode number, date, anime ID.
        :rtype: list[ChronicleEntry]
        """
        data = {
            "controller": "Profile",
            "action": "getChronicle",
            "profile_id": str(user_id),
            "page": page,
        }
        return [
            ChronicleEntry(data_dict, self.network, self.API_URL) for data_dict in self.network.post(data)["chronicle"]
        ]

    def get_user_anime_list(self):
        """Gets the user's aniwatch.me anime list. This list includes animes 
        that are marked by the user. 

        :return: A list of UserAnimeListEntry objects. An UserAnimeListEntry objects
                 contains information like the status, progress and total episodes etc.
        :rtype: list[UserAnimeListEntry]
        """
        data = {
            "controller": "Profile",
            "action": "getAnimelist",
            "profile_id": str(self.userId),
        }
        return [
            UserAnimeListEntry(data_dict, self.network)
            for data_dict in self.network.post(data)["animelist"]
        ]

    def get_user_media(self, page=1):
        """Gets the users favorite media.

        :param page: The page number of the favorites page that you want, defaults to 1
        :type page: int, optional
        :return: A list of UserMedia objects. A UserMedia object has data like title and 
                 media ID
        :rtype: list[UserMedia]
        """
        data = {
            "controller": "Profile",
            "action": "getMedia",
            "profile_id": str(self.userId),
            "page": page,
        }
        return [UserMedia(data_dict, self.network, self.API_URL) for data_dict in self.network.post(data)["entries"]]

    def send_image_to_discord(self, episode_id, base64_image, episode_time):
        data = {
            "controller": "Profile",
            "action": "sendToDiscord",
            "file": base64_image,
            "episode_id": int(episode_id),
            "time": episode_time,
            "lang": "en-US",
        }
        return self.network.post(data)

    def get_friends(self, page=1):
        data = {"controller": "Profile", "action": "getFriends", "page": page}
        resp = self.network.post(data)
        return [Friend(self.network, x) for x in resp["friends"]]

    def get_outgoing_requests(self, page=1):
        data = {"controller": "Profile", "action": "getFriends", "page": page}
        resp = self.network.post(data)
        return [FriendRequestOutgoing(self.network, x) for x in resp["outgoing"]]

    def get_friend_requests(self, page=1):
        data = {"controller": "Profile", "action": "getFriends", "page": page}
        resp = self.network.post(data)
        return [FriendRequestIncoming(self.network, x) for x in resp["incoming"]]

    def add_friend(self, friend_user_id):
        data = {
            "controller": "Profile",
            "action": "addFriend",
            "profile_id": friend_user_id,
        }
        self.network.post(data)
        return self.get_outgoing_requests()[-1]

    def remove_friend(self, friend_id):
        data = {
            "controller": "Profile",
            "action": "removeFriend",
            "friend_id": friend_id,
        }
        return self.network.post(data)

    def withdraw_friend_request(self, friend_id):
        data = {
            "controller": "Profile",
            "action": "withdrawRequest",
            "friend_id": friend_id,
        }
        return self.network.post(data)

    def accept_friend_request(self, friend_id):
        data = {
            "controller": "Profile",
            "action": "acceptRequest",
            "friend_id": friend_id,
        }
        return self.network.post(data)

    def reject_friend_request(self, friend_id):
        data = {
            "controller": "Profile",
            "action": "rejectRequest",
            "friend_id": friend_id,
        }
        return self.network.post(data)

    def get_user_settings(self):
        data = {"controller": "Profile", "action": "getSettings"}
        return self.network.post(data)

    def get_notifications(self):
        """Gets the user's unread notifications. 

        :return: A list of Notification objects. A Notificaton object contains 
                 data like date, notification ID and the content etc.
        :rtype: list[Notification]
        """
        data = {"controller": "Profile", "action": "getNotifications"}
        return [
            Notification(data_dict, self.network)
            for data_dict in self.network.post(data)["notifications"]
        ]

    def mark_all_notifications_as_read(self):
        """Marks all notification as read.

        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Profile",
            "action": "markAllNotificationsAsRead",
            "view": 0,
        }
        return self.network.post(data)

    def delete_all_notifications(self):
        """Deletes all notifications.

        :return: [description]
        :rtype: [type]
        """
        data = {"controller": "Profile", "action": "deleteAllNotifications", "view": 0}
        return self.network.post(data)

    def toggle_notification_seen(self, notification_id: int):
        """Toggles the mark as seen status of a notification.

        :param notification_id: The ID of the notification whose status you want to 
                                toggle.
        :type notification_id: int
        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Profile",
            "action": "toggleNotificationSeen",
            "id": notification_id,
        }
        return self.network.post(data)

    def delete_notification(self, notification_id: int):
        """Deletes a specific notification.

        :param notification_id: The ID of the notification you want to delete.
        :type notification_id: int
        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Profile",
            "action": "deleteNotification",
            "id": notification_id,
        }
        return self.network.post(data)

    def get_anime_chronicle(self, anime_id: int, page=1):
        """
        Gets the user's anime specific chronicle.

        :param anime_id: The ID of the anime whose chronicle you want.
        :type anime_id: int
        :param page: The page number of the chronicle that you want, defaults to 1
        :type page: int, optional
        :return: A list of ChronicleEntry objects.
        :rtype: list[ChronicleEntry]
        """
        data = {
            "controller": "Profile",
            "action": "getChronicle",
            "detail_id": str(anime_id),
            "page": page,
        }
        return [
            ChronicleEntry(data_dict, self.network, self.API_URL) for data_dict in self.network.post(data)["chronicle"]
        ]

    def remove_chronicle_entry(self, chronicle_id: int):
        """Removes a specific chronicle entry. 

        :param chronicle_id: The ID of the chronicle that you want to remove.
        :type chronicle_id: int
        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Profile",
            "action": "removeChronicleEntry",
            "chronicle_id": chronicle_id,
        }
        return self.network.post(data)

    def get_discord_hash(self):
        data = {"controller": "Profile", "action": "getDiscordHash"}
        return self.network.post(data)

    def renew_discord_hash(self):
        data = {"controller": "Profile", "action": "renewDiscordHash"}
        return self.network.post(data)

    def remove_discord_verification(self):
        data = {"controller": "Profile", "action": "removeDiscordVerification"}
        return self.network.post(data)

    def get_unread_notifications(self):
        """Gets a user's unread notifications.

        :return: A list of Notification objects.
        :rtype: list[Notification]
        """
        data = {"controller": "Profile", "action": "getUnreadNotifications"}
        return [
            Notification(data_dict, self.network)
            for data_dict in self.network.post(data)["notifications"]
        ]

    def toggle_mark_as_watched(self, anime_id: int, episode_id: int):
        """Toggles the mark as watched status of a particular episode of an anime.

        :param anime_id: The ID of the anime to which the episode belongs.
        :type anime_id: int
        :param episode_id: The ID of the episode that you want to toggle the status for.
        :type episode_id: int
        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Profile",
            "action": "markAsWatched",
            "detail_id": str(anime_id),
            "episode_id": episode_id,
        }
        return self.network.post(data)

    def mark_as_completed(self, anime_id: int):
        """Marks an anime as completed.

        :param anime_id: The ID of the anime that you want to mark as "complete".
        :type anime_id: int
        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Profile",
            "action": "markAsCompleted",
            "detail_id": str(anime_id),
        }
        return self.network.post(data)

    def mark_as_plan_to_watch(self, anime_id: int):
        """Marks an anime as plan to watch.

        :param anime_id: The ID of the anime that you want to mark as "plan to watch".
        :type anime_id: int
        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Profile",
            "action": "markAsPlannedToWatch",
            "detail_id": str(anime_id),
        }
        return self.network.post(data)

    def mark_as_on_hold(self, anime_id: int):
        """Marks an anime as "on hold"

        :param anime_id: The ID of the anime that you want to mark as "on hold".
        :type anime_id: int
        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Profile",
            "action": "markAsOnHold",
            "detail_id": str(anime_id),
        }
        return self.network.post(data)

    def mark_as_dropped(self, anime_id: int):
        """Marks an anime as "dropped"

        :param anime_id: The ID of the anime that you want to mark as dropped.
        :type anime_id: int
        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Profile",
            "action": "markAsDropped",
            "detail_id": str(anime_id),
        }
        return self.network.post(data)

    def mark_as_watching(self, anime_id: int):
        """Marks an anime as "watching"

        :param anime_id: The ID of the anime that you want to mark as watching.
        :type anime_id: int
        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Profile",
            "action": "markAsWatching",
            "detail_id": str(anime_id),
        }
        return self.network.post(data)

    def remove_from_list(self, anime_id: int):
        """Removes an anime from the user's anime list.

        :param anime_id: The ID of the anime that you want to remove from the list.
        :type anime_id: int
        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Profile",
            "action": "removeAnime",
            "detail_id": str(anime_id),
        }
        return self.network.post(data)

    def favorite_media(self, media_id: int):
        """Marks a media as favorite. 

        :param media_id: The ID of the media that you want to marks as favorite.
        :type media_id: int
        :return: [description]
        :rtype: [type]
        """
        data = {"controller": "Media", "action": "favMedia", "media_id": str(media_id)}
        return self.network.post(data)

    def rateAnime(self, anime_id: int, rating: int):
        """Sets the user's rating for a given anime. Rate an anime zero inorder to 
        remove the user's rating.

        :param anime_id: The ID of the anime that you want to rate.
        :type anime_id: int 
        :param rating: The number of stars that you want to the rate the given anime.
        :type rating: int
        :return: [description]
        :rtype: [type]
        """
        # Rate 0 to remove rating
        data = {
            "controller": "Profile",
            "action": "rateAnime",
            "detail_id": str(anime_id),
            "rating": rating,
        }
        return self.network.post(data)

    def get_reports(self):
        data = {"controller": "Profile", "action": "getReports"}
        return self.network.post(data)

    def report_missing_anime(self, anime_name: str):
        """Reports a missing anime.

        :param anime_name: The name of the anime that you want to report. 
        :type anime_name: str
        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Anime",
            "action": "reportMissingAnime",
            "anime_name": str(anime_name),
        }
        return self.network.post(data)

    def report_missing_streams(self, anime_id: int):
        """Reports a missing stream.

        :param anime_id: The ID of the anime whose strean you want to report as missing.
        :type anime_id: int
        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Anime",
            "action": "reportMissingStreams",
            "detail_id": str(anime_id),
        }
        return self.network.post(data)

    def get_watchlist(self, page=1):
        """Gets the user's current watchlist.

        :param page: The page number of the watchlist that you want to get, defaults to 1
        :type page: int, optional
        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Anime",
            "action": "getWatchlist",
            "detail_id": 0,
            "page": page,
        }
        return [
            WatchListEntry(data_dict, self.network, self.API_URL) for data_dict in self.network.post(data)["entries"]
        ]

    def login(self, username, password):
        data = {
            "username": username,
            "password": base64.b64encode(bytes(password, "utf8")).decode("utf8"),
            "code": "",
            "controller": "Authentication",
            "action": "doLogin",
        }
        return self.network.post(data)

    def forgot_password(self, email):
        data = {
            "controller": "Authentication",
            "action": "doForgotPW",
            "email": base64.b64encode(bytes(email, "utf8")).decode("utf8"),
        }
        return self.network.post(data)

    def search(self, query: str):
        """Searches the aniwatch.me library for the given anime title.

        :param query: The title of the anime that you want to search. Aniwatch also 
                      stores synonyms, english names for animes so those can be used too.
        :type query: str
        :return: A list of Anime objects.
        :rtype: [type]
        """
        data = {
            "controller": "Search",
            "action": "search",
            "rOrder": False,
            "order": "title",
            "typed": str(query),
            "genre": "[]",
            "staff": "[]",
            "tags": [],
            "langs": [],
            "anyGenre": False,
            "anyStaff": False,
            "anyTag": False,
            "animelist": [2],
            "types": [0],
            "status": [0],
            "yearRange": [1965, 2022],
            "maxEpisodes": 0,
            "hasRelation": False,
        }
        return [Anime(data_dict, self.network, self.API_URL) for data_dict in self.network.post(data)]

    def get_media(self, anime_id: int):
        """Gets an anime's media.

        :param anime_id: The ID of the anime whose media you want.
        :type anime_id: int
        :return: A Media object. A Media object has properties like opennings, endings, OSTs etc
                 that each contain a list of MediaEntry objects representing the respective media. 
        :rtype: Media
        """
        data = {"controller": "Media", "action": "getMedia", "detail_id": str(anime_id)}
        return Media(self.network.post(data), self.network, anime_id)
