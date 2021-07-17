from __future__ import unicode_literals
import youtube_dl
import os
from pydub import AudioSegment, effects
from pydub.utils import mediainfo

PLAYLIST = 'https://www.youtube.com/playlist?list=PLirMc55Q2sfr2fwApCxY4vap0jbV9Ew0Q'

class MyLogger:
    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    },
    {    'key': 'FFmpegMetadata'},
],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    'nooverwrites': True,
    'simulate': True,
}


with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    os.chdir('./Downloads')
    ydl.download([PLAYLIST])

songs = os.listdir('./')

def normalize(file):
    print('Normalizing: ', file)
    rawsound = AudioSegment.from_file(file)
    normalizedsound = effects.normalize(rawsound)
    name = file.rsplit('.')[0]
    return normalizedsound.export(f'{name}_normalized.mp3', bitrate='192k', tags=mediainfo(file).get('TAG', {}))

print('Begin Normalization')

for song in songs:
    normalize(song)