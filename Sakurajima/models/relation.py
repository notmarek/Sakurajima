class RelationEntry(object):
    def __init__(self, data_dict):
        self.title = data_dict.get("title", None)
        """The title of the related anime."""
        self.episodes_max = data_dict.get("episodes_max", None)
        """The total number of episodes that the related anime has."""
        self.type = data_dict.get("type", None)
        """The type of the related anime. For example the type can be anime,
         special or movie."""
        self.cover = data_dict.get("cover", None)
        """The URL to the cover of the related anime."""
        self.anime_id = data_dict.get("detail_id", None)
        """The ID of the related anime."""
        self.airing_start = data_dict.get("airing_start", None)
        """The season when the related anime started airing."""
        self.d_status = data_dict.get("d_status", None)
        self.has_nudity = data_dict.get("hasNudity", None)
        """If the anime has nudity."""
        self.progress = data_dict.get("progress", None)
        """The number of episodes that the user has watched for recommended anime."""
        self.cur_episodes = data_dict.get("cur_episodes", None)
        """The total number of epiosodes that have aired for the recommended anime"""
        self.completed = data_dict.get("completed", None)
        """The "completed" status of the recommended anime."""

    def __repr__(self):
        return f"<Relation Entry {self.title}>"


class Relation(object):
    def __init__(self, data_dict):
        self.relation_id = data_dict.get("relation_id", None)
        """The ID of the relation."""
        self.title = data_dict.get("title", None)
        """The title of the relation"""
        self.description = data_dict.get("description")
        """The description of the relation."""
        self.entries = [RelationEntry(data) for data in data_dict["entries"]]
        """The entries in the relation"""
    
    def __repr__(self):
        return f"<Relation {self.title}>"
