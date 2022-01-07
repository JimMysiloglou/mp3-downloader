import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
from PIL import ImageTk, Image
from sound_process_script import sound_process, yt_downloader
import os
import shutil
from threading import Thread
import re
import configparser

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__)))

if os.name == 'nt':
    from find_usb_mass_storage_windows import find_removable_usb_storage
else:
    from find_usb_mass_storage_linux import find_removable_usb_storage


# My default download url
config = configparser.ConfigParser()
config.read(os.path.join(ROOT_DIR, 'playlist_address.ini'))
ADDRESS = config.get('DEFAULT', 'playlist_address')

# Finding downloading progress from youtube-dl with regex
pattern = re.compile(r'(\d+.\d+)%')


class YTLogger:
    """Custom logging class used in youtube_dl by yt_downloader function"""
    def __init__(self, window, message, bar):
        self.window = window
        self.message = message
        self.bar = bar

    def debug(self, msg):
        progress = pattern.search(msg)
        if progress:
            self.bar['value'] = progress.groups()[0]
        print(msg)
        self.message.set(msg)

    def warning(self, msg):
        print(msg)
        self.message.set(msg)

    def error(self, msg):
        print(msg)
        self.message.set(msg)


class Log:
    """Second logging class for youtube_dl"""
    def __init__(self, window, message) -> None:
        self.window = window
        self.message = message

    def error(self, msg):
        self.message.set(msg)
    
    def my_hook(self, d):
        if d['status'] == 'finished':
            print('Τέλος λήψεων, αρχή μετατροπής ...')
            self.message.set('Τέλος λήψεων, αρχή μετατροπής ...')


class Gui:
    """Class that creates the GUI"""

    def __init__(self, root):
        self.root = root
        self.usb_drives = find_removable_usb_storage()
        self.titlefont = font.Font(family='Arial Bold', size=27)
        self.urlfont = font.Font(family='Arial', size=18)
        self.normalfont = font.Font(family='Arial', size=15)
        self.redcolor = '#d40606'
        self.usb_variable = tk.StringVar(self.root, value='Διάλεξε USB')
        self.progressmsg = tk.StringVar(self.root)
        self.create_frames()
        self.first_frame_widgets()
        self.second_frame_widgets()
        self.third_frame_widgets()

    def create_frames(self):
        self.f1 = tk.Frame(self.root)
        self.f1.pack(fill='both', expand=True)
        self.f2 = tk.Frame(self.root)
        self.f2.pack(fill='both', expand=True)
        self.f3 = tk.Frame(self.root)
        self.f3.pack(fill='x')
        self.f2_1 = tk.Frame(self.f2, bg=self.redcolor)
        self.f2_1.pack(fill='both', expand=True, side='left')
        self.f2_2 = tk.Frame(self.f2, bg=self.redcolor)
        self.f2_2.pack(fill='both', expand=True, side='left')
        self.f2_3 = tk.Frame(self.f2, bg=self.redcolor)
        self.f2_3.pack(fill='both', expand=True, side='left')

    def first_frame_widgets(self):
        """Youtube icon and title"""
        self.image = Image.open(os.path.join(ROOT_DIR, 'youtube.png'))
        self.ytlogo = ImageTk.PhotoImage(self.image)

        self.label1 = tk.Label(self.f1, image=self.ytlogo)
        self.label1.image = self.ytlogo
        self.label1.pack(pady=25)

        self.label2 = tk.Label(self.f1, font=self.titlefont, text='Youtube MP3 Λήψεις')
        self.label2.pack()

    def second_frame_widgets(self):
        """Url entry box, usb selector and begin button"""
        self.label3 = tk.Label(self.f2_1, font=self.normalfont, text='Playlist', bg=self.redcolor, fg='white')
        self.label3.pack(pady=25)
        self.entry = tk.Entry(self.f2_1, font=self.urlfont, width=15)
        self.entry.pack()

        self.refresh_button = tk.Button(self.f2_2, font=self.normalfont, text="Ανανέωση", command=self.refresh_usb)
        self.refresh_button.pack(expand=True)

        self.label4 = tk.Label(self.f2_2, font=self.normalfont, text='USB στικάκι', bg=self.redcolor, fg='white')
        self.label4.pack(pady=10)
        self.option_menu = tk.OptionMenu(self.f2_2, self.usb_variable, *self.usb_drives.keys(),
                                         command=self.create_clear_button)
        self.option_menu.pack(expand=True)

        self.label5 = tk.Label(self.f2_3, font=self.normalfont, text='Εκκίνηση λήψεων', bg=self.redcolor, fg='white')
        self.label5.pack(pady=25)
        self.start_button = tk.Button(self.f2_3, font=self.normalfont, text="Εκκίνηση", command=self.threading)
        self.start_button.pack()

    def third_frame_widgets(self):
        """Progress Bar and message"""
        self.progressbar = ttk.Progressbar(self.f3, orient='horizontal', length=300, mode='determinate')
        self.progressbar.pack(pady=10)
        self.label6 = tk.Label(self.f3, font=self.normalfont, textvariable=self.progressmsg, width=100)
        self.label6.pack()

    def refresh_usb(self):
        """Check again if usb inserted"""
        if hasattr(self, 'clear_button'): self.clear_button.pack_forget()
        self.usb_drives = find_removable_usb_storage()
        self.usb_variable.set('Διάλεξε USB')
        menu = self.option_menu['menu']
        menu.delete(0, 'end')
        for usb in self.usb_drives.keys():
            menu.add_command(label=usb, command=lambda: [self.usb_variable.set(usb), self.create_clear_button(usb)])

    def create_clear_button(self, usb_selected):
        """Create a delete usb button if usb chosen"""
        if usb_selected != 'No usb inserted' and not hasattr(self, 'clear_button'):
            self.usb_path = self.usb_drives.get(self.usb_variable.get(), False)
            self.clear_button = tk.Button(self.f2_2, font=self.normalfont, text="Διαγραφή", command=self.clear_usb)
            self.clear_button.pack(expand=True)

    def clear_usb(self):
        """Delete all files from the chosen usb"""
        for filename in os.listdir(self.usb_path):
            file_path = os.path.join(self.usb_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        self.progressmsg.set('Διαγράφηκε')

    def threading(self):
        """Our download script runs in a different thread than the gui"""
        t1 = Thread(target=self.start_download)
        t1.start()

    def start_download(self):
        """Download script starting when we press the "Εκκίνηση" button"""

        # Getting the url on the entrybox otherwise using the default
        self.download_url = self.entry.get() or ADDRESS

        # Getting the usb drive mount path otherwise False
        self.usb_path = self.usb_drives.get(self.usb_variable.get(), False)

        # Initiate our first logger
        self.log = Log(self.f3, self.progressmsg)

        # Chosen options for youtube_dl
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
                                {
                'key': 'FFmpegMetadata'}],
            'logger': YTLogger(self.f3, self.progressmsg, self.progressbar),
            'progress_hooks': [self.log.my_hook],
            'nooverwrites': True,
            'simulate': False,
            'outtmpl': '%(title)s.%(ext)s',
        }

        # Starting download and converting to mp3
        yt_downloader(self.download_url, ydl_opts)

        # A list of our files
        files = os.listdir(os.path.join(ROOT_DIR, 'Downloads'))
        max_value = len(files)

        # Normalizing our files removing original and inform user
        for i, file in enumerate(files, 1):
            self.progressmsg.set(f'Ομαλοποιηση ήχου: {file}')
            self.progressbar['value'] = (i / max_value) * 100
            sound_process(file)
            os.remove(file)

        # Moving the files to usb drive if we inserted one
        if self.usb_path:
            normalized_files = os.listdir(os.path.join(ROOT_DIR, 'Downloads'))
            self.progressmsg.set('Μετακίνηση κομματιών')
            max_value = len(normalized_files)
            for i, file in enumerate(normalized_files, 1):
                self.progressbar['value'] = (i / max_value) * 100
                shutil.move(file, os.path.join(self.usb_path, file))
        self.progressmsg.set('Διαδικασία Ολοκληρώθηκε')


def start():
    root = tk.Tk()
    root.title('Youtube Λήψεις')
    root.geometry('750x450')
    root.resizable(False, False)
    Gui(root)
    root.mainloop()


if __name__ == "__main__":
    start()
