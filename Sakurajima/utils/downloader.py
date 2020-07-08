import requests
import os
from Crypto.Cipher import AES
from Sakurajima.utils.merger import ChunkMerger, FFmpegMerger

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

        for chunk_number, segment in enumerate(self.m3u8.data["segments"]):
            file_name = f"chunks\/{self.file_name}-{chunk_number}.chunk.ts"
            ChunkDownloader(self.headers, self.cookies, segment, file_name).download()

    def merge(self):
        if self.use_ffmpeg:
            FFmpegMerger(self.file_name, self.total_chunks).merge()
        else:
            ChunkMerger(self.file_name, self.total_chunks).merge()


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
