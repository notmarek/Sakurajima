from datetime import datetime
import requests
import json
from m3u8 import M3U8
from Crypto.Cipher import AES
from Sakurajima.models.relation import Relation
from Sakurajima.models.recommendation import RecommendationEntry
from Sakurajima.models.chronicle import ChronicleEntry
from Sakurajima.models.media import Media
from Sakurajima.models.helper_models import Language, Stream
from Sakurajima.utils.episode_list import EpisodeList
import subprocess
from time import sleep
from multiprocessing import Process
import os
import shutil


class Anime(object):
    """Wraps all the relevant data for an anime like anime_id
    (called as detail_id by AniWatch backend), title, airing date etc.
    Use the get_episodes method to get a list of available episodes"""

    def __init__(self, data_dict: dict, headers: dict, cookies: dict, api_url: str):
        self.__headers = headers
        self.__cookies = cookies
        self.__API_URL = api_url
        self.data_dict = data_dict
        self.anime_id = data_dict.get("detail_id", None)
        self.airing_start = data_dict.get("airing_start", None)
        self.airing_end = data_dict.get("airing_end", None)
        self.start_index = data_dict.get("start_index", None)
        self.end_index = data_dict.get("end_index", None)
        self.airing_start_unknown = data_dict.get("airing_start_unknown", None)
        self.airing_end_unknown = data_dict.get("airing_end_unknown", None)
        self.relation_id = data_dict.get("relation_id", None)
        self.genre = data_dict.get("genre", None)
        self.staff = data_dict.get("staff", None)
        self.tags = data_dict.get("tags", None)
        self.title = data_dict.get("title", None)
        self.description = data_dict.get("description", None)
        self.cover = data_dict.get("cover", None)
        self.episode_max = data_dict.get("episode_max", None)
        self.type = data_dict.get("type", None)
        try:
            self.broadcast_start = datetime.utcfromtimestamp(
                data_dict.get("broadcast_start")
            )
        except:
            self.broadcast_start = None
        try:
            self.launch_day = datetime.utcfromtimestamp(data_dict.get("launch_day"))
        except:
            self.launch_day = None
        self.status = data_dict.get("status", None)
        self.synonyms = data_dict.get("synonyms", None)
        self.broadcast_time = data_dict.get("broadcast_time", None)
        self.launch_offset = data_dict.get("launch_offset", None)
        self.has_nudity = data_dict.get("hasNudity", None)
        self.cur_episodes = data_dict.get("cur_episodes", None)
        self.is_on_anime_list = data_dict.get("isOnAnimeList", None)
        self.planned_to_watch = data_dict.get("planned_to_watch", None)
        self.completed = data_dict.get("completed", None)
        self.watching = data_dict.get("watching", None)
        self.progress = data_dict.get("progress", None)
        self.dropped = data_dict.get("dropped", None)
        self.on_hold = data_dict.get("on_hold", None)
        self.rating = data_dict.get("rating", None)
        self.members_counter = data_dict.get("member_counters", None)
        self.members_counter_rank = data_dict.get("members_counter_rank", None)
        self.score = data_dict.get("score", None)
        self.score_count = data_dict.get("score_count", None)
        self.score_rank = data_dict.get("score_rank", None)
        self.__episodes = None

    def get_episodes(self):
        data = {
            "controller": "Anime",
            "action": "getEpisodes",
            "detail_id": str(self.anime_id),
        }
        if self.__episodes:
            return self.__episodes
        else:
            self.__episodes = EpisodeList(
                [
                    Episode(
                        data_dict,
                        self.__headers,
                        self.__cookies,
                        self.__API_URL,
                        self.anime_id,
                        self.title,
                    )
                    for data_dict in self.__post(data)["episodes"]
                ]
            )
            return self.__episodes

    def __post(self, data):
        with requests.post(
            self.__API_URL, headers=self.__headers, json=data, cookies=self.__cookies
        ) as url:
            return json.loads(url.text)

    def __repr__(self):
        return f"<Anime: {self.title}>"

    def get_relations(self):
        data = {
            "controller": "Relation",
            "action": "getRelation",
            "relation_id": self.relation_id,
        }
        return Relation(self.__post(data)["relation"])

    def get_recommendations(self):
        data = {
            "controller": "Anime",
            "action": "getRecommendations",
            "detail_id": str(self.anime_id),
        }
        return [
            RecommendationEntry(
                data_dict, self.__headers, self.__cookies, self.__API_URL
            )
            for data_dict in self.__post(data)["entries"]
        ]

    def get_chronicle(self, page=1):
        data = {
            "controller": "Profile",
            "action": "getChronicle",
            "detail_id": str(self.anime_id),
            "page": page,
        }
        return [
            ChronicleEntry(data_dict, self.__headers, self.__cookies, self.__API_URL)
            for data_dict in self.__post(data)["chronicle"]
        ]

    def mark_as_completed(self):
        data = {
            "controller": "Profile",
            "action": "markAsCompleted",
            "detail_id": str(self.anime_id),
        }
        return self.__post(data)["success"]

    def mark_as_plan_to_watch(self):
        data = {
            "controller": "Profile",
            "action": "markAsPlannedToWatch",
            "detail_id": str(self.anime_id),
        }
        return self.__post(data)["success"]

    def mark_as_on_hold(self):
        data = {
            "controller": "Profile",
            "action": "markAsOnHold",
            "detail_id": str(self.anime_id),
        }
        return self.__post(data)["success"]

    def mark_as_dropped(self):
        data = {
            "controller": "Profile",
            "action": "markAsDropped",
            "detail_id": str(self.anime_id),
        }
        return self.__post(data)["success"]

    def mark_as_watching(self):
        data = {
            "controller": "Profile",
            "action": "markAsWatching",
            "detail_id": str(self.anime_id),
        }
        return self.__post(data)["success"]

    def remove_from_list(self):
        data = {
            "controller": "Profile",
            "action": "removeAnime",
            "detail_id": str(self.anime_id),
        }
        return self.__post(data)["success"]

    def rate(self, rating):
        # Rate 0 to remove rating
        data = {
            "controller": "Profile",
            "action": "rateAnime",
            "detail_id": str(self.anime_id),
            "rating": rating,
        }
        return self.__post(data)["success"]

    def get_media(self):
        data = {
            "controller": "Media",
            "action": "getMedia",
            "detail_id": str(self.anime_id),
        }
        return Media(
            self.__post(data),
            self.__headers,
            self.__cookies,
            self.__API_URL,
            self.anime_id,
        )

    def get_complete_object(self):
        data = {
            "controller": "Anime",
            "action": "getAnime",
            "detail_id": str(self.anime_id),
        }
        data_dict = self.__post(data)["anime"]
        return Anime(
            data_dict,
            headers=self.__headers,
            cookies=self.__cookies,
            api_url=self.__API_URL,
        )

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


class Episode(object):
    def __init__(
        self, data_dict, headers, cookies, api_url, anime_id, anime_title=None
    ):
        self.anime_title = anime_title
        self.__cookies = cookies
        self.__headers = headers
        self.anime_id = anime_id
        self.API_URL = api_url
        self.number = data_dict.get("number", None)
        self.title = data_dict.get("title", None)
        self.description = data_dict.get("description", None)
        self.thumbnail = data_dict.get("thumbnail", None)
        self.added = datetime.utcfromtimestamp(data_dict.get("added", None))
        self.filler = data_dict.get("filler", None)
        self.ep_id = data_dict.get("ep_id", None)
        self.duration = data_dict.get("duration", None)
        self.is_aired = data_dict.get("is_aired", None)
        self.lang = data_dict.get("lang", None)
        self.watched = data_dict.get("watched", None)
        self.__aniwatch_episode = None
        self.__m3u8 = None

    def __post(self, data):
        with requests.post(
            self.API_URL, headers=self.__headers, json=data, cookies=self.__cookies
        ) as url:
            return json.loads(url.text)

    def __generate_referer(self):
        return f"https://aniwatch.me/anime/{self.anime_id}/{self.number}"

    def __get_decrypt_key(self, url, headers, cookies):
        res = requests.get(url, cookies=cookies, headers=headers)
        return res.content

    def __decrypt_chunk(self, chunk, key):
        decrytor = AES.new(key, AES.MODE_CBC)
        return decrytor.decrypt(chunk)

    def get_aniwatch_episode(self, lang="en-US"):
        if self.__aniwatch_episode:
            return self.__aniwatch_episode
        else:
            data = {
                "controller": "Anime",
                "action": "watchAnime",
                "lang": lang,
                "ep_id": self.ep_id,
                "hoster": "",
            }
            self.__aniwatch_episode = AniWatchEpisode(self.__post(data), self.ep_id)
            return self.__aniwatch_episode

    def get_m3u8(self, quality: str):
        if self.__m3u8:
            return self.__m3u8
        else:
            REFERER = self.__generate_referer()
            HEADERS = self.__headers
            HEADERS.update({"REFERER": REFERER, "ORIGIN": "https://aniwatch.me"})
            aniwatch_episode = self.get_aniwatch_episode()
            res = requests.get(
                aniwatch_episode.stream.sources[quality],
                headers=HEADERS,
                cookies=self.__cookies,
            )
            self.__m3u8 = M3U8(res.text)
            return self.__m3u8

    def download_chunk(self, file_name, chunk_num, segment, headers):
        try:
            os.mkdir("chunks")
        except FileExistsError:
            pass
        with open(f"chunks\/{file_name}-{chunk_num}.chunk.ts", "wb") as videofile:
            res = requests.get(segment["uri"], cookies=self.__cookies, headers=headers)
            chunk = res.content
            key_dict = segment.get("key", None)
            if key_dict is not None:
                key = self.__get_decrypt_key(key_dict["uri"], headers, self.__cookies)
                decrypted_chunk = self.__decrypt_chunk(chunk, key)
                videofile.write(decrypted_chunk)
            else:
                videofile.write(chunk)

    def download(
        self,
        quality: str,
        file_name: str = None,
        multi_threading: bool = False,
        use_ffmpeg: bool = False,
        include_intro_chunk: bool = False,
        delete_chunks: bool = True,
        on_progress=None,
        print_progress: bool = True,
    ):
        if file_name is None:
            if self.anime_title is None:
                file_name = f"Download-{self.ep_id}"
            else:
                file_name = f"{self.anime_title[:128]}-{self.number}"  # limit anime title lenght to 128 chars so we don't surpass the filename limit
        m3u8 = self.get_m3u8(quality)
        REFERER = self.__generate_referer()
        HEADERS = self.__headers
        HEADERS.update({"REFERER": REFERER, "ORIGIN": "https://aniwatch.me"})
        chunks_done = 0
        threads = []
        cur_chunk = 0
        if not include_intro_chunk:
            for x in m3u8.data["segments"]:
                # Remove useless segments (intro)
                if "img.aniwatch.me" in x["uri"]:
                    m3u8.data["segments"].remove(x)
        total_chunks = len(m3u8.data["segments"])

        for segment in m3u8.data["segments"]:
            if not multi_threading:
                if on_progress:
                    on_progress.__call__(chunks_done, total_chunks)
                self.download_chunk(file_name, chunks_done, segment, HEADERS)
                chunks_done += 1
                if print_progress:
                    print(f"{chunks_done}/{total_chunks} done.")
            else:
                threads.append(
                    Process(
                        target=self.download_chunk,
                        args=(file_name, cur_chunk, segment, HEADERS,),
                    )
                )
                cur_chunk += 1
        if multi_threading:
            for p in threads:
                p.start()
            print(f"[{datetime.now()}] Started download.")
            for p in threads:
                p.join()
            print(f"[{datetime.now()}] Download finishing.")
        if use_ffmpeg:
            print("Merging chunks into mp4.")
            concat = '"concat'
            for x in range(0, total_chunks):
                if x == 0:
                    concat += f":chunks\/{file_name}-{x}.chunk.ts"
                else:
                    concat += f"|chunks\/{file_name}-{x}.chunk.ts"
            concat += '"'
            subprocess.run(f'ffmpeg -i {concat} -c copy "{file_name}.mp4"')

        else:
            print("Merging chunks into mp4")
            with open(f"{file_name}.mp4", "wb") as merged:
                for ts_file in [
                    f"chunks\/{file_name}-{x}.chunk.ts" for x in range(0, total_chunks)
                ]:
                    with open(ts_file, "rb") as ts:
                        shutil.copyfileobj(ts, merged)
        if delete_chunks:
            for x in range(0, total_chunks):
                # Remove chunk files
                os.remove(f"chunks\/{file_name}-{x}.chunk.ts")

    def get_available_qualities(self):
        aniwatch_episode = self.get_aniwatch_episode()
        return list(aniwatch_episode.stream.sources.keys())

    def toggle_mark_as_watched(self):
        data = {
            "controller": "Profile",
            "action": "markAsWatched",
            "detail_id": str(self.anime_id),
            "episode_id": self.ep_id,
        }
        return self.__post(data)["success"]

    def __repr__(self):
        return f"<Episode {self.number}: {self.title}>"


class AniWatchEpisode(object):
    def __init__(self, data_dict, episode_id):
        self.episode_id = episode_id
        self.languages = [Language(lang) for lang in data_dict.get("lang", None)]
        self.stream = Stream(data_dict.get("stream", None))

    def __repr__(self):
        return f"Episode ID: {self.episode_id}"
