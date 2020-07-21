class AniwatchStats(object):
    def __init__(self, data_dict):
        self.total_streams = data_dict["hoster"][0]["count"]
        """The total number of streams on aniwatch.me"""
        self.total_1080p_streams = data_dict["hoster"][0]["rows"][0]["count"]
        """The total number of 1080p streams on aniwatch.me"""
        self.total_720p_streams = data_dict["hoster"][0]["rows"][1]["count"]
        """The total number of 720p streams on aniwatch.me"""
        self.total_480p_streams = data_dict["hoster"][0]["rows"][2]["count"]
        """The total number of 480p streams on aniwatch.me"""
        self.total_360p_streams = data_dict["hoster"][0]["rows"][3]["count"]
        """The total number of 360p streams on aniwatch.me"""
        self.registered_users = data_dict["user"][0]["count"]
        """The total number of registered users on aniwatch.me"""
        self.registered_users_graph_data = data_dict["user"][0]["rows"]
        """The graph data for the total number of registered users on aniwatch.me"""
        self.new_registered_users = data_dict["user"][1]["count"]
        """The total number of users who have registered recently."""
        self.new_registered_users_graph_data = data_dict["user"][1]["rows"]
        """The graph data for the recently joined users."""
        self.total_shows = data_dict["entry"]["count"]
        """The total number of shows on aniwatch, this is the sum total of all the
        animes, specials, movies and hentais."""
        self.total_animes = data_dict["entry"]["rows"][0]["count"]
        """The total number of animes on aniwatch.me"""
        self.total_specials = data_dict["entry"]["rows"][1]["count"]
        """The total number of specials on aniwatch.me"""
        self.total_movies = data_dict["entry"]["rows"][2]["count"]
        """The total number of movies on aniwatch.me"""
        self.total_hentais = data_dict["entry"]["rows"][3]["count"]
        """The total number of hentais on aniwatch.me"""
        # I don't know what they mean by it, the api response has a "Unknown" column the same way it
        # has the total anime and total movie column so I decided to include it.
        self.total_unknowns = data_dict["entry"]["rows"][4]["count"]
        """The total number of shows that don't fall into any of the categories."""

    def __repr__(self):
        return "<AniwatchStats>"