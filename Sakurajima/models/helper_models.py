class Support(object):
    def __init__(self, data_dict):
        self.screenshot = data_dict.get('screenshot', None)
        self.download = data_dict.get('download', None)
        self.download_type = data_dict.get('download_type', None)

class Language(object):
    def __init__(self, data_dict):
        self.language = data_dict.get('str', None)
        self.id = data_dict.get('id', None)

class Stream(object):
    def __init__(self, data_dict):
        self.sources = data_dict.get('src', None)
        self.lang = data_dict.get('lang', None)
        self.no_streams = data_dict.get('no_streams', None)
        self.hoster = data_dict.get('hoster', None)
        self.hosters = data_dict.get('hosters', None)
        self.hosterkey = data_dict.get('hosterKey', None)
        self.support = Support(data_dict.get('support', None))
        self.sprites = data_dict.get('sprites', None)