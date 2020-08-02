import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Sakurajima.utils.merger import ChunkMerger, FFmpegMerger, ChunkRemover
from threading import Thread, Lock
from progress.bar import IncrementalBar
from Sakurajima.utils.progress_tracker import ProgressTracker
from Sakurajima.utils.decrypter_provider import DecrypterProvider

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
        chunk_tuple_list = []
        # Will hold a list of tuples of the form (chunk_number, chunk).
        # The chunk_number in this list will start from 1.
        for chunk_number, chunk in enumerate(self.m3u8.data["segments"]):
            chunk_tuple_list.append((chunk_number, chunk))

        if not self.include_intro:
            for chunk_tuple in chunk_tuple_list:
                # Check if the string is in the URI of the chunk
                if "img.aniwatch.me" in chunk_tuple[1]["uri"]:
                    # Revome the tuple from the tuple list.
                    chunk_tuple_list.remove(chunk_tuple) 
        self.total_chunks = len(chunk_tuple_list)

        try:
            os.makedirs("chunks")
        except FileExistsError:
            pass

        self.progress_bar = IncrementalBar("Downloading", max=self.total_chunks)
        self.init_tracker()
        decryter_provider = DecrypterProvider(self__network, self.m3u8)
        for chunk_number, chunk_tuple in enumerate(chunk_tuple_list):
            # We need the chunk number here to name the files. Note that this is
            # different from the chunk number that is inside the tuple.
            file_name = f"chunks\/{self.file_name}-{chunk_number}.chunk.ts"
            ChunkDownloader(
                self.__network,
                chunk_tuple[1], # The segment data
                file_name,
                chunk_tuple[0], # The chunk number needed for decryption.
                decryter_provider
                ).download()
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
    def __init__(self, network, segment, file_name, chunk_number, decrypt_provider: DecrypterProvider):
        """
        :param network: The Sakurajima :class:`Network` object that is used to make network requests. 
        :type network: :class:`Network`
        :param segment: The segement data from that M3U8 file that is to be downloaded. 
        :type segment: :class:`dict`
        :param file_name: The file name of the downloaded chunk.  
        :type file_name: :class:`str`
        :param chunk_number: The chunk number of the the chunk to be downloaded, required to generate
                        the AES decryption initialization vector.
        :type chunk_number: int
        """
        self.__network = network
        self.segment = segment
        self.file_name = file_name
        self.chunk_number = chunk_number,
        self.decrypter_provider = decrypter_provider

    def download(self):
        """Starts downloading the chunk.
        """
        with open(self.file_name, "wb") as videofile:
            res = self.__network.get(self.segment["uri"])
            chunk = res.content
            key_dict = self.segment.get("key", None)
            
            if key_dict is not None:
                decrypted_chunk = self.decrypt_chunk(chunk)
                videofile.write(decrypted_chunk)
            else:
                videofile.write(chunk)
    
    def decrypt_chunk(self, chunk):
        decryter = self.decrypter_provider.get_decrypter(self.chunk_number)
        return decryter.decrypt(chunk)


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
        ChunkDownloader(network, segment, file_name, chunk_number).download()
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
