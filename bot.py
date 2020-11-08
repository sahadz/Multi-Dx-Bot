import os
from config import Config
from multidxbot import MultiDxBot


if __name__ == "__main__":
    if not os.path.exists(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)
    MultiDxBot().run()
