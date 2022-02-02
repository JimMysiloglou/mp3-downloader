import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import shutil
import json
import youtube_dl
from threading import Thread
import concurrent.futures
from helpers.folder_preparation import prepare_download
from helpers.ydl import YoutubeDownload
from helpers.sound_process import sound_process

# Recognize operating system
if os.name == 'nt':
    from helpers.find_usb_windows import find_removable_usb_storage
else:
    from helpers.find_usb_linux import find_removable_usb_storage

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__)))

# Load options from options.json
try:
    with open("options.json", "r") as jsonfile:
        options = json.load(jsonfile)
        ADDRESS = options['playlist_address']
        WORKERS = options['workers']
        YDL_OPTIONS = options['ydl_opts']
except FileNotFoundError:
    raise FileNotFoundError("File options.json not found!")


class Progress:
    """Second logging class for youtube_dl"""
    downloads_count = 0
    errors_count = 0

    def __init__(self, window):
        self.filename = None
        self.progressmsg = tk.StringVar(window)
        self.progress = tk.Label(window, textvariable=self.progressmsg, width=100)
        self.progress.pack()
        self.progressbar = ttk.Progressbar(window, orient='horizontal', length=300, mode='determinate')
        self.progressbar.pack()

    def debug(self, msg):
        pass
        # print('Debug: ', msg)

    def warning(self, msg):
        print('Warning: ', msg)

    def error(self, msg):
        print('Error: ', msg)
        self.progressmsg.set(f"Error: {msg}")
        Progress.errors_count += 1

    def my_hook(self, d):
        if d['status'] == 'downloading':
            # downloading info
            print(f"{d['filename']} eta: {d['_eta_str']}, percent: {d['_percent_str']}, speed: {d['_speed_str']}")
            self.progressmsg.set(f"{d['filename']:25}, eta: {d['_eta_str']}, speed: {d['_speed_str']}")

            # progress bar
            progress = float(d['_percent_str'].strip('%'))
            self.progressbar['value'] = progress

        elif d['status'] == 'finished':
            self.filename = d['filename']
            self.progressmsg.set(f"{d['filename']:25} finished downloading")
            Progress.downloads_count += 1



class Gui:
    """Class that creates the GUI"""

    def __init__(self, root):
        self.root = root
        self.usb_drives = find_removable_usb_storage()
        self.titlefont = font.Font(family='Courier New Greek', size=27)
        self.urlfont = font.Font(family='Courier New Greek', size=18)
        self.normalfont = font.Font(family='Courier New Greek', size=15)
        self.redcolor = '#d40606'
        self.usb_variable = tk.StringVar(self.root, value='Διάλεξε USB')
        self.create_frames()
        self.first_frame_widgets()
        self.second_frame_widgets()
        self.download_url = ADDRESS
        self.usb_path = None
        self.downloads_count = 0
        self.errors_count = 0

    def create_frames(self):
        self.f1 = tk.Frame(self.root)
        self.f1.pack(fill='both', expand=True)
        self.f2 = tk.Frame(self.root)
        self.f2.pack(fill='both', expand=True)
        self.f2_1 = tk.Frame(self.f2, bg=self.redcolor)
        self.f2_1.pack(fill='both', expand=True, side='left')
        self.f2_2 = tk.Frame(self.f2, bg=self.redcolor)
        self.f2_2.pack(fill='both', expand=True, side='left')
        self.f2_3 = tk.Frame(self.f2, bg=self.redcolor)
        self.f2_3.pack(fill='both', expand=True, side='left')

    def first_frame_widgets(self):
        """Play icon and title"""
        self.image = Image.open(os.path.join(ROOT_DIR, "play_icon.png"))
        self.logo = ImageTk.PhotoImage(self.image)

        self.label1 = tk.Label(self.f1, image=self.logo)
        self.label1.image = self.logo
        self.label1.pack(pady=25)

        self.label2 = tk.Label(self.f1, font=self.titlefont, text='Youtube MP3 Λήψεις')
        self.label2.pack()

    def second_frame_widgets(self):
        """Url entry box, usb selector and begin button"""
        self.label3 = tk.Label(self.f2_1, font=self.normalfont, text='Playlist', bg=self.redcolor, fg="white")
        self.label3.pack(pady=25)
        self.entry = tk.Entry(self.f2_1, font=self.urlfont, width=15)
        self.entry.pack()

        self.refresh_button = tk.Button(self.f2_2, font=self.normalfont, text="Ανανέωση", command=self.refresh_usb)
        self.refresh_button.pack(expand=True)

        self.label4 = tk.Label(self.f2_2, font=self.normalfont, text='Στικάκι USB', bg=self.redcolor, fg='white')
        self.label4.pack(pady=10)
        self.option_menu = tk.OptionMenu(self.f2_2, self.usb_variable, *self.usb_drives.keys(),
                                         command=self.create_clear_button)
        self.option_menu.pack(expand=True)

        self.label5 = tk.Label(self.f2_3, font=self.normalfont, text='Εκκίνηση λήψεων', bg=self.redcolor, fg='white')
        self.label5.pack(pady=25)
        self.start_button = tk.Button(self.f2_3, font=self.normalfont, text="Εκκίνηση", command=self.downloading)
        self.start_button.pack()

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
        print('Διαγράφηκε')


    def download_procedure(self, url):
        # create custom log
        options = YDL_OPTIONS.copy()
        log = Progress(self.info_window)
        options['progress_hooks'] = [log.my_hook]

        # start download and postprocess to mp3
        logger = log
        ydl = YoutubeDownload(url, options, logger)
        ydl.run()

        # sound processing of the file and removal of the original
        filename, _ = os.path.splitext(log.filename)
        print(f"{filename}: start sound processing")
        sound_process(os.path.join(ROOT_DIR, 'Downloads', filename+'.mp3'))
        os.remove(os.path.join(ROOT_DIR, 'Downloads', filename+'.mp3'))

        # Moving the file to usb drive if we inserted one
        if self.usb_path:
            print(f"{filename} move song to usb")
            shutil.move(os.path.join(ROOT_DIR, 'Downloads', filename+'_normalized.mp3'),
                        os.path.join(self.usb_path, filename+'_normalized.mp3'))



    def start_downloaders(self, urls):
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
            future_downloads = {executor.submit(self.download_procedure, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_downloads):
                url = future_downloads[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))
            executor.shutdown()
        self.info_window.destroy()
        self.finished_window = messagebox.showinfo("Λήψεις Ολοκληρώθηκαν", f"Downloads: {Progress.downloads_count} \nErrors: {Progress.errors_count}")




    def create_info_window(self):
        # create new window
        self.info_window = tk.Toplevel(self.root)
        self.info_window.title("Downloads")
        self.info_window.geometry("500x500")


    def downloading(self):
        """Prepare for downloading and open thread for ydl"""

        # prepare downloads folder
        prepare_download(ROOT_DIR)
        # Getting the usb drive mount path otherwise False
        self.usb_path = self.usb_drives.get(self.usb_variable.get(), False)
        # Change url address if other has been given
        if self.entry.get():
            self.download_url = self.entry.get()
        # Getting song list from playlist
        with youtube_dl.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
            songs = ydl.extract_info(self.download_url, process=False)
            print("Done, downloading list")
            song_urls = [entry["url"] for entry in songs["entries"]]
        os.chdir(os.path.join(ROOT_DIR, 'Downloads'))

        self.create_info_window()

        # loading threads for download
        thread = Thread(target=self.start_downloaders, kwargs={'urls': song_urls})
        thread.start()


def start():
    root = tk.Tk()
    root.title('Youtube Λήψεις')
    root.geometry('750x450')
    root.resizable(False, False)
    Gui(root)
    root.mainloop()

if __name__ == "__main__":
    start()