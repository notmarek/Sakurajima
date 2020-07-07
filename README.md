# Sakurajima

![Pypi downloads](https://img.shields.io/pypi/dm/sakurajima?label=Downloads&style=for-the-badge&logo=python)
Sakurajima is a Python API wrapper for [AniWatch](https://aniwatch.me).

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Sakurajima.

```bash
pip install sakurajima
```

## Usage

Get you user details. If you have no idea how to do that feel free to read [our guide](https://github.com/veselysps/Sakurajima/wiki/How-to-get-username,-user-ID,-authorization-token.).

```python
from Sakurajima import Sakurajima
# Setup our instance of Sakurajima
#                    Username      User ID   Auth token
client = Sakurajima("Sakurajima", "106960", "J2ltJtj9yg1bmly4vKVZWcJe7PKlOF05")
my_anime = client.search("Somali to Mori no Kamisama")[0] # Search for "Somali to Mori no Kamisama" and get the first Anime object in the list
all_episodes = my_anime.get_episodes() # Get all the episodes from our Anime object
episode = all_episodes.get_episode_by_number(4) # Get the 4th episode from our all_episodes object, you can also use all_episodes[3]
episode.download("fullhd", "Somali - Ep. 4", True) # Download the episode in 1080p into "Somali - Ep. 4.mp4" using multiple threads

```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
