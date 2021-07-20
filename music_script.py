from __future__ import unicode_literals
import youtube_dl
import os
from pydub import AudioSegment, effects
from pydub.utils import mediainfo




def mp3_downloading(url, ydl_opts):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        os.chdir('./Downloads')
        ydl.download([url])


def normalize_song(file):
    rawsound = AudioSegment.from_file(file)
    normalizedsound = effects.normalize(rawsound)
    name = file.rsplit('.')[0]
    return normalizedsound.export(f'{name}_normalized.mp3', bitrate='192k', tags=mediainfo(file).get('TAG', {}))
