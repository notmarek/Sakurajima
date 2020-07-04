class AniwatchStats(object):
    def __init__(self, data_dict):
        self.total_streams = data_dict['hoster'][0]['count']
        self.total_1080p_streams = data_dict['hoster'][0]['rows'][0]['count']        
        self.total_720p_streams = data_dict['hoster'][0]['rows'][1]['count']
        self.total_480p_streams = data_dict['hoster'][0]['rows'][2]['count']
        self.total_360p_streams = data_dict['hoster'][0]['rows'][3]['count']
        self.registered_users = data_dict['user'][0]['count']
        self.registered_users_graph_data = data_dict['user'][0]['rows']
        self.new_registered_users = data_dict['user'][1]['count']
        self.new_registered_users_graph_data = data_dict['user'][1]['rows']
        self.total_show = data_dict['entry']['count']
        self.total_shows = data_dict['entry']['count']
        self.total_animes = data_dict['entry']['rows'][0]['count']
        self.total_specials = data_dict['entry']['rows'][1]['count']
        self.total_movies = data_dict['entry']['rows'][2]['count']
        self.total_hentais = data_dict['entry']['rows'][3]['count']
        # I don't know what they mean by it, the api response has a "Unknown" column the same way it
        # has the total anime and total movie column so I decided to include it.
        self.total_unknowns = data_dict['entry']['rows'][4]['count'] 
