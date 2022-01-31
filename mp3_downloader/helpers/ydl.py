import youtube_dl

class MyLogger:

    def debug(self, msg):
        pass
        #print('Debug: ', msg)

    def warning(self, msg):
        print('Warning: ', msg)

    def error(self, msg):
        print('Error: ', msg)


class YoutubeDownload:
    def __init__(self, url, ydl_opts):
        self.url = url
        self.ydl_options = ydl_opts
        self.ydl_options['logger'] = MyLogger()

    def run(self):
        with youtube_dl.YoutubeDL(self.ydl_options) as ydl:
            ydl.download([self.url])



