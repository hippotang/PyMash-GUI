import os
import subprocess
import tkinter as tk
import subprocess as sub
# from run_pymash import *
# note - cannot import run_pymash, it returns the error:
    # libc++abi.dylib: terminating with uncaught exception of type NSException
    #  Abort trap: 6
from pydub import AudioSegment
from pydub.playback import play
from shutil import copyfile
from tkinter import * 
from tkinter import ttk
from playsound import playsound
from tkinter.filedialog import askopenfilename

playlist_folder = 'playlist'

def format_audio_file(absolute_path):
    if absolute_path.endswith('wav'): 
        return
    if (absolute_path.endswith('mp3') or absolute_path.endswith('aiff') 
        or absolute_path.endswith('wma') or absolute_path.endswith('pcm')):
        sound = AudioSegment.from_file(absolute_path)
        os.remove(absolute_path)
        sound.export(playlist_folder + '/' + os.path.basename(absolute_path) + '.wav', format="wav")
        return

class App():
    def __init__(self,width,height):
        self.already_mashed = False
        self.playlist_folder = playlist_folder
        self.checkboxes = []
        self.checkboxvars = []
        self.checkedsongs = []
        self.playlist = os.listdir(playlist_folder)
        self.width = width
        self.height = height
        self.root = Tk()
        self.root.geometry(str(width) + 'x' + str(height)) #width*height
        self.head = Label(self.root, text="pymash")
        self.root.grid()
        self.sidebar = Frame(self.root, width = self.width/3, 
                    height = self.height, bg="#eee") 
        self.results = Frame(self.root, width = self.width/3, 
                    height = self.height, bg="#eee")
        self.feedbackmessage = Label(self.sidebar, text="- ready -")

        # head
        label = Label(self.sidebar, text="Playlist")
        label.pack(side=TOP, fill=X)
        #results
        self.scroller = Scrollbar(self.results)
        self.outputArea = Text(self.results)
        self.outputArea.place(height = (int)(self.height/2), width=(int)(self.width/3))
        self.scroller.config(command=self.outputArea.yview)
        self.outputArea.config(yscrollcommand = self.scroller.set, wrap=WORD)
        self.outputArea.pack(side=TOP)
        self.scroller.pack(side=RIGHT)
        self.results.pack(side=RIGHT,fill=Y)
        #feedback message
        self.feedbackmessage.pack(side=BOTTOM)

        i=0
        for path in self.playlist:
            if path.endswith('wav') or path.endswith('mp3'):
                v = IntVar()
                self.checkboxvars.append(v)
                self.checkboxes.append(Checkbutton(self.sidebar, text=os.path.basename(path), 
                                                        variable=v,justify=tk.LEFT, wraplength=self.width/3))
                self.checkboxes[i].pack()
                i+=1
    
    def reset_playlist(self):
        self.checkboxvars = []
        for c in self.checkboxes:
            c.destroy()
        self.checkboxes = []
        for obj in os.listdir(playlist_folder):
            if os.path.isfile(playlist_folder+'/'+obj):
                os.remove(playlist_folder+'/'+obj)
        for obj in os.listdir(playlist_folder + '/normalized'):
            if os.path.isfile(playlist_folder+'/normalized/'+obj):
                os.remove(playlist_folder+'/normalized/'+obj)
        for obj in os.listdir(playlist_folder + '/mashups'):
            if os.path.isfile(playlist_folder+'/mashups/'+obj):
                os.remove(playlist_folder+'/mashups/'+obj)
        #self.sidebar.pack()
    
    def quit(self):
        self.reset_playlist()
        self.root.destroy()
    
    def choosefile(self):
        Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
        filepath = askopenfilename() # show an "Open" dialog box and return the path to the selected file
        filename = os.path.basename(filepath)
        audio_types = ["mid", "mp3", "m4a", "ogg", "flac", "amr"]
        if filepath[-3:] in audio_types:
            copyfile(filepath, playlist_folder+'/'+filename)
            self.playlist.append(playlist_folder+'/'+filename)
            self.update(playlist_folder+'/'+filename)
            return 0
        else:
            copyfile(filepath, playlist_folder+'/'+filename)
            format_audio_file(playlist_folder+'/'+filename)
            self.update(playlist_folder+'/'+filename)

    def update(self, path):
        print(path)
        v = IntVar()
        self.checkboxvars.append(v)
        self.checkboxes.append(Checkbutton(self.sidebar, text=os.path.basename(path), 
                                            variable=v, justify=tk.LEFT, wraplength=self.width/3))
        self.checkboxes[len(self.checkboxvars)-1].pack()
        self.already_mashed = False

    def orderbyquality(self):
        print('just reading the quality file')
        if self.already_mashed:
            f = open('playlist/qualities.txt', 'r')
            contents = f.read()
            # print(contents)
            self.outputArea.insert(END,contents)
        else:
            self.feedbackmessage.config(text='mashups needed')
            

    # returns an array of filenames
    def getcheckedsongs(self):
        self.checkedsongs = []
        i = 0
        self.playlist = os.listdir(playlist_folder)
        for c in self.checkboxvars:
            if c.get():
                self.checkedsongs.append(self.playlist[i])
            i+=1
        #self.feedbackmessage.config(text=str(self.checkedsongs), wraplength=self.width/3)

    # FIX THIS (have this parse qualities.txt)
    def play_best_song(self):
        for i in os.listdir(playlist_folder+'/mashups'):
            if os.path.isfile(os.path.join(playlist_folder+'/mashups',i)) and 'best_' in i:
                song = AudioSegment.from_wav(playlist_folder+'/mashups/'+i)
                while True:
                    try:
                        play(song)
                    except KeyboardInterrupt:
                        print("Stopping playing")
                        break #to exit out of loop, back to main program
    
    def mash(self):
        if not self.already_mashed:
            self.already_mashed = True
            subprocess.call(["python", "run_pymash.py", "playlist", "WAV", "NORM", "QUAL", "PCM_16"])
            # subprocess.call(["python", "run_pymash.py", "playlist", "WAV", "NORM", "PCM_16"])
        else:
            self.feedbackmessage.config(text="already ran mashups")

if __name__ == "__main__":
    app = App(900,600) #width, height
    center = Frame(app.root, width = app.width/3, 
                    height = app.height, bg="#aff")

    #sidebar
    btn = Button(app.sidebar, text="upload files", command=app.choosefile)
    btn.pack(padx=5, pady=5, side=BOTTOM, fill=X)

    btn_reset = Button(app.sidebar, padx=5, pady=5, text="reset playlist", command=app.reset_playlist)
    btn_reset.pack(side = BOTTOM, fill=X)

    app.sidebar.pack(side=LEFT, fill=Y)

    btn_aq = Button(app.results, text="order by quality", command=app.orderbyquality)
    btn_aq.pack(padx=5, pady=5,side=BOTTOM)

    btn_play = Button(app.results, text="play best song", command=app.play_best_song)
    btn_play.pack(padx=5, pady=5, side=BOTTOM)

    btn_mash = Button(app.results, text="give me my mashups", command=app.mash)
    btn_mash.pack(padx=5, pady=5, side=BOTTOM)

    btn_exit = Button(app.results, text="exit", command=app.quit)
    btn_exit.pack(padx=5, pady=5, side=BOTTOM)

    app.root.mainloop()
    