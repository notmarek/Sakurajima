from Sakurajima.utils.misc import Misc
from requests import Session


class Network:
    def __init__(self, username: str, user_id: str, auth_token: str, proxies, endpoint):
        self.API_URL = endpoint
        self.session = Session()
        self.session.proxies = proxies
        self.headers = self.session.headers  # Expose session headers
        self.headers["referer"] = "https://aniwatch.me/"
        self.cookies = self.session.cookies  # Expose session cookies
        xsrf_token = Misc().generate_xsrf_token()
        headers = {
            "x-xsrf-token": xsrf_token,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        }
        cookies = {"xsrf-token": xsrf_token}
        if username is not None and user_id is not None and user_id is not None:
            headers["x-auth"] = auth_token
            session_token = (
                '{"userid":'
                + str(user_id)
                + ',"username":"'
                + str(username)
                + '","usergroup":4,"player_lang":1,"player_quality":0,"player_time_left_side":2,"player_time_right_side":3,"screen_orientation":1,"nsfw":1,"chrLogging":1,"mask_episode_info":0,"blur_thumbnails":0,"autoplay":1,"preview_thumbnails":1,"update_watchlist":1,"playheads":1,"seek_time":5,"cover":null,"title":"Member","premium":1,"lang":"en-US","auth":"'
                + str(auth_token)
                + '","remember_login":true}'
            )
            cookies["SESSION"] = session_token
            headers["COOKIE"] = f"SESSION={session_token}; XSRF-TOKEN={xsrf_token};"
        self.session.headers.update(headers)
        self.session.cookies.update(cookies)

    def __repr__(self):
        return "<Network>"

    def post(self, data):
        try:
            res = self.session.post(self.API_URL, json=data)
            return res.json()
        except Exception as e:
            self.session.close()
            raise e

    def get(self, uri):
        try:
            res = self.session.get(uri)
            return res
        except Exception as e:
            self.session.close()
            raise e
