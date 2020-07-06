class RelationEntry(object):
    def __init__(self, data_dict):
        self.title = data_dict.get("title", None)
        self.episodes_max = data_dict.get("episodes_max", None)
        self.type = data_dict.get("type", None)
        self.cover = data_dict.get("cover", None)
        self.anime_id = data_dict.get("detail_id", None)
        self.airing_start = data_dict.get("airing_start", None)
        self.d_status = data_dict.get("d_status", None)
        self.has_nudity = data_dict.get("hasNudity", None)
        self.progress = data_dict.get("progress", None)
        self.cur_episodes = data_dict.get("cur_episodes", None)
        self.completed = data_dict.get("completed", None)

    def __repr__(self):
        return f"<Relation Entry {self.title}>"


class Relation(object):
    def __init__(self, data_dict):
        self.relation_id = data_dict.get("relation_id", None)
        self.title = data_dict.get("title", None)
        self.description = data_dict.get("description")
        self.entries = [RelationEntry(data) for data in data_dict["entries"]]

    def __repr__(self):
        return f"<Relation {self.title}>"

