from .. models import base_models as bm

class EpisodeList(object):
    def __init__(self, episode_list):
        self.validate_list(episode_list)
        self.__episode_list = episode_list

    def validate_list(self, episode_list):
        for episode in episode_list:
            if isinstance(episode, bm.Episode):
                continue
            else:
                raise ValueError("EpisodeList only take in lists that contain only Episode objects")

    def get_episode_by_number(self, episode_number):
        return list(filter(
            lambda episode: True if episode.number == episode_number else False,
            self.__episode_list
            ))[0]

    def get_episode_by_title(self, title):
        return list(filter(
            lambda episode: True if episode.title == title else False,
            self.__episode_list
            ))[0]
    
    def __getitem__(self, position):
        return self.__episode_list[position]
    
    def __reversed__(self):
        return self[::-1]
    
    def __repr__(self):
        return f"<EpisodeList({self.__episode_list})>"