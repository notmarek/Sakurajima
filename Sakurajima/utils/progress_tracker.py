import pickle
import os


class ProgressTracker(object):
    def __init__(self, episode_id):
        self.resume_data = None
        self.chunks_done = []
        self.episode_id = episode_id
        try:
            os.makedirs(f"chunks\/.temp-{episode_id}")
        except FileExistsError:
            pass
        
    def init_tracker(self, resume_data):
        with open(f"chunks\/.temp-{self.episode_id}\/.resume_data", "wb") as resume_data_file:
            pickle.dump(resume_data, resume_data_file)
        with open(f"chunks\/.temp-{self.episode_id}\/.chunks_done", "wb") as chunks_done_file:
            pickle.dump(self.chunks_done, chunks_done_file)

    def update_chunks_done(self, chunk_done: int):
        self.chunks_done.append(chunk_done)
        with open(f"chunks\/.temp-{self.episode_id}\/.chunks_done", "wb") as chunks_done_file:
            pickle.dump(self.chunks_done, chunks_done_file)

    def get_progress_data(self):
        try:
            with open(f"chunks\/.temp-{self.episode_id}\/.resume_data", "rb") as resume_data_file:
                resume_data = pickle.load(resume_data_file)
            with open(f"chunks\/.temp-{self.episode_id}\/.chunks_done", "rb") as chunks_done_file:
                chunks_done = pickle.load(chunks_done_file)
            return resume_data, chunks_done
        except:
            print("No data found!")
            return None

    def remove_data(self):
        os.remove(f"chunks\/.temp-{self.episode_id}\/.resume_data")
        os.remove(f"chunks\/.temp-{self.episode_id}\/.chunks_done")
