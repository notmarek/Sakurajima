import requests
import os
from Crypto.Cipher import AES
from Sakurajima.utils.merger import ChunkMerger, FFmpegMerger, ChunkRemover
from threading import Thread
from progress.bar import IncrementalBar
import pickle

class Downloader(object):
    def __init__(
        self,
        headers: dict,
        cookies: dict,
        m3u8,
        file_name: str,
        use_ffmpeg: bool = True,
        include_intro: bool = False,
        delete_chunks: bool = True,
        on_progress = None
        ):
        self.headers = headers
        self.cookies = cookies
        self.m3u8 = m3u8
        self.file_name = file_name
        self.use_ffmpeg = use_ffmpeg
        self.include_intro = include_intro
        self.delete_chunks = delete_chunks
        self.on_progress = on_progress
        self.chunks_done = []
        self.resume_data = {}
    
    def create_resume_data(self):
        self.resume_data.update(
            {
                "headers" : self.headers,
                "cookies" : self.cookies,
                "segments" : self.m3u8.data["segments"],
                "file_name" : self.file_name,
                "total_chunks": self.total_chunks
            }
        )
        with open(f"chunks\/.resume_data", "wb") as resume_data_file:
            pickle.dump(self.resume_data, resume_data_file)

    def update_chunks_done(self):
        with open(f"chunks\/.chunks_done", "wb") as chunks_done_file:
            pickle.dump(self.chunks_done, chunks_done_file)
    
    def download(self):
        if not self.include_intro:
            for segment in self.m3u8.data["segments"]:
                if "img.aniwatch.me" in segment["uri"]:
                    self.m3u8.data["segments"].remove(segment)
        self.total_chunks = len(self.m3u8.data["segments"])
        
        try:
            os.makedirs("chunks")
        except FileExistsError:
            pass

        self.progress_bar = IncrementalBar("Downloading", max = self.total_chunks)
        self.create_resume_data()
        for chunk_number, segment in enumerate(self.m3u8.data["segments"]):
            file_name = f"chunks\/{self.file_name}-{chunk_number}.chunk.ts"
            ChunkDownloader(self.headers, self.cookies, segment, file_name).download()
            self.chunks_done.append(chunk_number)
            self.progress_bar.next()
            self.update_chunks_done()
            if self.on_progress:
                self.on_progress.__call__(chunk_number+1, self.total_chunks)
        self.progress_bar.finish()

    def merge(self):
        if self.use_ffmpeg:
            FFmpegMerger(self.file_name, self.total_chunks).merge()
        else:
            ChunkMerger(self.file_name, self.total_chunks).merge()
 
    def remove_chunks(self):
        ChunkRemover(self.file_name, self.total_chunks).remove()

class ChunkDownloader(object):
    def __init__(
        self, 
        headers, 
        cookies,
        segment,
        file_name
        ):
        self.headers = headers
        self.cookies = cookies
        self.segment = segment
        self.file_name = file_name

    def download(self):
        with open(self.file_name, "wb") as videofile:
            res = requests.get(
                self.segment["uri"],
                headers = self.headers,
                cookies = self.cookies
            )
            chunk = res.content
            key_dict = self.segment.get('key', None)
            if key_dict is not None:
                key = self.get_decrypt_key(key_dict["uri"])
                decrypted_chunk = self.decrypt_chunk(chunk, key)
                videofile.write(decrypted_chunk)
            else:
                videofile.write(chunk)

    def get_decrypt_key(self, uri):
        res = requests.get(
            uri, 
            headers = self.headers,
            cookies = self.cookies
        )
        return res.content

    def decrypt_chunk(self, chunk, key):
        decryptor = AES.new(key, AES.MODE_CBC)
        return decryptor.decrypt(chunk)


class MultiThreadDownloader(object):
    def __init__(
        self,
        headers: dict,
        cookies: dict,
        m3u8,
        file_name: str,
        max_threads: int = None,
        use_ffmpeg: bool = True,
        include_intro: bool = False,
        delete_chunks: bool = True,
        ):
        self.headers = headers
        self.cookies = cookies
        self.m3u8 = m3u8
        self.file_name = file_name
        self.use_ffmpeg = use_ffmpeg
        self.include_intro = include_intro
        self.delete_chunks = delete_chunks
        self.threads = []
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

    def start_threads(self):
        for t in self.threads:
            t.start()
        for t in self.threads:
            t.join()
    
    def reset_threads(self):
        self.threads = []
    
    def assign_target(self, headers, cookies, segment, file_name):
        ChunkDownloader(headers, cookies, segment, file_name).download()
    
    def download(self):
        stateful_segment_list = StatefulSegmentList(self.m3u8.data["segments"])
        while True:
            try:
                for x in range(self.max_threads):
                    chunk_number, segment = stateful_segment_list.next()
                    file_name = f"chunks\/{self.file_name}-{chunk_number}.chunk.ts"
                    self.threads.append(
                        Thread(
                            target = self.assign_target,
                            args = (self.headers, self.cookies, segment, file_name)
                        )
                    )
                self.start_threads()
                self.reset_threads()
            except IndexError:
                if self.threads != []:
                    self.start_threads()
                    self.reset_threads()
                break
    
    def merge(self):
        if self.use_ffmpeg:
            FFmpegMerger(self.file_name, self.total_chunks).merge()
        else:
            ChunkMerger(self.file_name, self.total_chunks).merge()

    def remove_chunks(self):
        ChunkRemover(self.file_name, self.total_chunks).remove()

class StatefulSegmentList(object):
    def __init__(self, segment_list):
        self.segment_list = segment_list
        self.index = 0

    def next(self):
        segment = self.segment_list[self.index]
        index = self.index
        self.index +=1
        return index, segment