import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
from PIL import ImageTk, Image
from find_usb_mass_storage import find_removable_usb_storage
from music_script import mp3_downloading, normalize_song
import os
import shutil

ADDRESS = 'https://www.youtube.com/playlist?list=PLirMc55Q2sfr2fwApCxY4vap0jbV9Ew0Q'

usb_devices = find_removable_usb_storage()

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
    'simulate': False,
}

class DownloadApp():
    def __init__(self, root) -> None:
        self.root = root
        self.root.title('Youtube Λήψεις')
        self.root.geometry('750x450')
        self.root.resizable(0, 0)
        self.bigfont = font.Font(family='Arial Bold', size=27)
        self.efont = font.Font(family='Aria', size=18)
        self.nmfont = font.Font(family='Arial', size=15)
        self.rcolor = '#d40606'
        self.usb_var = tk.StringVar(self.root)
        self.usb_var.set('Διάλεξε USB')
        self.widgets()

    def widgets(self):
        # Frames
        self.f1 = tk.Frame(self.root)
        self.f1.pack(fill='both', expand=True)
        self.f2 = tk.Frame(self.root)
        self.f2.pack(fill='both', expand=True)
        self.f3 = tk.Frame(self.root)
        self.f3.pack(fill='x')
        self.f2_1 = tk.Frame(self.f2, bg=self.rcolor)
        self.f2_1.pack(fill='both', expand=True, side='left')
        self.f2_2 = tk.Frame(self.f2, bg=self.rcolor)
        self.f2_2.pack(fill='both', expand=True, side='left')
        self.f2_3 = tk.Frame(self.f2, bg=self.rcolor)
        self.f2_3.pack(fill='both', expand=True, side='left')

        # First frame
        self.image = Image.open('./youtube.png')
        self.ytlogo = ImageTk.PhotoImage(self.image)

        self.label1 = tk.Label(self.f1, image=self.ytlogo)
        self.label1.image = self.ytlogo
        self.label1.pack(pady=25)

        self.label2 = tk.Label(self.f1, font=self.bigfont, text='Youtube MP3 Λήψεις')
        self.label2.pack()

        # Second frame
        self.label3 = tk.Label(self.f2_1, font=self.nmfont, text='Playlist', bg=self.rcolor, fg='white')
        self.label3.pack(pady=25)
        self.entry = tk.Entry(self.f2_1, font=self.efont, width=15)
        self.entry.pack()

        self.label4 = tk.Label(self.f2_2, font=self.nmfont, text='USB στικάκι', bg=self.rcolor, fg='white')
        self.label4.pack(pady=25)
        self.option_menu = tk.OptionMenu(self.f2_2, self.usb_var, *usb_devices.keys())
        self.option_menu.pack()

        self.label5 = tk.Label(self.f2_3, font=self.nmfont, text='Εκκίνηση λήψεων', bg=self.rcolor, fg='white')
        self.label5.pack(pady=25)
        self.start_button = tk.Button(self.f2_3, font=self.nmfont, text="Εκκίνηση", command=self.start_download)
        self.start_button.pack()

        # Third frame


    def start_download(self):
        self.download_url = self.entry.get() if self.entry.get() else ADDRESS
        self.usb_path = usb_devices[self.usb_var.get()]
        mp3_downloading(self.download_url, ydl_opts)
        songs = os.listdir('./')
        for file in songs:
            print(file)
            normalize_song(file)
            os.remove(file)
        normalized_songs = os.listdir('./')
        for file in normalized_songs:
            print(file)
            shutil.move(file, os.path.join(self.usb_path, file))

        

        
        




root = tk.Tk()
DownloadApp(root)
root.mainloop()