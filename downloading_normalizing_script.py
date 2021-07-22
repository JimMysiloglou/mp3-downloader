from __future__ import unicode_literals
import youtube_dl
import os
from pydub import AudioSegment, effects
from pydub.utils import mediainfo # Transferring tags to normalized file




def yt_downloader(url, ydl_opts):
    '''
    A function using youtube_dl to download videos given a
    playlist or video (url) and options (ydl_opts) to the 
    Downloads folder.
    '''
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        os.chdir('./Downloads')
        ydl.download([url])


def normalize_sound(file):
    '''
    A function using pydub to normalize a sound file (file)
    '''
    rawsound = AudioSegment.from_file(file)
    normalizedsound = effects.normalize(rawsound)
    name = file.rsplit('.')[0]
    return normalizedsound.export(f'{name}_normalized.mp3', bitrate='192k', tags=mediainfo(file).get('TAG', {}))
