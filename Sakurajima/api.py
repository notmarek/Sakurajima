import requests
import json
import base64
import random

class Sakurajima:

    def __init__(self, username=None, password=None, endpoint="https://aniwatch.me/api/ajax/APIHandle"):
        xsrf_token = self.__generate_xsrf_token()
        self.headers = { 'X-XSRF-TOKEN': xsrf_token }
        self.cookies = { 'XSRF-TOKEN': xsrf_token }
        self.API_URL = endpoint
        if username is not None and password is not None:
            login_response = self.login(username, password)
            self.headers['X-AUTH'] = login_response['auth']
            self.cookies["SESSION"] = '{"userid":' + str(login_response['user']['userid']) + ',"username":"' + str(login_response['user']['username']) + '","usergroup":4,"player_lang":1,"player_quality":0,"player_time_left_side":2,"player_time_right_side":3,"screen_orientation":1,"nsfw":1,"chrLogging":1,"mask_episode_info":0,"blur_thumbnails":0,"autoplay":1,"preview_thumbnails":1,"update_watchlist":1,"playheads":1,"seek_time":5,"cover":null,"title":"Member","premium":1,"lang":"en-US","auth":"' + str(login_response['auth']) + '","remember_login":true}'

    def __generate_xsrf_token(self):
        characters = ['a','b','c','d','e','f','0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
        return ''.join(random.choice(characters) for i in range(32))

    def __post(self, data):
        with requests.post(self.API_URL, headers=self.headers, json=data, cookies=self.cookies) as url:
            return json.loads(url.text)

    def get_episode(self, episode_id, lang='en-US'):
        data = { "controller": "Anime", "action": "watchAnime", "lang": lang, "ep_id": episode_id, "hoster": "" }
        return self.__post(data)

    def get_episodes(self, anime_id):
        data = { "controller": "Anime", "action": "getEpisodes", "detail_id": str(anime_id) }
        return self.__post(data)
    
    def get_anime(self, anime_id):
        data = { "controller": "Anime", "action": "getAnime", "detail_id": str(anime_id) }
        return self.__post(data)
    
    def get_recommendations(self, anime_id):
        data = { "controller": "Anime", "action": "getRecommendations", "detail_id": str(anime_id) }
        return self.__post(data)

    def get_relation(self, relation_id):
        data = { "controller": "Relation", "action": "getRelation", "relation_id": relation_id }
        return self.__post(data)

    def get_seasonal_anime(self, index="null", year="null"):
        data = { "controller": "Anime", "action": "getSeasonalAnime", "current_index": index, "current_year": year }
        return self.__post(data)
    
    def get_latest_releases(self):
        data = { "controller": "Anime", "action": "getLatestReleases" }
        return self.__post(data)

    def get_latest_uploads(self):
        data = { "controller": "Anime", "action": "getLatestUploads" }
        return self.__post(data)

    def get_latest_anime(self):
        data = { "controller": "Anime", "action": "getLatestAnime" }
        return self.__post(data)
    
    def get_random_anime(self):
        data = { "controller": "Anime", "action": "getRandomAnime" }
        return self.__post(data)

    def get_airing_anime(self, randomize=False):
        data = { "controller": "Anime", "action": "getAiringAnime", "randomize": randomize }
        return self.__post(data)
    
    def get_popular_anime(self, page=1):
        data = { "controller": "Anime", "action": "getPopularAnime", "page": page }
        return self.__post(data)
    
    def get_popular_seasonal_anime(self, page=1):
        data = { "controller": "Anime", "action": "getPopularSeasonals", "page": page }
        return self.__post(data)

    def get_popular_upcoming_anime(self, page=1):
        data = { "controller": "Anime", "action": "getPopularUpcomings", "page": page }
        return self.__post(data)

    def get_hot_anime(self, page=1):
        data = { "controller": "Anime", "action": "getHotAnime", "page": page }
        return self.__post(data)

    def get_best_rated_anime(self, page=1):
        data = { "controller": "Anime", "action": "getBestRatedAnime", "page": page }
        return self.__post(data)

    def add_recommendation(self, anime_id, recommended_anime_id):
        data = { "controller": "Anime", "action": "addRecommendation", "detail_id": str(anime_id), "recommendation": str(recommended_anime_id) }
        return self.__post(data)

    def get_stats(self):
        data = { "controller": "XML", "action": "getStatsData" }
        return self.__post(data)

    def get_user_overview(self, user_id):
        data = { "controller": "Profile", "action": "getOverview", "profile_id": str(user_id) }
        return self.__post(data)
    
    def get_user_chronicle(self, user_id, page=1):
        data = { "controller": "Profile", "action": "getChronicle", "profile_id": str(user_id), "page": page }
        return self.__post(data)

    def get_user_anime_list(self, user_id):
        data = { "controller": "Profile", "action": "getAnimelist", "profile_id": str(user_id) }
        return self.__post(data)

    def get_user_media(self, user_id, page=1):
        data = { "controller": "Profile", "action": "getMedia", "profile_id": str(user_id), "page": page }
        return self.__post(data)
    
    def get_user_friends(self, page=1):
        data = { "controller": "Profile", "action": "getFriends", "page": page }
        return self.__post(data)
    
    def add_friend(self, friend_user_id):
        data = { "controller": "Profile", "action": "addFriend", "profile_id": friend_user_id }
        return self.__post(data)
    
    def remove_friend(self, friend_id):
        data = { "controller": "Profile", "action": "removeFriend", "friend_id": friend_id }
        return self.__post(data)

    def withdraw_friend_request(self, friend_id):
        data = { "controller": "Profile", "action": "withdrawRequest", "friend_id": friend_id }
        return self.__post(data)

    def accept_friend_request(self, friend_id):
        data = { "controller": "Profile", "action": "acceptRequest", "friend_id": friend_id }
        return self.__post(data)

    def reject_friend_request(self, friend_id):
        data = { "controller": "Profile", "action": "rejectRequest", "friend_id": friend_id }
        return self.__post(data)

    def get_user_settings(self):
        data = { "controller": "Profile", "action": "getSettings" }
        return self.__post(data)

    def get_notifications(self):
        data = { "controller": "Profile", "action": "getNotifications" }
        return self.__post(data)

    def mark_all_notifications_as_read(self):
        data = { "controller": "Profile", "action": "markAllNotificationsAsRead", "view": 0 }
        return self.__post(data)

    def delete_all_notifications(self):
        data = { "controller": "Profile", "action": "deleteAllNotifications", "view": 0 }
        return self.__post(data)
        
    def toggle_notification_seen(self, notification_id):
        data = { "controller": "Profile", "action": "toggleNotificationSeen", "id": notification_id }
        return self.__post(data)        

    def delete_notification(self, notification_id):
        data = { "controller": "Profile", "action": "deleteNotification", "id": notification_id }
        return self.__post(data)

    def get_anime_chronicle(self, anime_id, page=1):
        data = { "controller": "Profile", "action": "getChronicle", "detail_id": str(anime_id), "page": page }
        return self.__post(data)

    def remove_chronicle_entry(self, chronicle_id):
        data = { "controller": "Profile", "action": "removeChronicleEntry", "chronicle_id": chronicle_id }
        return self.__post(data)
    
    def get_discord_hash(self):
        data = { "controller": "Profile", "action": "getDiscordHash" }
        return self.__post(data)
    
    def renew_discord_hash(self):
        data = { "controller": "Profile", "action": "renewDiscordHash" }
        return self.__post(data)
    
    def remove_discord_verification(self):
        data = { "controller": "Profile", "action": "removeDiscordVerification" }
        return self.__post(data)

    def get_unread_notifications(self):
        data = { "controller": "Profile", "action": "getUnreadNotifications" }
        return self.__post(data)
    
    def mark_as_watched(self, anime_id, episode_id):
        data = { "controller": "Profile", "action": "markAsWatched", "detail_id": str(anime_id), "episode_id": episode_id }
        return self.__post(data)

    def mark_as_completed(self, anime_id):
        data = { "controller": "Profile", "action": "markAsCompleted", "detail_id": str(anime_id) }
        return self.__post(data)

    def mark_as_plan_to_watch(self, anime_id):
        data = { "controller": "Profile", "action": "markAsPlannedToWatch", "detail_id": str(anime_id) }
        return self.__post(data)

    def mark_as_on_hold(self, anime_id):
        data = { "controller": "Profile", "action": "markAsOnHold", "detail_id": str(anime_id) }
        return self.__post(data)

    def mark_as_dropped(self, anime_id):
        data = { "controller": "Profile", "action": "markAsDropped", "detail_id": str(anime_id) }
        return self.__post(data)

    def mark_as_watching(self, anime_id):
        data = { "controller": "Profile", "action": "markAsWatching", "detail_id": str(anime_id) }
        return self.__post(data)

    def remove_from_list(self, anime_id):
        data = { "controller": "Profile", "action": "removeAnime", "detail_id": str(anime_id) }
        return self.__post(data)

    def favorite_media(self, media_id):
        data = { "controller": "Media", "action": "favMedia", "media_id": str(media_id) }
        return self.__post(data)

    def rateAnime(self, anime_id, rating):
        # Rate 0 to remove rating
        data = { "controller": "Profile", "action": "rateAnime", "detail_id": str(anime_id), "rating": rating }
        return self.__post(data)

    def get_reports(self):
        data = { "controller": "Profile", "action": "getReports" }
        return self.__post(data)

    def report_missing_anime(self, anime_name):
        data = { "controller": "Anime", "action": "reportMissingAnime", "anime_name": str(anime_name) }
        return self.__post(data)
    
    def report_missing_streams(self, anime_id):
        data = { "controller": "Anime", "action": "reportMissingStreams", "detail_id": str(anime_id) }
        return self.__post(data)

    def get_watchlist(self, page=1):
        data = { "controller": "Anime", "action": "getWatchlist", "detail_id": 0, "page": page }
        return self.__post(data)
    
    def login(self, username, password):
        data = { "username": username, "password": base64.b64encode(bytes(password, 'utf8')).decode('utf8'), "code": "", "controller": "Authentication", "action":"doLogin" }
        return self.__post(data)

    def forgot_password(self, email):
        data = { "controller": "Authentication", "action": 'doForgotPW', "email": base64.b64encode(bytes(email, 'utf8')).decode('utf8') }
        return self.__post(data)

    def search(self, query):
        data = { "controller": "Search", "action": "search", "rOrder": False, "order": "title", "typed": str(query), "genre": "[]", "staff": "[]", "tags": [], "langs": [], "anyGenre": False, "anyStaff": False, "anyTag": False, "animelist": [2], "types": [0], "status": [0], "yearRange": [1965,2022], "maxEpisodes": 0, "hasRelation": False }
        return self.__post(data)

    def get_media(self, anime_id):
        data = { "controller": "Media", "action": "getMedia", "detail_id": str(anime_id) }
        return self.__post(data)
