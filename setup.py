from setuptools import setup, find_packages


setup(name='sakurajima',  
      version='0.1.4',
      license='MIT',
      author="Not Marek",
      author_email="notmarek@animex.tech",
      description="AniWatch.me API wrapper",
      long_description=open("README.md", "r").read(),
      long_description_content_type="text/markdown",
      url="https://github.com/veselysps/Sakurajima",
      packages=find_packages(),
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      python_requires='>=3.6',
 )