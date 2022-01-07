from __future__ import unicode_literals
import youtube_dl
import os
from pydub import AudioSegment, effects
from pydub.utils import mediainfo  # Transferring tags to normalized file

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__)))

def yt_downloader(url, ydl_opts):
    """
    A function using youtube_dl to download videos given a
    playlist or video (url) and options (ydl_opts) to the 
    Downloads folder.
    """

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        downloads_path = os.path.join(ROOT_DIR, 'Downloads')
        if not os.path.exists(downloads_path):
            os.makedirs(downloads_path)
        os.chdir(downloads_path)
        ydl.download([url])


def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    """
    Iterating over chunks until finding the first one with sound based on given silence_threshold
    """

    trim_ms = 0

    assert chunk_size > 0  # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms


def sound_process(file):
    """
    A function processing a sound file for normalization and silence removal
    """

    rawsound = AudioSegment.from_file(file) 

    start_trim = detect_leading_silence(rawsound)
    end_trim = detect_leading_silence(rawsound.reverse())

    duration = len(rawsound)

    normalized_sound = effects.normalize(rawsound[start_trim:duration-end_trim])

    name = file.rsplit('.')[0]
    return normalized_sound.export(f'{name}_normalized.mp3', bitrate='192k', tags=mediainfo(file).get('TAG', {}))
