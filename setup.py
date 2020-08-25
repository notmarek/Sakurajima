from setuptools import setup, find_packages


setup(
    name="sakurajima",
    version="0.2.1",
    license="MIT",
    author="NotMarek, Dhanraj Hira",
    author_email="notmarek1337@gmail.com",
    description="AniWatch.me API wrapper & downloader",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/veselysps/Sakurajima",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.23.0",
        "pycryptodome>=3.9.7",
        "m3u8>=0.6.0",
        "pathvalidate>=2.3.0"
    ],
)
