from Sakurajima.models import base_models as bm


class EpisodeList(object):
    """An :class:`EpisodeList` is very similar to a normal list. You can do everything
    with a :class:`EpisodeList` that you can with a normal list. The only difference is that 
    an EpisodeList has some convinience methods that make selecting a particular episode easier. 
    """
    def __init__(self, episode_list):
        self.validate_list(episode_list)
        self.__episode_list = episode_list

    def validate_list(self, episode_list):
        for episode in episode_list:
            if isinstance(episode, bm.Episode):
                continue
            else:
                raise ValueError(
                    "EpisodeList only take in lists that contain only Episode objects"
                )

    def get_episode_by_number(self, episode_number: int):
        """Returns the first :class:`Episode` object from the list whose ``number`` attribue matches the 
        ``episode_number`` parameter.

        :param episode_number: The episode number that you want to find in the list.
        :type episode_number: int

        :rtype: :class:`Episode`
        """
        def check_episode_number(episode):
            if episode.number == episode_number:
                return True
            else:
                return False

        result = None
        for episode in self.__episode_list:
            if check_episode_number(episode):
                result = episode
                break 
        return result

    def get_episode_by_title(self, title: str):
        """Returns the first :class:`Episode` object from the list whose ``title`` attribue matches the 
        ``title`` parameter.

        :param title: The title of the episode that you want to find.
        :type title: str
        
        :rtype: :class:`Episode`        
        """
        def check_episode_title(episode):
            if episode.title == title:
                return True
            else:
                return False

        result = None
        
        for episode in self.__episode_list:
            if check_episode_title(episode):
                result = episode
                break
        return result

    def last(self):
        """Returns the last :class:`Episode` object from the list.

        :rtype: :class:`Episode`
        """
        return self.__episode_list[:-1]
    
    def __getitem__(self, position):
        if isinstance(position, int):
            return self.__episode_list[position]
        elif isinstance(position, slice):
            return EpisodeList(self.__episode_list[position])

    def __len__(self):
        return len(self.__episode_list)

    def __reversed__(self):
        return self[::-1]

    def __repr__(self):
        return f"EpisodeList({self.__episode_list})"
