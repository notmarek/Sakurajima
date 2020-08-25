import shutil
import subprocess
import os


class ChunkMerger(object):
    """Merges the downloaded chunks by concatinating them into a single file.
    """
    def __init__(self, file_name, total_chunks):
        """
        :param file_name: The file name prefix of the chunks. 
        :type file_name: str
        :param total_chunks: The total number of chunks. The merger assumes thet the chunks are 
                             in a ``chunks`` directory and are named according to a sequence 
                             i.e. "{file_name}-{chunk_number}.chunk.ts"
        :type total_chunks: int
        """
        self.file_name = file_name
        self.total_chunks = total_chunks

    def merge(self):
        """Starts the merger and creates a single file ``.mp4`` file.
        """
        with open(f"{self.file_name}.mp4", "wb") as merged_file:
            for ts_file in [
                open(f"chunks\/{self.file_name}-{chunk_number}.chunk.ts")
                for chunk_number in range(self.total_chunks)
            ]:
                shutil.copyfileobj(ts_file, merged_file)


class FFmpegMerger(object):
    """Merges the downloaded chunks using ``ffmpeg``.
    """
    def __init__(self, file_name, total_chunks):
        """
        The parameters have the same meaning as in :class:`ChunkMerger`"""
        self.file_name = file_name
        self.total_chunks = total_chunks

    def merge(self):
        """Starts the merger and creates a single file ``.mp4`` file.
        """
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
