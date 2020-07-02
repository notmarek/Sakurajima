from datetime import datetime
import requests
import json 
from m3u8 import M3U8
from Crypto.Cipher import AES

class Anime(object):
    '''Wraps all the relevant data for an anime like anime_id 
    (called as detail_id by AniWatch backend), title, airing date etc.
    Use the get_episodes method to get a list of available episodes'''
    def __init__(self, data_dict: dict, headers: dict, cookies: dict, api_url: str):
        self.headers = headers
        self.cookies = cookies
        self.API_URL = api_url
        self.data_dict = data_dict
        self.anime_id =  data_dict.get('detail_id', None)
        self.airing_start =  data_dict.get('airing_start', None)
        self.airing_end =  data_dict.get('airing_end', None)
        self.start_index =  data_dict.get('start_index', None)
        self.end_index =  data_dict.get('end_index', None)
        self.airing_start_unknown =  data_dict.get('airing_start_unknown', None)
        self.airing_end_unknown = data_dict.get('airing_end_unknown', None)
        self.relation_id =  data_dict.get('relation_id', None)
        self.genre =  data_dict.get('genre', None)
        self.staff =  data_dict.get('staff', None)
        self.tags =  data_dict.get('tags', None)
        self.title =  data_dict.get('title', None)
        self.description =  data_dict.get('description', None)
        self.cover = data_dict.get('cover', None)
        self.episode_max = data_dict.get('episode_max', None) 
        self.type = data_dict.get('type', None) 
        try:
            self.broadcast_start = datetime.utcfromtimestamp(data_dict.get('broadcast_start'))
        except:
            self.broadcast_start = None
        try:
            self.launch_day = datetime.utcfromtimestamp(data_dict.get('launch_day'))
        except:
            self.launch_day = None
        self.status = data_dict.get('status', None)
        self.synonyms = data_dict.get('synonyms', None)
        self.broadcast_time = data_dict.get('broadcast_time', None)
        self.launch_offset = data_dict.get('launch_offset', None)
        self.has_nudity = data_dict.get('hasNudity', None)
        self.cur_episodes = data_dict.get('cur_episodes', None)
        self.is_on_anime_list = data_dict.get('isOnAnimeList', None)
        self.planned_to_watch = data_dict.get('planned_to_watch', None)
        self.completed = data_dict.get('completed', None)
        self.watching = data_dict.get('watching', None)
        self.progress = data_dict.get('progress', None)
        self.dropped = data_dict.get('dropped', None)
        self.on_hold = data_dict.get('on_hold', None)
        self.rating = data_dict.get('rating', None)
        self.members_counter = data_dict.get('member_counters', None)
        self.members_counter_rank = data_dict.get('members_counter_rank', None)
        self.score = data_dict.get('score', None)
        self.score_count = data_dict.get('score_count', None)
        self.score_rank = data_dict.get('score_rank', None)
        self.__episodes = None
        
    def get_episodes(self):
        data = { "controller": "Anime", "action": "getEpisodes", "detail_id": str(self.anime_id) }
        if self.__episodes:
            return self.__episodes
        else:
            self.__episodes = [Episode(data_dict, cookies = self.cookies, headers = self.headers, anime_id = self.anime_id, api_url = self.API_URL) for data_dict in self.__post(data)['episodes']]
            return self.__episodes

    def __post(self, data):
        with requests.post(self.API_URL, headers=self.headers, json=data, cookies=self.cookies) as url:
            return json.loads(url.text)

    def __repr__(self):
        return f'<Anime : {self.title}>'

    def get_relations(self):
        data = { "controller": "Relation", "action": "getRelation", "relation_id": self.relation_id }
        return Relation(self.__post(data)['relation'])

    def mark_as_completed(self):
        data = { "controller": "Profile", "action": "markAsCompleted", "detail_id": str(self.anime_id) }
        return self.__post(data)['success']
    
    def mark_as_plan_to_watch(self):
        data = { "controller": "Profile", "action": "markAsPlannedToWatch", "detail_id": str(self.anime_id) }
        return self.__post(data)['success']
    
    def mark_as_on_hold(self):
        data = { "controller": "Profile", "action": "markAsOnHold", "detail_id": str(self.anime_id) }
        return self.__post(data)['success']
    
    def mark_as_dropped(self):
        data = { "controller": "Profile", "action": "markAsDropped", "detail_id": str(self.anime_id) }
        return self.__post(data)['success']
    
    def mark_as_watching(self):
        data = { "controller": "Profile", "action": "markAsWatching", "detail_id": str(self.anime_id) }
        return self.__post(data)['success']

    def remove_from_list(self):
        data = { "controller": "Profile", "action": "removeAnime", "detail_id": str(self.anime_id) }
        return self.__post(data)['success']

    def rate(self, rating):
        # Rate 0 to remove rating
        data = { "controller": "Profile", "action": "rateAnime", "detail_id": str(self.anime_id), "rating": rating }
        return self.__post(data)['success']
    
    def get_media(self):
        data = { "controller": "Media", "action": "getMedia", "detail_id": str(self.anime_id) }
        return Media(self.__post(data), self.headers, self.cookies, self.API_URL, self.anime_id)
    
    def get_complete_object(self):
        data = { "controller": "Anime", "action": "getAnime", "detail_id": str(self.anime_id) }
        data_dict = self.__post(data)['anime']
        return Anime(data_dict, headers=self.headers, cookies = self.cookies, api_url=self.API_URL)
    
    def add_recommendation(self, recommended_anime_id):
        data = {
            "controller": "Anime",
            "action": "addRecommendation",
            "detail_id": str(self.anime_id),
            "recommendation": str(recommended_anime_id),
        }
        return self.__post(data)
    
    def get_dict(self):
        return self.data_dict

class Support(object):
    def __init__(self, data_dict):
        self.screenshot = data_dict.get('screenshot', None)
        self.download = data_dict.get('download', None)
        self.download_type = data_dict.get('download_type', None)

class Language(object):
    def __init__(self, data_dict):
        self.language = data_dict.get('str', None)
        self.id = data_dict.get('id', None)

class Stream(object):
    def __init__(self, data_dict):
        self.sources = data_dict.get('src', None)
        self.lang = data_dict.get('lang', None)
        self.no_streams = data_dict.get('no_streams', None)
        self.hoster = data_dict.get('hoster', None)
        self.hosters = data_dict.get('hosters', None)
        self.hosterkey = data_dict.get('hosterKey', None)
        self.support = Support(data_dict.get('support', None))
        self.sprites = data_dict.get('sprites', None)

class AniWatchEpisode(object):
    def __init__(self, data_dict, episode_id):
        self.episode_id = episode_id
        self.languages = [Language(lang) for lang in data_dict.get('lang', None)]
        self.stream = Stream(data_dict.get('stream', None))
        
    def __repr__(self):
        return f'Episode ID : {self.episode_id}'

class Episode(object):
    def __init__(self, data_dict, cookies, headers, anime_id, api_url):
        self.cookies = cookies
        self.headers = headers
        self.anime_id = anime_id
        self.API_URL = api_url
        self.number = data_dict.get('number', None)
        self.title = data_dict.get('title', None)
        self.description = data_dict.get('description', None)
        self.thumbnail = data_dict.get('thumbnail', None)
        self.added =  datetime.utcfromtimestamp(data_dict.get('added', None))
        self.filler = data_dict.get('filler', None)
        self.ep_id = data_dict.get('ep_id', None)
        self.duration = data_dict.get('duration', None)
        self.is_aired = data_dict.get('is_aired', None)
        self.lang = data_dict.get('lang', None)
        self.watched = data_dict.get('watched', None)

    def __post(self, data):
        with requests.post(self.API_URL, headers=self.headers, json=data, cookies=self.cookies) as url:
            return json.loads(url.text)    
    
    def __generate_referer(self):
        return f'https://aniwatch.me/anime/{self.anime_id}/{self.number}'
    
    def __get_decrypt_key(self, url, headers, cookies):
        res = requests.get(url, cookies = cookies, headers = headers)
        return res.content

    def __decrypt_chunk(self, chunk, key):
        decrytor = AES.new(key,AES.MODE_CBC)
        return decrytor.decrypt(chunk)

    def get_aniwatch_episode(self, lang = 'en-US'):
        data = { "controller": "Anime", "action": "watchAnime", "lang": lang, "ep_id": self.ep_id, "hoster": "" }
        return AniWatchEpisode(self.__post(data), self.ep_id)
    
    def get_m3u8(self, quality: str):
        REFERER = self.__generate_referer()
        HEADERS = self.headers
        HEADERS.update({'REFERER' : REFERER, 'ORIGIN' : 'https://aniwatch.me'})
        aniwatch_episode = self.get_aniwatch_episode()
        res = requests.get(aniwatch_episode.stream.sources[quality], headers = HEADERS, cookies = self.cookies)
        return M3U8(res.text)

    def download(self, quality: str, file_name = 'download'):
        m3u8 = self.get_m3u8(quality)
        REFERER = self.__generate_referer()
        HEADERS = self.headers
        HEADERS.update({'REFERER' : REFERER, 'ORIGIN' : 'https://aniwatch.me'})
        total_chunks = len(m3u8.data['segments'])
        chunks_done = 0
        with open(f'{file_name}.ts', 'wb') as videofile:
            for segment in m3u8.data['segments']:
                res = requests.get(segment['uri'], cookies = self.cookies, headers = HEADERS)
                chunk = res.content
                key_dict = segment.get('key', None)
                if key_dict is not None:
                    key = self.__get_decrypt_key(key_dict['uri'], HEADERS, self.cookies)
                    decrypted_chunk = self.__decrypt_chunk(chunk, key)
                    videofile.write(decrypted_chunk)
                    chunks_done = chunks_done + 1
                else:
                    videofile.write(chunk)
                    chunks_done = chunks_done + 1
                print(f'{chunks_done}/{total_chunks} done')

    def mark_as_watched(self):
        data = { "controller": "Profile", "action": "markAsWatched", "detail_id": str(self.anime_id), "episode_id": self.ep_id }
        return self.__post(data)['success']
    
    def __repr__(self):
        return f'<Episode {self.number} : {self.title}>'

class Notification(object):
    def __init__(self, data_dict, headers, cookies, api_url):
        self.headers = headers
        self.cookies = cookies
        self.API_URL = api_url
        self.data_dict = data_dict
        self.id = data_dict.get('id', None)
        self.type = data_dict.get('type', None)
        self.mode = data_dict.get('mode', None)
        self.content = data_dict.get('content', None)
        try:
            self.time = datetime.utcfromtimestamp(data_dict.get('time', None))
        except:
            self.time = data_dict.get('time', None)
        self.seen = data_dict.get('seen', None)
        self.href_blank = data_dict.get('href_blank', None)
        self.href = data_dict.get('href', None)

    def __post(self, data):
        with requests.post(self.API_URL, headers=self.headers, json=data, cookies=self.cookies) as url:
            return json.loads(url.text)

    def get_dict(self):
        return self.data_dict

    def toggle_seen(self):
        data = { "controller": "Profile", "action": "toggleNotificationSeen", "id": self.id }
        return self.__post(data)['success']  

    def delete(self):
        data = { "controller": "Profile", "action": "deleteNotification", "id": self.id }
        return self.__post(data)['success']

    def __repr__(self):
        return f'<Notification ID : {self.id}, Date : {self.time}>'

class RelationEntry(object):
    def __init__(self, data_dict):
        self.title = data_dict.get('title', None)
        self.episodes_max = data_dict.get('episodes_max', None)
        self.type = data_dict.get('type', None)
        self.cover = data_dict.get('cover', None)
        self.anime_id = data_dict.get('detail_id', None)
        self.airing_start = data_dict.get('airing_start', None)
        self.d_status = data_dict.get('d_status', None)
        self.has_nudity = data_dict.get('hasNudity', None)
        self.progress = data_dict.get('progress', None)
        self.cur_episodes = data_dict.get('cur_episodes', None)
        self.completed = data_dict.get('completed', None)

    def __repr__(self):
        return f'<Relation Entry {self.title}>'

class Relation(object):
    def __init__(self, data_dict):
        self.relation_id = data_dict.get('relation_id', None)
        self.title = data_dict.get('title', None)
        self.description = data_dict.get('description')
        self.entries = [RelationEntry(data) for data in data_dict['entries']]
    
    def __repr__(self):
        return f'<Relation {self.title}>'

class WatchListEntry(object):
    def __init__(self, data_dict, headers, cookies, api_url):
        self.headers = headers
        self.cookies = cookies
        self.API_URL = api_url
        self.title = data_dict.get('title', None)
        self.type = data_dict.get('type', None)
        self.anime_id = data_dict.get('detail_id', None)
        self.selPage = data_dict.get('selPage', None)
        self.pages = data_dict.get('pages', None)
        self.status = data_dict.get('status', None)
        self.progress = data_dict.get('progress', None)
        self.list_status = data_dict.get('list_status', None)
        self.max_episodes = data_dict.get('max_episodes', None)
        self.cover = data_dict.get('cover', None)
        self.available_episodes = data_dict.get('available_episodes', None)
        self.episodes = [Episode(data, self.cookies, self.headers, self.anime_id, self.API_URL) for data in data_dict.get('episodes', [])]

    def __repr__(self):
        return f'<WatchListEntry : {self.title}>'

class Media(object):
    '''Contains media entries for categories like openings, endings and OSTs'''
    def __init__(self, data_dict, headers, cookies, api_url, anime_id):
        self.headers = headers
        self.cookies = cookies 
        self.API_URL = api_url
        self.anime_id = anime_id
        self.theme_songs = [MediaEntry(data, self.headers, self.cookies, self.API_URL) for data in data_dict.get('Theme Songs', [])]
        self.openings = [MediaEntry(data, self.headers, self.cookies, self.API_URL) for data in data_dict.get('Openings', [])]
        self.endings = [MediaEntry(data, self.headers, self.cookies, self.API_URL) for data in data_dict.get('Endings', [])]
        self.osts = [MediaEntry(data, self.headers, self.cookies, self.API_URL) for data in data_dict.get('OSTs', [])]

    def __repr__(self):
        return f'<Media for Anime : {self.anime_id}>'

class MediaEntry(object):
    '''Represents a single media entry and contains all the relevant data related
    to the entry like media_id and favorite status.'''
    def __init__(self, data_dict, headers, cookies, api_url):
        self.headers = headers
        self.cookies = cookies
        self.API_URL = api_url
        self.title = data_dict.get('media_title', None)
        self.type = data_dict.get('media_type', None)
        self.value = data_dict.get('media_value', None)
        self.favorites = data_dict.get('media_favorites', None)
        self.is_favorited = data_dict.get('media_hasFaved', None)
        self.id = data_dict.get('media_id', None)
        self.occurence = data_dict.get('media_occurence', None)
        self.thumbnail = data_dict.get('media_thumb', None)

    def __post(self, data):
        with requests.post(self.API_URL, headers=self.headers, json=data, cookies=self.cookies) as url:
            return json.loads(url.text)    

    def __repr__(self):
        return f'<Media Entry {self.title}>'

    def favorite_media(self):
        '''Marks the media as a favotite'''
        data = { "controller": "Media", "action": "favMedia", "media_id": str(self.id) }
        return self.__post(data)['success'] 

class UserAnimeListEntry(object):
    def __init__(self, data_dict, headers, cookies, api_url):
        self.headers = headers
        self.cookies = cookies
        self.API_URL = api_url
        self.title = data_dict.get('title', None)
        self.episodes_max = data_dict.get('episodes_max', None)
        self.type = data_dict.get('type', None)
        self.cover = data_dict.get('cover', None)
        self.anime_id = data_dict.get('details_id', None)
        self.progress = data_dict.get('progress', None)
        self.airing_start = data_dict.get('airing_start', None)
        self.cur_episodes = data_dict.get('cur_episodes', None)
        if data_dict.get('completed', None) == 1:
            self.status = 'completed' 
        elif data_dict.get('planned_to_watch', None) == 1:
            self.status = 'planned_to_watch'
        elif data_dict.get('on_hold', None) == 1:
            self.status = 'on_hold'
        elif data_dict.get('dropped', None) == 1:
            self.status = 'dropped'

    def __post(self, data):
        with requests.post(self.API_URL, headers=self.headers, json=data, cookies=self.cookies) as url:
            return json.loads(url.text)

    def get_anime(self):
        data = {"controller": "Anime", "action": "getAnime", "detail_id": str(self.anime_id)}
        return Anime(self.__post(data)['anime'], headers=self.headers, cookies = self.cookies, api_url=self.API_URL)

    def __repr__(self):
            return f'<AnimeListEntry : {self.title}>'

class UserOverview(object):
    def __init__(self, data_dict):
        self.anime = UserOverviewType(data_dict['anime'])
        self.special = UserOverviewType(data_dict['special'])
        self.movie = UserOverviewType(data_dict['movie'])
        self.hentai = UserOverviewType(data_dict['hentai'])
        self.stats = UserOverviewStats(data_dict['stats'])
        self.mine =data_dict.get('mine', None)
        self.username = data_dict.get('username', None)
        self.title = data_dict.get('title', None)
        self.admin = data_dict.get('admin', None)
        self.staff = data_dict.get('staff', None)
        self.cover = data_dict.get('cover', None)
        self.friend = data_dict.get('friend', None)

    def __repr__(self):
        return f'<UserOverView: {self.username}>'

class UserOverviewType(object):
    def __init__(self, data_dict):
        self.total = data_dict.get('total', None)
        self.episodes = data_dict.get('episodes', None)
        self.icon = data_dict.get('icon', None)

class UserOverviewStats(object):
    def __init__(self, data_dict):
        self.total = data_dict.get('total', None)
        self.total_episodes = data_dict.get('total_episodes', None)
        self.watched_hours = data_dict.get('watched_hours', None)
        self.watched_days = data_dict.get('watched_days', None)
        self.mean_score = data_dict.get('mean_score', None)
        self.ratings = data_dict.get('ratings', None)