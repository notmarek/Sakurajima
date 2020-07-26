import random


class Misc:
    def __repr__(self):
        return "<Misc>"

    def generate_xsrf_token(self):
        characters = [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
        ]
        return "".join(random.choice(characters) for i in range(32))
