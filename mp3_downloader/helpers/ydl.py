import youtube_dl
import time

class YoutubeDownload:
    def __init__(self, url, ydl_opts, logger):
        self.url = url
        self.ydl_options = ydl_opts
        self.ydl_options['logger'] = logger

    def run(self):
        with youtube_dl.YoutubeDL(self.ydl_options) as ydl:
            ydl.download([self.url])



