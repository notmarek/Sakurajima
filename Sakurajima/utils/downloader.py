import os
from Crypto.Cipher import AES
from Sakurajima.utils.merger import ChunkMerger, FFmpegMerger, ChunkRemover
from threading import Thread, Lock
from progress.bar import IncrementalBar
from Sakurajima.utils.progress_tracker import ProgressTracker


class Downloader(object):
    """
    Facilitates downloading an episode from aniwatch.me using a single thread.

    """
    def __init__(
        self,
        network,
        m3u8,
        file_name: str,
        episode_id: int,
        use_ffmpeg: bool = True,
        include_intro: bool = False,
        delete_chunks: bool = True,
        on_progress=None,
    ):
        """
        :param network: The Sakurajima :class:`Network` object that is used to make network requests.  
        :type network: :class:`Network`
        :param m3u8: The M3U8 data of the episode that is to be downloaded.
        :type m3u8: :class:`M3U8`
        :param file_name: The name of the downloaded video file.
        :type file_name: str
        :param episode_id: The episode ID of the episode being downloaded.
                           This is only required to uniquely identify the progree
                           tracking data of the episode.
        :type episode_id: int
        :param use_ffmpeg: Whether to use ``ffmpeg`` to merge the downlaoded chunks, defaults to True
        :type use_ffmpeg: bool, optional
        :param include_intro: Whether to include the 5 second aniwatch intro, defaults to False
        :type include_intro: bool, optional
        :param delete_chunks: Whether to delete the downloaded chunks after that have been
                              merged into a single file, defaults to True
        :type delete_chunks: bool, optional
        :param on_progress: Register a function that is called every time a chunk is downloaded, the function
                            passed the chunk number of the downloaded chunk and the total number of chunks as 
                            parameters, defaults to None
        :type on_progress:  ``function``, optional
        """
        self.__network = network
        self.m3u8 = m3u8
        self.file_name = file_name
        self.use_ffmpeg = use_ffmpeg
        self.include_intro = include_intro
        self.delete_chunks = delete_chunks
        self.on_progress = on_progress
        self.progress_tracker = ProgressTracker(episode_id)

    def init_tracker(self):
        self.progress_tracker.init_tracker(
            {
                "headers": self.__network.headers,
                "cookies": self.__network.cookies,
                "segments": self.m3u8.data["segments"],
                "file_name": self.file_name,
                "total_chunks": self.total_chunks,
            }
        )

    def download(self):
        """Runs the downloader and starts downloading the video file.
        """
        if not self.include_intro:
            for segment in self.m3u8.data["segments"]:
                if "img.aniwatch.me" in segment["uri"]:
                    self.m3u8.data["segments"].remove(segment)
        self.total_chunks = len(self.m3u8.data["segments"])

        try:
            os.makedirs("chunks")
        except FileExistsError:
            pass

        self.progress_bar = IncrementalBar("Downloading", max=self.total_chunks)
        self.init_tracker()

        for chunk_number, segment in enumerate(self.m3u8.data["segments"]):
            file_name = f"chunks\/{self.file_name}-{chunk_number}.chunk.ts"
            ChunkDownloader(self.__network, segment, file_name).download()
            self.progress_bar.next()
            self.progress_tracker.update_chunks_done(chunk_number)
            if self.on_progress:
                self.on_progress.__call__(chunk_number + 1, self.total_chunks)

        self.progress_bar.finish()

    def merge(self):
        """Merges the downloaded chunks into a single file.
        """
        if self.use_ffmpeg:
            FFmpegMerger(self.file_name, self.total_chunks).merge()
        else:
            ChunkMerger(self.file_name, self.total_chunks).merge()

    def remove_chunks(self):
        """Deletes the downloaded chunks.
        """
        ChunkRemover(self.file_name, self.total_chunks).remove()


class ChunkDownloader(object):
    """
    The object that actually downloads a single chunk.
    """
    def __init__(self, network, segment, file_name):
        """
        :param network: The Sakurajima :class:`Network` object that is used to make network requests. 
        :type network: :class:`Network`
        :param segment: The segement data from that M3U8 file that is to be downloaded. 
        :type segment: :class:`dict`
        :param file_name: The file name of the downloaded chunk.  
        :type file_name: :class:`str`
        """
        self.__network = network
        self.segment = segment
        self.file_name = file_name

    def download(self):
        """Starts downloading the chunk.
        """
        with open(self.file_name, "wb") as videofile:
            res = self.__network.get(self.segment["uri"])
            chunk = res.content
            key_dict = self.segment.get("key", None)
            if key_dict is not None:
                key = self.get_decrypt_key(key_dict["uri"])
                decrypted_chunk = self.decrypt_chunk(chunk, key)
                videofile.write(decrypted_chunk)
            else:
                videofile.write(chunk)

    def get_decrypt_key(self, uri):
        res = self.__network.get(uri)
        return res.content

    def decrypt_chunk(self, chunk, key):
        decryptor = AES.new(key, AES.MODE_CBC)
        return decryptor.decrypt(chunk)


class MultiThreadDownloader(object):
    """
    Facilitates downloading an episode from aniwatch.me using multiple threads.
    """
    def __init__(
        self,
        network,
        m3u8,
        file_name: str,
        episode_id: int,
        max_threads: int = None,
        use_ffmpeg: bool = True,
        include_intro: bool = False,
        delete_chunks: bool = True,
    ):
        """
        :param network: The Sakurajima :class:`Network` object that is used to make network requests.
        :type network: :class:`Network`
        :type m3u8: :class:`M3U8`
        :param file_name: The name of the downloaded video file.
        :type file_name: str
        :param episode_id: The episode ID of the episode being downloaded.
                           This is only required to uniquely identify the progree
                           tracking data of the episode.
        :type episode_id: int
        :param max_threads: The maximum number of threads that will be used for downloading, defaults to None,
                            if None, the maximum possible number of threads will be used.
        :type max_threads: int, optional
        :param use_ffmpeg: Whether to use ``ffmpeg`` to merge the downlaoded chunks, defaults to True
        :type use_ffmpeg: bool, optional
        :param include_intro: Whether to include the 5 second aniwatch intro, defaults to False
        :type include_intro: bool, optional
        :param delete_chunks: Whether to delete the downloaded chunks after that have been
                              merged into a single file, defaults to True
        :type delete_chunks: bool, optional
        """
        self.__network = network
        self.m3u8 = m3u8
        self.file_name = file_name
        self.use_ffmpeg = use_ffmpeg
        self.include_intro = include_intro
        self.delete_chunks = delete_chunks
        self.threads = []
        self.progress_tracker = ProgressTracker(episode_id)
        self.__lock = Lock()

        if not include_intro:
            for segment in self.m3u8.data["segments"]:
                if "img.aniwatch.me" in segment["uri"]:
                    self.m3u8.data["segments"].remove(segment)
        self.total_chunks = len(self.m3u8.data["segments"])

        if max_threads is None:
            self.max_threads = self.total_chunks
        else:
            self.max_threads = max_threads

        try:
            os.makedirs("chunks")
        except FileExistsError:
            pass

    def init_tracker(self):
        self.progress_tracker.init_tracker(
            {
                "headers": self.__network.headers,
                "cookies": self.__network.cookies,
                "segments": self.m3u8.data["segments"],
                "file_name": self.file_name,
                "total_chunks": self.total_chunks,
            }
        )

    def start_threads(self):
        for t in self.threads:
            t.start()
        for t in self.threads:
            t.join()

    def reset_threads(self):
        self.threads = []

    def assign_target(self, network, segment, file_name, chunk_number):
        ChunkDownloader(network, segment, file_name).download()
        with self.__lock:
            self.progress_tracker.update_chunks_done(chunk_number)
            self.progress_bar.next()

    def download(self):
        """Runs the downloader and starts downloading the video file.
        """
        stateful_segment_list = StatefulSegmentList(self.m3u8.data["segments"])
        self.progress_bar = IncrementalBar("Downloading", max=self.total_chunks)
        self.init_tracker()
        while True:
            try:
                for _ in range(self.max_threads):
                    chunk_number, segment = stateful_segment_list.next()
                    file_name = f"chunks\/{self.file_name}-{chunk_number}.chunk.ts"
                    self.threads.append(
                        Thread(target=self.assign_target, args=(self.__network, segment, file_name, chunk_number),)
                    )
                self.start_threads()
                self.reset_threads()
            except IndexError:
                if self.threads != []:
                    self.start_threads()
                    self.reset_threads()
                break
        self.progress_bar.finish()

    def merge(self):
        """Merges the downloaded chunks into a single file.
        """
        if self.use_ffmpeg:
            FFmpegMerger(self.file_name, self.total_chunks).merge()
        else:
            ChunkMerger(self.file_name, self.total_chunks).merge()

    def remove_chunks(self):
        """Deletes the downloaded chunks.
        """
        ChunkRemover(self.file_name, self.total_chunks).remove()


class StatefulSegmentList(object):
    def __init__(self, segment_list):
        self.segment_list = segment_list
        self.index = 0

    def next(self):
        segment = self.segment_list[self.index]
        index = self.index
        self.index += 1
        return index, segment
