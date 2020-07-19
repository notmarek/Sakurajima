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
from Sakurajima.utils.downloader import Downloader, MultiThreadDownloader
import subprocess
from time import sleep
from pathvalidate import sanitize_filename
from multiprocessing import Process
import os
import shutil


class Anime(object):
    """Wraps all the relevant data for an anime like anime_id
    (called as detail_id by AniWatch backend), title, airing date etc.
    Use the get_episodes method to get a list of available episodes"""

    def __init__(self, data_dict: dict, network, api_url: str):
        self.__network = network
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
            self.broadcast_start = datetime.utcfromtimestamp(data_dict.get("broadcast_start"))
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
        """Gets a list of all available episodes of the anime. 

        :return: An EpisodeList object, an EpisodeList object is very similar to a 
                 normal list. You can access specific indexes using the "[]" syntax.
                 In addition to this, an EpisodeList has few convinience methods like
                 ``get_episode_by_number(episode_number)`` which returns an episode with the provided
                 episode number.
        :rtype: EpisodeList
        """
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
                    Episode(data_dict, self.__network, self.__API_URL, self.anime_id, self.title,)
                    for data_dict in self.__network.post(data)["episodes"]
                ]
            )
            return self.__episodes

    def __repr__(self):
        return f"<Anime: {self.title}>"

    def get_relations(self):
        """Gets the relation of the anime.

        :return: A Relation object that contains all the details of the relation.
        :rtype: Relation
        """
        data = {
            "controller": "Relation",
            "action": "getRelation",
            "relation_id": self.relation_id,
        }
        return Relation(self.__network.post(data)["relation"])

    def get_recommendations(self):
        """Gets the recommendations for the anime.

        :return: A list of RecommendationEntry objects where each object represents 
                 a single recommendation. 
        :rtype: list[RecommendationEntry]
        """
        data = {
            "controller": "Anime",
            "action": "getRecommendations",
            "detail_id": str(self.anime_id),
        }
        return [
            RecommendationEntry(data_dict, self.__network, self.__API_URL)
            for data_dict in self.__network.post(data)["entries"]
        ]

    def get_chronicle(self, page=1):
        """Gets the chronicle for the anime, a chronicle tracks the user's watch 
        history for a particular anime.         
        

        :param page: The page of the chronicle you want to get, defaults to 1
        :type page: int, optional
        :return: A list of ChronicleEntry objects where each object has details like date.
        :rtype: list[ChronicleEntry]
        """
        data = {
            "controller": "Profile",
            "action": "getChronicle",
            "detail_id": str(self.anime_id),
            "page": page,
        }
        return [
            ChronicleEntry(data_dict, self.__network, self.__API_URL)
            for data_dict in self.__network.post(data)["chronicle"]
        ]

    def mark_as_completed(self):
        """Marks the anime as "completed" on the user's aniwatch anime list.

        :return: True if the operation is successful, False if an error occurs.
        :rtype: bool
        """
        data = {
            "controller": "Profile",
            "action": "markAsCompleted",
            "detail_id": str(self.anime_id),
        }
        return self.__network.post(data)["success"]

    def mark_as_plan_to_watch(self):
        """Marks the anime as "plan to watch" on the user's aniwatch anime list.

        :return: True if the operation is successful, False if an error occurs.
        :rtype: bool
        """
        data = {
            "controller": "Profile",
            "action": "markAsPlannedToWatch",
            "detail_id": str(self.anime_id),
        }
        return self.__network.post(data)["success"]

    def mark_as_on_hold(self):
        """Marks the anime as "on hold" on the user's aniwatch anime list.

        :return: True if the operation is successful, False if an error occurs.
        :rtype: bool
        """
        data = {
            "controller": "Profile",
            "action": "markAsOnHold",
            "detail_id": str(self.anime_id),
        }
        return self.__network.post(data)["success"]

    def mark_as_dropped(self):
        """Marks the anime as "dropped" on the user's aniwatch anime list.

        :return: True if the operation is successful, False if an error occurs.
        :rtype: bool
        """
        data = {
            "controller": "Profile",
            "action": "markAsDropped",
            "detail_id": str(self.anime_id),
        }
        return self.__network.post(data)["success"]

    def mark_as_watching(self):
        """Marks the anime as "watching" on the user's aniwatch anime list

        :return: True if the operation is successful, False if an error occurs.
        :rtype: bool
        """
        data = {
            "controller": "Profile",
            "action": "markAsWatching",
            "detail_id": str(self.anime_id),
        }
        return self.__network.post(data)["success"]

    def remove_from_list(self):
        """Removes the anime from the user's aniwatch anime list.

        :return: True if the operation is successful, False if an error occurs.
        :rtype: bool
        """
        data = {
            "controller": "Profile",
            "action": "removeAnime",
            "detail_id": str(self.anime_id),
        }
        return self.__network.post(data)["success"]

    def rate(self, rating: int):
        """Set the user's rating for the anime on aniwatch.

        :param rating: The rating you want to set, should be between 1 to 10.
                       Rate 0 to remove the user's rating for the anime
        :type rating: int
        :return: True if the operation is successful, False if an error occurs.
        :rtype: bool
        """
        # Rate 0 to remove rating
        data = {
            "controller": "Profile",
            "action": "rateAnime",
            "detail_id": str(self.anime_id),
            "rating": rating,
        }
        return self.__network.post(data)["success"]

    def get_media(self):
        """Gets the anime's associated media from aniwatch.me 

        :return: A Media object that has attributes like ``opening``, ``osts``.
        :rtype: Media
        """
        data = {
            "controller": "Media",
            "action": "getMedia",
            "detail_id": str(self.anime_id),
        }
        return Media(self.__network.post(data), self.__network, self.__API_URL, self.anime_id,)

    def get_complete_object(self):
        """Gets the current anime object but with complete attributes. Sometimes, the Anime
        object that is returned by the API does not contain values for all the attributes 
        that the Anime object has. Use this method to get an object with the maximum amount of 
        data. This method is almost never required but is for edge cases 

        :return: An Anime object with values for as many attributes as possible.
        :rtype: Anime
        """
        data = {
            "controller": "Anime",
            "action": "getAnime",
            "detail_id": str(self.anime_id),
        }
        data_dict = self.__network.post(data)["anime"]
        return Anime(data_dict, self.__network, api_url=self.__API_URL,)

    def add_recommendation(self, recommended_anime_id: int):
        """Adds the user's reccomendation for the anime. 

        :param recommended_anime_id: The aniwatch anime ID of the anime you want to recommend. 
        :type recommended_anime_id: int
        :return: [description]
        :rtype: [type]
        """
        data = {
            "controller": "Anime",
            "action": "addRecommendation",
            "detail_id": str(self.anime_id),
            "recommendation": str(recommended_anime_id),
        }
        return self.__network.post(data)

    def get_dict(self):
        """Gets the JSON response in the form of a dictionary that was used to
        initialize the object.

        :return: A dictionary of the JSON response
        :rtype: dict
        """
        return self.data_dict


class Episode(object):
    def __init__(self, data_dict, network, api_url, anime_id, anime_title=None):
        self.anime_title = anime_title
        """The title of the anime that the episode belongs to."""
        self.__network = network
        self.anime_id = anime_id
        """The anime ID of the anime that the episode belongs to."""
        self.__API_URL = api_url
        self.number = data_dict.get("number", None)
        """The episode number of the episode."""
        self.title = data_dict.get("title", None)
        """The title of the episode."""
        self.description = data_dict.get("description", None)
        """The description of the episode.
        """
        self.thumbnail = data_dict.get("thumbnail", None)
        """The URL to the thumbnail for the episode."""
        self.added = datetime.utcfromtimestamp(data_dict.get("added", None))
        """The date when the episode was added."""
        self.filler = data_dict.get("filler", None)
        """Is set to 1 if the episode is filler else 0"""
        self.ep_id = data_dict.get("ep_id", None)
        """The ID of the episode"""
        self.duration = data_dict.get("duration", None)
        """The duration of the episode"""
        self.is_aired = data_dict.get("is_aired", None)
        """Is set to 1 if the episode has aired else 0.""" 
        self.lang = data_dict.get("lang", None)
        """The language of the episode."""
        self.watched = data_dict.get("watched", None)
        """Is set to 1 if the user has marked the episode as watched else 0"""
        self.__aniwatch_episode = None
        self.__m3u8 = None

    def __generate_referer(self):
        return f"https://aniwatch.me/anime/{self.anime_id}/{self.number}"

    def __get_decrypt_key(self, url):
        res = self.__network.get(url)
        return res.content

    def __decrypt_chunk(self, chunk, key):
        decrytor = AES.new(key, AES.MODE_CBC)
        return decrytor.decrypt(chunk)

    def get_aniwatch_episode(self, lang="en-US"):
        """Gets the AniWatchEpisode object associated with the episode.
        An AniWatchEpisode has data regarding languages and streams available 
        for the current anime. 

        :param lang: Used only because the aniwatch API requires it, defaults to "en-US"
        :type lang: str, optional
        :return: An AniWatchEpisode object.
        :rtype: AniWatchEpisode
        """
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
            self.__aniwatch_episode = AniWatchEpisode(self.__network.post(data), self.ep_id)
            return self.__aniwatch_episode

    def get_m3u8(self, quality: str) -> M3U8:
        """Gets the episode's M3U8 data.

        :param quality: The quality whose M3U8 data you need. All the available 
                        are "ld" (360p), "sd" (480p), "hd" (720p) and "fullhd" (1080p).
        :type quality: str
        :return: A M3U8 object, the data can be accessed by calling the ``data`` property on the
                 object.
        :rtype: M3U8
        """
        if self.__m3u8:
            return self.__m3u8
        else:
            REFERER = self.__generate_referer()
            self.__network.headers.update({"REFERER": REFERER, "ORIGIN": "https://aniwatch.me"})
            aniwatch_episode = self.get_aniwatch_episode()
            res = self.__network.get(aniwatch_episode.stream.sources[quality])
            self.__m3u8 = M3U8(res.text)
            return self.__m3u8

    def download_chunk(self, file_name, chunk_num, segment):
        try:
            os.mkdir("chunks")
        except FileExistsError:
            pass
        with open(f"chunks\/{file_name}-{chunk_num}.chunk.ts", "wb") as videofile:
            res = self.__network.get(segment["uri"])
            chunk = res.content
            key_dict = segment.get("key", None)
            if key_dict is not None:
                key = self.__get_decrypt_key(key_dict["uri"])
                decrypted_chunk = self.__decrypt_chunk(chunk, key)
                videofile.write(decrypted_chunk)
            else:
                videofile.write(chunk)

    def download(
        self,
        quality: str,
        file_name: str = None,
        path: str = None,
        multi_threading: bool = False,
        max_threads: int = None,
        use_ffmpeg: bool = True,
        include_intro: bool = False,
        delete_chunks: bool = True,
        on_progress=None,
        print_progress: bool = True,
    ):
        """Downloads the current episode in your selected quality.

        :param quality: The quality that you want to dowload. All the available 
                        are "ld" (360p), "sd" (480p), "hd" (720p) and "fullhd".
                        Note that all qualities may not be available for all episodes.
        :type quality: str
        :param file_name: The name of the downloaded file. If left to None, the file will be named
                        "[anime_name] - [episode_number].mp4". Macros are also supported,
                        "<anititle>" will be replaced by the anime name, <ep> will be replaced 
                        by episode number and <eptitle> will be replaced by the episodes title.
                        For example, lets say that the episode in question is the third episode of
                        the anime called "Vinland Saga". The title of the episode is "Troll". Suppose
                        we pass the string ``"<anititle> - <ep> - <eptitle>"``, the resulting file will be 
                        named ``"Vinland Saga - 3 - Troll.mp4"``
        :type file_name: str, optional
        :param path: Path to where you want the downloaded video to be, defaults to None. If left None
                     the current working directory i.e. the directory where the script calling the method 
                     lives is taken as the path.
        :type path: str, optional
        :param multi_threading: Set this to true to enable multithreaded downloading, defaults to False.
                      Enabling this can offer significant performance benefits especially on faster
                      connections. However this comes with a trade off. Using multi threading negatively
                      affects download resumabilty. Therefore it is recommended that this be set to False 
                      when using slower connections.
        :type multi_threading: bool, optional
        :param max_threads: Set the maximum number of threads that will be used at once when using multi
                      threaded downloading, defaults to None. When None, the maximum number of feasible
                      threads will be used i.e one thread per chunk. 
        :type max_threads: int, optional
        :param use_ffmpeg: Enable/disable using FFMPEG to combine the downloaded chunks, defaults to True.
                      Requires FFMPEG. It is recommended to keep this enabled as not using FFMPEG can cause
                      video playback issues on certain players. Using FFMPEG also results in noticibly smaller
                      files.
        :type use_ffmpeg: bool, optional
        :param include_intro: Set this to true to include the 5 second aniwatch intro, defaults to False.
                      It is recommended to skip the intro as this causes issues when combining the chunks 
                      with FFMPEG.
        :type include_intro: bool, optional
        :param delete_chunks: Set this to False to not delete the downloaded .ts chunks after they have been, 
                              combined into a single mp4 file. Defaults to True
        :type delete_chunks: bool, optional
        :param on_progress: Register a function that is called every time a new chunk is downloaded. The the number
                      of chunks done and the total number of chunks are passed as arguments to the function in that
                      exact order. Defaults to None.              
        :type on_progress: function, optional
        :param print_progress: Print the number of chunks done and the total number of chunks to the console, 
                      defaults to True.
        :type print_progress: bool, optional
        """
        m3u8 = self.get_m3u8(quality)

        if file_name is None:
            file_name = f"{self.anime_title[:128]}-{self.number}"
        else:
            file_name = (
                file_name.replace("<ep>", str(self.number))
                .replace("<eptitle>", self.title)
                .replace("<anititle>", self.anime_title[:128])
            )
        file_name = sanitize_filename(file_name)
        current_path = os.getcwd()
        if path:
            os.chdir(path)
        
        if multi_threading:
            dlr = MultiThreadDownloader(
                self.__network, m3u8, file_name, self.ep_id, max_threads, use_ffmpeg, include_intro, delete_chunks,
            )
        else:
            dlr = Downloader(self.__network, m3u8, file_name, self.ep_id, use_ffmpeg, include_intro, delete_chunks,)
        
        dlr.download()
        dlr.merge()
        if delete_chunks:
            dlr.remove_chunks()
        os.chdir(current_path)

    def download_without_downloader(
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
        self.__network.headers.update({"REFERER": REFERER, "ORIGIN": "https://aniwatch.me"})
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
                self.download_chunk(file_name, chunks_done, segment)
                chunks_done += 1
                if print_progress:
                    print(f"{chunks_done}/{total_chunks} done.")
            else:
                threads.append(Process(target=self.download_chunk, args=(file_name, cur_chunk, segment,),))
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
                for ts_file in [f"chunks\/{file_name}-{x}.chunk.ts" for x in range(0, total_chunks)]:
                    with open(ts_file, "rb") as ts:
                        shutil.copyfileobj(ts, merged)
        if delete_chunks:
            for x in range(0, total_chunks):
                # Remove chunk files
                os.remove(f"chunks\/{file_name}-{x}.chunk.ts")

    def get_available_qualities(self):
        """Gets a list of available qualities for the episode.

        :return: A list of available qualities. "ld", "sd", "hd" and "fullhd"
                 refer to 360p, 480p, 720 and 1080p respectively.
        :rtype: list[str]
        """ 
        aniwatch_episode = self.get_aniwatch_episode()
        return list(aniwatch_episode.stream.sources.keys())

    def toggle_mark_as_watched(self):
        """Toggles the "mark as watched" status of the episode

        :return: True if the operation is successful, False if an error occured.
        :rtype: bool
        """
        data = {
            "controller": "Profile",
            "action": "markAsWatched",
            "detail_id": str(self.anime_id),
            "episode_id": self.ep_id,
        }
        return self.__network.post(data)["success"]

    def __repr__(self):
        return f"<Episode {self.number}: {self.title}>"


class AniWatchEpisode(object):
    def __init__(self, data_dict, episode_id):
        self.episode_id = episode_id
        self.languages = [Language(lang) for lang in data_dict.get("lang", None)]
        self.stream = Stream(data_dict.get("stream", None))

    def __repr__(self):
        return f"Episode ID: {self.episode_id}"
