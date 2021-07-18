import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
from PIL import ImageTk, Image
from find_usb_mass_storage import find_removable_usb_storage

ADDRESS = 'https://www.youtube.com/playlist?list=PLirMc55Q2sfr2fwApCxY4vap0jbV9Ew0Q'

usb_devices = find_removable_usb_storage()

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
        self.label3.pack(pady=30)
        self.entry = tk.Entry(self.f2_1, font=self.efont, width=15)
        self.entry.pack()


        self.label4 = tk.Label(self.f2_2, font=self.nmfont, text='USB στικάκι', bg=self.rcolor, fg='white')
        self.label4.pack(pady=30)
        self.mbutton = tk.Menubutton(self.f2_2, text='USB stick', width=10)
        self.mbutton.pack()
        self.menu = tk.Menu(self.mbutton)
        for usb in usb_devices.keys():
            self.menu.add_command(label=usb, command=self.usb_select)
        self.mbutton.config(menu=self.menu)


    




root = tk.Tk()
DownloadApp(root)
root.mainloop()