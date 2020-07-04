class WatchListEntry(object):
    def __init__(self, data_dict, headers, cookies, api_url):
        self.headers = headers
        self.cookies = cookies
        self.API_URL = api_url
        self.title = data_dict.get('title', None)
        self.type = data_dict.get('type', None)
        self.anime_id = data_dict.get('detail_id', None)
        self.selPage = data_dict.get('selPage', None)
        self.pages = data_dict.get('pages', None)
        self.status = data_dict.get('status', None)
        self.progress = data_dict.get('progress', None)
        self.list_status = data_dict.get('list_status', None)
        self.max_episodes = data_dict.get('max_episodes', None)
        self.cover = data_dict.get('cover', None)
        self.available_episodes = data_dict.get('available_episodes', None)
        self.episodes = [Episode(data, self.headers, self.cookies, self.API_URL, self.anime_id) for data in data_dict.get('episodes', [])]

    def __repr__(self):
        return f'<WatchListEntry : {self.title}>'