import shutil
import subprocess
import os


class ChunkMerger(object):
    def __init__(self, file_name, total_chunks):
        self.file_name = file_name
        self.total_chunks = total_chunks

    def merge(self):
        with open(f"{self.file_name}.mp4", "wb") as merged_file:
            for ts_file in [
                open(f"chunks\/{self.file_name}-{chunk_number}.chunk.ts")
                for chunk_number in range(self.total_chunks)
            ]:
                shutil.copyfileobj(ts_file, merged_file)


class FFmpegMerger(object):
    def __init__(self, file_name, total_chunks):
        self.file_name = file_name
        self.total_chunks = total_chunks

    def merge(self):
        print("Merging chunks into mp4.")
        concat = '"concat'
        for x in range(0, self.total_chunks):
            if x == 0:
                concat += f":chunks\/{self.file_name}-{x}.chunk.ts"
            else:
                concat += f"|chunks\/{self.file_name}-{x}.chunk.ts"
        concat += '"'
        subprocess.run(f'ffmpeg -i {concat} -c copy "{self.file_name}.mp4"')


class ChunkRemover(object):
    def __init__(self, file_name, total_chunks):
        self.file_name = file_name
        self.total_chunks = total_chunks

    def remove(self):
        for chunk_number in range(self.total_chunks):
            try:
                os.remove(f"chunks\/{self.file_name}-{chunk_number}.chunk.ts")
            except FileNotFoundError:
                pass
