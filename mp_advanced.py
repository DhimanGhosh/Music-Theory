import datetime
import pickle
import random
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter import StringVar
import os
import pygame
import re
from tkinter.ttk import Progressbar, Combobox
import sched, time
import sys
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from PIL import ImageTk, Image
import subprocess
import math
import shutil
import urllib3
from bs4 import BeautifulSoup
from abc import ABC
from tkinter import font
from urllib3.exceptions import NewConnectionError
from fractions import Fraction
from PIL import GifImagePlugin #used for animated gifs

class Playlist:
    def __init__(self):
        self.isSongPause = False
        self.isSongStopped = False
        self.VolumeLevel=1.0
        self.useMassFileEditor=False
        self.dirFilePath = None
        self.danthologyMode=False
        self.danthologyDuration=0
        self.danthologyTimer=0
        self.windowOpacity=1.0
        self.progressTime = "Ascending" #possible values: Ascending and Descending
        self.skin=0
        self.SHUFFLE = False
        self.isListOrdered = 17 #0-on songrating ; 1-sorted by name 2-sorted by name reversed; 3-random ....;
        self.validFiles = []
        self.slideImages = []
        self.slideImagesTransitionSeconds = 0
        self.usePlayerTitleTransition = True
        self.playingFileNameTransition = "separation" # values : separation, typewriting, none
        self.usingSlideShow = False
        self.slideImageIndex = 0
        self.currentSongIndex = None
        self.currentSongPosition = 0
        self.REPEAT = 1 # 1 is value for repeat all, 0 - repeat off, 2, repeat one, 3 - repeat none
        self.RESUMED=False
        self.viewModel = "COMPACT" # COMPACT value on this one will make the playList compact.
        self.playTime = 0
        self.customFont = None
        self.customElementBackground = None
        self.customLabelBackground = None
        self.customBackgroundPicture = None
        self.customFontColor = None
        self.customChangeBackgroundedLabelsColor = None
        self.userCreatedColors = []
        self.ProgressBarType = "determinate"
        self.LyricsActiveSource = LyricsOnlineSources[0] #default, all sources
        self.resetSettings = False
        self.useCrossFade = False
        self.crossFadeDuration = 10 #default value not customizable
        self.crossFadeGap = 3 #default value not customizable
        self.shufflingHistory = []
        self.playerXPos = 100 #Music player X coordinate
        self.playerYPos = 100 #Music player Y coordinate
        self.listboxNoRows = 35
        self.listboxWidth = "Auto"
        self.buttonSpacing = 50 #default value
        self.keepSongsStats = True
        self.PlaylistListenedTime = 0
        self.BornDate = datetime.datetime.now()

class Song:
    def __init__(self, filename, filepath, filesize):
        self.fileName = filename
        self.filePath = filepath
        self.fileSize = filesize
        self.Rating = 0
        self.NumberOfPlays = 0
        audio = MP3(self.filePath)
        self.sample_rate = audio.info.sample_rate
        self.channels = audio.info.channels
        self.Length = audio.info.length
        self.SongListenedTime = 0
        
        mp3 = MP3(self.filePath) # if the mp3 file has no tags, then the tags will be added to the file.
        if mp3.tags is None:
            mp3.add_tags()
            mp3.save()
        audio = EasyID3(self.filePath)
        try:
            self.Genre = audio["genre"]
        except: #enter here if you can't get the genre
            self.Genre = "Various"
        else:
            self.Genre = self.Genre[0]
        try:
            self.Artist = audio["artist"]
        except:
            self.Artist = "Various"
        else:
            self.Artist = self.Artist[0]
        try:
            self.Title = audio["title"]
        except:
            self.Title = "Various"
        else:
            self.Title = self.Title[0]
        try:
            self.Year = audio["date"]
        except:
            self.Year = "Various"
        else:
            self.Year = self.Year[0]
        try:
            self.Album = audio["album"]
        except:
            self.Album = "Various"
        else:
            self.Album = self.Album[0]
        self.startPos = 0
        self.endPos = self.Length
        self.fadein_duration = 0
        self.fadeout_duration = 0

class Window(ABC): #let this class be abstract
    def destroyEsc(self,event):
        self.destroy()

    def destroy(self):
        global dialog
        self.top.destroy()
        if type(dialog) == Mp3TagModifierTool:
           global progressViewRealTime
           progressViewRealTime = 0.8 # set back the default value for progress.
        dialog = None
        
    def take_focus(self):
        self.top.wm_attributes("-topmost", 1)
        self.top.grab_set()
    
    def focus_out(self, event):
        window.wm_attributes("-topmost", 1)
        window.grab_set()
        window.focus_force()
    
class CuttingTool(Window):
    def __init__(self, parent, fileIndex=None):
        global allButtonsFont
        global dialog
        color = OpenFileButton["bg"]  # get the color which the rest of elements is using at the moment
        self.index = play_list.currentSongIndex
        if fileIndex!=None:
            self.index = fileIndex
        if self.index != None:
            self.top = tk.Toplevel(parent, bg=color)
            self.top.protocol("WM_DELETE_WINDOW", self.destroy)
            Window_Title = "Cutting Tool"
            self.top.title(Window_Title)
            self.top.geometry("410x350+100+100")
            self.top.attributes('-alpha', play_list.windowOpacity)
            allButtonsFont = skinOptions[2][play_list.skin]
            columnOne = 10
            columnTwo = 220
            self.InfoLabelText = StringVar()
            self.InfoLabelText.set("Welcome to MP3 Cutting capability:\n\n"
                               +"Please enter Start and End value and Hit OK.\n"
                                +"This will NOT change the original file.\n\n\n")
            tk.Label(self.top, textvariable=self.InfoLabelText, fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=columnOne+30, y=10)
            tk.Label(self.top, text="Selected File: " + play_list.validFiles[self.index].fileName,
                                            fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=columnOne, y=100)
            tk.Label(self.top, text="Start Value (0 - " + str(int(play_list.validFiles[self.index].Length)) + "):",
                                            fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=columnOne, y=140)

            self.startValue = tk.Entry(self.top)
            self.startValue.place(x=columnOne, y=160)
            self.startValue.insert(tk.END, str(datetime.timedelta(seconds=int(play_list.validFiles[self.index].startPos))))
            self.startValue.bind("<Return>", self.cutItem)

            tk.Label(self.top, text="End Value (0 - " + str(int(play_list.validFiles[self.index].Length)) + "):", fg=fontColor.get(),
                                          font=allButtonsFont, bg=color).place(x=columnOne, y=182)
            self.endValue = tk.Entry(self.top)
            self.endValue.place(x=columnOne, y=202)
            self.endValue.insert(tk.END, str(datetime.timedelta(seconds=int(play_list.validFiles[self.index].endPos))))
            self.endValue.bind("<Return>", self.cutItem)
            
            self.buttonOK = tk.Button(self.top, text="Cut Song", command=self.okButtonPressed, bg=color, fg=fontColor.get(), font=allButtonsFont)
            self.buttonOK.place(x=columnOne, y=230)

            tk.Label(self.top, text="Add FadeIn: ", fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=columnTwo, y=140)
            self.FadeIn = StringVar()
            self.FadeIn.set(str(play_list.validFiles[self.index].fadein_duration))
            fadeOptions = ["5","10","15", "20"]
            self.fadeInBox = Combobox(self.top, textvariable=self.FadeIn, values=fadeOptions, state="readonly", font=allButtonsFont)
            self.fadeInBox.place(x=columnTwo, y=160)
            self.fadeInBox.bind("<<ComboboxSelected>>", self.addFadeIn)

            tk.Label(self.top, text="Add FadeOut: ", fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=columnTwo, y=182)
            self.FadeOut = StringVar()
            self.FadeOut.set(str(play_list.validFiles[self.index].fadeout_duration))
            self.fadeOutBox = Combobox(self.top, textvariable=self.FadeOut, values=fadeOptions, state="readonly", font=allButtonsFont)
            self.fadeOutBox.place(x=columnTwo, y=202)
            self.fadeOutBox.bind("<<ComboboxSelected>>", self.addFadeOut)
            self.top.bind("<Escape>", self.destroyEsc)
            self.top.bind("<Tab>", self.focus_Input)
            self.addFadeInOutAll = tk.Button(self.top, text="Add Fading to All", command=self.addFadingOnPlaylist,
                                             bg=color,
                                             fg=fontColor.get(), font=allButtonsFont)
            self.addFadeInOutAll.place(x=columnTwo, y=230)

            self.restoreButton = tk.Button(self.top, text="Restore Defaults for This Song", command=self.restoreCurrentSong, bg=color, fg=fontColor.get(), font=allButtonsFont)
            self.restoreButton.place(x=80, y=280)

            self.restoreForAllButton = tk.Button(self.top, text="Restore Defaults for All Songs",
                                           command=self.restoreAllSongs, bg=color, fg=fontColor.get(),
                                           font=allButtonsFont)
            self.restoreForAllButton.place(x=80, y=310)
            dialog = self #each instance of CuttingTool will be assigned to this variable:

    def addFadingOnPlaylist(self):
        global play_list
        message = ""
        for song in play_list.validFiles:
            if int(self.FadeIn.get()) + int(self.FadeOut.get()) > (song.endPos-song.startPos):
                message+= song.fileName + "\n"
            else:
                song.fadein_duration = int(self.FadeIn.get())
                song.fadeout_duration = int(self.FadeOut.get())
        if message!= "":
            messagebox.showinfo("Information", "Operation Done.\n\nFading was added to all Songs in the Playlist.\n\n" 
                                               +"Some songs are too short for such long fading: " + message)
        else:
            messagebox.showinfo("Information", "Operation Done.\n\nFading was added to all Songs in the Playlist.")

    def restoreCurrentSong(self):
        global play_list
        play_list.validFiles[self.index].fadein_duration = 0
        play_list.validFiles[self.index].fadeout_duration = 0
        play_list.validFiles[self.index].startPos = 0
        play_list.validFiles[self.index].endPos = play_list.validFiles[self.index].Length
        self.FadeIn.set(str(play_list.validFiles[self.index].fadein_duration))
        self.FadeOut.set(str(play_list.validFiles[self.index].fadeout_duration))
        messagebox.showinfo("Information", "Operation Done.\n\nCutting\Fading was removed from current Song.")
        textFadeIn.set("FadeIn: " + str(play_list.validFiles[self.index].fadein_duration)+"s")
        textFadeOut.set("FadeOut: " + str(play_list.validFiles[self.index].fadeout_duration)+"s")
        textEndTime.set("End Time: {:0>8}".format(str(datetime.timedelta(seconds=int(play_list.validFiles[self.index].endPos)))))
        textStartTime.set("Start Time: {:0>8}".format(str(datetime.timedelta(seconds=int(play_list.validFiles[self.index].startPos)))))
        self.endValue.delete(0, tk.END)
        self.startValue.delete(0, tk.END)
        self.endValue.insert(tk.END, str(datetime.timedelta(seconds=int(play_list.validFiles[self.index].endPos))))
        self.startValue.insert(tk.END, str(datetime.timedelta(seconds=int(play_list.validFiles[self.index].startPos))))
        
    def restoreAllSongs(self):
        global play_list
        for song in play_list.validFiles:
            song.fadein_duration = 0
            song.fadeout_duration = 0
            song.startPos = 0
            song.endPos = song.Length
        self.FadeIn.set(str(play_list.validFiles[self.index].fadein_duration))
        self.FadeOut.set(str(play_list.validFiles[self.index].fadeout_duration))
        messagebox.showinfo("Information", "Operation Done.\n\nCutting\Fading was removed for all Songs in the Playlist.")
        textFadeIn.set("FadeIn: " + str(play_list.validFiles[self.index].fadein_duration)+"s")
        textFadeOut.set("FadeOut: " + str(play_list.validFiles[self.index].fadeout_duration)+"s")
        textEndTime.set("End Time: {:0>8}".format(str(datetime.timedelta(seconds=int(play_list.validFiles[self.index].endPos)))))
        textStartTime.set("Start Time: {:0>8}".format(str(datetime.timedelta(seconds=int(play_list.validFiles[self.index].startPos)))))
        self.endValue.delete(0, tk.END)
        self.startValue.delete(0, tk.END)
        self.endValue.insert(tk.END, str(datetime.timedelta(seconds=int(play_list.validFiles[self.index].endPos))))
        self.startValue.insert(tk.END, str(datetime.timedelta(seconds=int(play_list.validFiles[self.index].startPos))))

    def take_focus(self):
        self.top.wm_attributes("-topmost", 1)
        self.top.grab_set()
        self.startValue.focus_force()

    def focus_Input(self, event):
        if self.startValue.focus_get():
            self.endValue.focus_force()
        else:
            self.startValue.focus_force()

    def addFadeIn(self, event):
        global play_list
        if self.index !=None:
            if int(self.FadeIn.get()) + int(self.FadeOut.get()) > (play_list.validFiles[self.index].endPos-play_list.validFiles[self.index].startPos):
                messagebox.showinfo("Information", "Song PlayTime is too short for these values.")
            else:
                play_list.validFiles[self.index].fadein_duration = int(self.FadeIn.get())
            textFadeIn.set("FadeIn: " + str(play_list.validFiles[self.index].fadein_duration)+"s")
        showCurrentSongInList() #select/highlist the current song in the listbox

    def addFadeOut(self, event):
        global play_list
        if self.index!= None:
            if int(self.FadeIn.get()) + int(self.FadeOut.get()) > (play_list.validFiles[self.index].endPos-play_list.validFiles[self.index].startPos):
                messagebox.showinfo("Information", "Song PlayTime is too short for these values.")
            else:
                play_list.validFiles[self.index].fadeout_duration = int(self.FadeOut.get())
            textFadeOut.set("FadeOut: " + str(play_list.validFiles[self.index].fadeout_duration)+"s")
        showCurrentSongInList() #select/highlist the current song in the listbox

    def cutItem(self, event):
        self.okButtonPressed()

    def okButtonPressed(self):
        global dialog
        if self.startValue.get()!="" and self.index!=None:
            st_value = computeTimeToSeconds(self.startValue.get()) #let assume user entered a value in time format.
            if st_value < 0:
                try:
                    st_value = float(self.startValue.get())
                except: 
                    messagebox.showinfo("Information", "You have entered and invalid START value.\nCutting was aborted.")
                else:
                    if self.endValue.get() != "":
                        try:
                            ed_value = float(self.endValue.get())
                        except: 
                            pass #don't say anything, the user will bey informed about this mistake in the next block
                        else:
                            if st_value > ed_value:
                                #interchange values
                                aux = st_value
                                st_value = ed_value
                                ed_value = aux
            if st_value >= 0 and st_value < play_list.validFiles[self.index].Length:
                play_list.validFiles[self.index].startPos = st_value
                startPos = int(play_list.validFiles[self.index].startPos)
                textStartTime.set("Start Time: {:0>8}".format(str(datetime.timedelta(seconds=startPos))))
            else:
                messagebox.showinfo("Information", "Start Value is out of range.\nThe START was kept the same.")
        if self.endValue.get() != "" and self.index!=None:
            ed_value = computeTimeToSeconds(self.endValue.get()) #let assume user entered a value in time format.
            if ed_value < 0:
                try:
                    ed_value = float(self.endValue.get())
                except: 
                    messagebox.showinfo("Information", "You have entered and invalid END value.\nCutting was aborted.")
                else:
                    if self.startValue.get() !="":
                        try:
                            st_value = float(self.startValue.get())
                        except: 
                            pass #don't say anything, the user was already informed about this mistake.
                        else:
                            if st_value > ed_value:
                                #interchange values
                                aux = st_value
                                st_value = ed_value
                                ed_value = aux
            if ed_value > 0 and ed_value <= play_list.validFiles[self.index].Length:
                play_list.validFiles[self.index].endPos = ed_value
                endPos = int(play_list.validFiles[self.index].endPos)
                textEndTime.set("End Time: {:0>8}".format(str(datetime.timedelta(seconds=endPos))))
            else:
                messagebox.showinfo("Information", "End Value is out of range.\nThe END was kept the same.")
        if (self.startValue.get()=="" and self.endValue.get() == ""):
            messagebox.showinfo("Information", "You didn't entered any value, so the song was left untouched.")

class SearchTool(Window):
    def __init__(self, parent):
        global allButtonsFont
        global dialog
        self.index = play_list.currentSongIndex
        color = OpenFileButton["bg"]  # get the color which the rest of elements is using at the moment
        self.top = tk.Toplevel(parent, bg=color)
        Window_Title = "Search Tool"
        self.top.title(Window_Title)
        self.top.geometry("300x180+100+100")
        self.top.protocol("WM_DELETE_WINDOW", self.closeDestroy)
        self.top.attributes('-alpha', play_list.windowOpacity)
        allButtonsFont = skinOptions[2][play_list.skin]
        InfoLabelText = StringVar()
        InfoLabelText.set("Search for song: \n")
        tk.Label(self.top, textvariable=InfoLabelText, fg=fontColor.get(), font=allButtonsFont, bg=color).pack()
        tk.Label(self.top, text="Value: ", fg=fontColor.get(), font=allButtonsFont, bg=color).pack()
        self.searchValue = tk.Entry(self.top)

        #this is used for normal search
        self.searchValue.bind("<Return>", self.showResults)
        
        #these are used for instant search, but require multi-processing/threading:
        #self.searchValue.bind("<Key>", self.showResultsOnSpace) 

        self.top.bind("<Key>", self.focus_Input)
        self.top.bind("<Tab>", self.focus_out)
        self.searchValue.bind("<Escape>", self.destroyEsc)
        self.searchValue.bind("<Shift_R>", self.playPreviousSearch)
        self.searchValue.bind("<Control_R>", self.playNextSearch)
        self.top.bind("<Escape>", self.destroyEsc)
        self.searchValue.pack(padx=5)
        ForwardButton = tk.Button(self.top, text="Forward", command= lambda:self.playNextSearch("<Return>"), fg=fontColor.get(), font=allButtonsFont,
                                bg=color)
        ForwardButton.pack(pady=10)
        BackwardButton = tk.Button(self.top, text="Backward", command=lambda:self.playPreviousSearch("<Shift_R>"), fg=fontColor.get(), font=allButtonsFont,
                                bg=color)
        BackwardButton.pack()
        dialog = self

    def focus_Input(self,event):
        self.top.wm_attributes("-topmost", 1)
        self.searchValue.focus_force()

    def showResultsOnSpace(self, event):
        if event.char == " ":
            self.showResults(event)

    def showResults(self, event):
        global listBox_Song_selected_index
        if len(self.searchValue.get()) > 0:
            self.index=None
            listbox.delete(0, tk.END)
            value = self.searchValue.get().lower()
            for element in play_list.validFiles:
                if value in element.fileName.lower():
                    listbox.insert(tk.END, str(play_list.validFiles.index(element)) + ". " + element.fileName)
                    window.update()
        else:
            displayElementsOnPlaylist()
            self.index=play_list.currentSongIndex

    def playPreviousSearch(self, event):
        global play_list
        global listBox_Song_selected_index
        elements = listbox.get(0, tk.END)
        if self.index == None:
            self.index = len(elements) - 1
        elif self.index - 1 >= 0:
            self.index -= 1
        else:
            self.index = len(elements)-1
        real_index = elements[self.index]
        real_index = real_index.split(". ")
        real_index = real_index[0]
        listBox_Song_selected_index = self.index
        listbox.see(listBox_Song_selected_index)  # Makes sure the given list index is visible. You can use an integer index,
        listbox.selection_clear(0, tk.END)  # clear existing selection
        listbox.select_set(listBox_Song_selected_index)
        play_list.currentSongIndex = int(real_index)
        if play_list.danthologyMode == False:
            play_list.currentSongPosition = 0
        play_music()

    def playNextSearch(self, event):
        global play_list
        global listBox_Song_selected_index
        elements = listbox.get(0,tk.END)
        if self.index == None:
            self.index = 0
        elif self.index + 1 < len(elements):
            self.index += 1
        else:
            self.index = 0
        real_index = elements[self.index]
        real_index = real_index.split(". ")
        real_index = real_index[0]
        listBox_Song_selected_index = self.index
        listbox.see(listBox_Song_selected_index)  # Makes sure the given list index is visible. You can use an integer index,
        listbox.selection_clear(0, tk.END)  # clear existing selection
        listbox.select_set(listBox_Song_selected_index)
        play_list.currentSongIndex = int(real_index)
        if play_list.danthologyMode == False:
            play_list.currentSongPosition = 0
        play_music()
    
    def destroyEsc(self,event):
        self.closeDestroy()
    
    def closeDestroy(self):
        global dialog
        global listBox_Song_selected_index
        self.top.destroy()
        dialog = None
        displayElementsOnPlaylist()
        showCurrentSongInList()

    def take_focus(self):
        self.top.wm_attributes("-topmost", 1)
        self.top.grab_set()
        self.searchValue.focus_force()

class Slideshow(Window):
    #static variables
    timer = 0
    seconds = None
    slide_image = None
    slideshow = None
    top=None
    Window_Title=None #can be used as a reference to check if window is opened

    def __init__(self):
        global allButtonsFont
        color = OpenFileButton["bg"]  # get the color which the rest of elements is using at the moment
        Slideshow.top = tk.Toplevel(window, bg=color)
        Slideshow.top.protocol("WM_DELETE_WINDOW", self.destroy)
        if type(allButtonsFont) == StringVar:
            allButtonsFont = allButtonsFont.get()
        Slideshow.Window_Title = "Slideshow"
        Slideshow.top.title(Slideshow.Window_Title)
        Slideshow.top.geometry("300x300+10+10")
        Slideshow.top.attributes('-alpha', play_list.windowOpacity)
        Slideshow.seconds = StringVar()
        if play_list.slideImagesTransitionSeconds != "0":
            Slideshow.seconds.set(play_list.slideImagesTransitionSeconds)
        else:
            Slideshow.seconds.set("1")
        durationOptions = [1,2,3,4,5,10,15,30,60]

        self.infoText = StringVar()
        self.infoText.set("Welcome to Slideshow!\n\n"+
                          "Please setup your slideshow before\n" +
                          "proceed or hit Continue Button\n"+
                          "(if available) to resume.\n\n" +
                          "Number of Seconds on Transition:")

        self.InfoLabel = tk.Label(Slideshow.top, textvariable=self.infoText, fg=fontColor.get(), font=allButtonsFont,
                                  bg=color)
        self.InfoLabel.pack()

        self.imageDuration = Combobox(Slideshow.top, textvariable=Slideshow.seconds, values=durationOptions, state="readonly", font=allButtonsFont)
        self.imageDuration.pack(pady=5)
        self.imageDuration.bind("<<ComboboxSelected>>", self.time_set)
        self.loadImagesButton = tk.Button(Slideshow.top, text="Load Images",
                                                 command=self.loadImages, bg=color, fg=fontColor.get(),
                                                 font=allButtonsFont)
        self.loadImagesButton.pack(pady=10)
        self.clearImages = tk.Button(Slideshow.top, text="Clear Slideshow",
                                                 command=self.clearSlideshow, bg=color, fg=fontColor.get(),
                                                 font=allButtonsFont)
        self.clearImages.pack()
        self.startSlideshowButtonText = StringVar()
        if int(self.seconds.get()) > 0 and len(play_list.slideImages) > 0:
            self.startSlideshowButtonText.set("Continue")
        else:
            self.startSlideshowButtonText.set("Start")

        self.startSlideshow = tk.Button(Slideshow.top, textvariable = self.startSlideshowButtonText,
                                                 command=self.start, bg=color, fg=fontColor.get(),
                                                 font=allButtonsFont)
        self.startSlideshow.pack(pady=10)
        self.numberOfImages = StringVar()
        self.numberOfImages.set("Number of Images: " + str(len(play_list.slideImages)))
        self.labelNumberOfImages = tk.Label(Slideshow.top, textvariable=self.numberOfImages, fg=fontColor.get(), font=allButtonsFont,
                                  bg=color)
        self.labelNumberOfImages.pack()
        Slideshow.top.bind("<Escape>", self.destroyEsc)
        Slideshow.top.bind("<Tab>", self.focus_out)

    def loadImages(self):
        global play_list
        slidePictures = filedialog.askopenfilenames(initialdir="/", title="Please select one or more files", filetypes=(
        ("jpg files", "*.jpg"), ("png files", "*.png"),("gif files", "*.gif"), ("jpeg files", "*.jpeg"),("all files", "*.*")))
        play_list.slideImages += list(slidePictures)
        if len(play_list.slideImages) == 0:
            messagebox.showinfo("Information", "Slideshow is empty. No valid files were found. Please load only .jpg, .jpeg, .png, or .gif files.")
        self.numberOfImages.set("Number of Images: " + str(len(play_list.slideImages)))

    def destroyEsc(self,event):
        self.destroy()

    def time_set(self,event):
        global play_list
        play_list.slideImagesTransitionSeconds = Slideshow.seconds.get()
        showCurrentSongInList() #select/highlight the current song in the listbox

    def clearSlideshow(self):
        play_list.slideImages.clear()
        Slideshow.seconds.set("1")
        self.startSlideshowButtonText.set("Start")
        self.numberOfImages.set("Number of Images: " + str(len(play_list.slideImages)))

    def destroy(self):
        global play_list
        self.top.destroy()
        play_list.usingSlideShow = False
        Slideshow.timer = 0
        Slideshow.seconds = None
        Slideshow.slide_image = None
        Slideshow.slideshow = None
        Slideshow.top = None
        Slideshow.Window_Title = None

    @staticmethod
    def take_focus():
        Slideshow.top.wm_attributes("-topmost", 1)
        Slideshow.top.grab_set()
        Slideshow.top.focus_force()

    @staticmethod
    def countSeconds():
        global play_list
        if (time.time() - Slideshow.timer) >= int(Slideshow.seconds.get()):
            if play_list.slideImageIndex+1 < len(play_list.slideImages):
                play_list.slideImageIndex+=1
            else:
                play_list.slideImageIndex = 0
            Slideshow.start()
        if Slideshow.slide_image.width() != Slideshow.top.winfo_width() or Slideshow.slide_image.height()!= Slideshow.top.winfo_height(): #this means window was resized()
            Slideshow.start() #this will redraw the image with the new size

    @staticmethod
    def start():
        global play_list
        Slideshow.timer = time.time()
        play_list.usingSlideShow = True
        if len(play_list.slideImages) > 0:
            Slideshow.slide_image = ImageTk.PhotoImage(Image.open(play_list.slideImages[play_list.slideImageIndex]).resize((Slideshow.top.winfo_width(), Slideshow.top.winfo_height()))) # open all kind of images like this
            Slideshow.slideshow = tk.Label(Slideshow.top, image=Slideshow.slide_image)
            Slideshow.slideshow.pack(fill="both")
            Slideshow.slideshow.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            messagebox.showinfo("Information",
                                "Slideshow is empty. No valid files were found. Please load only .jpg, .jpeg or .gif files.")

class SleepingTool(Window):

    def __init__(self, parent):
        global allButtonsFont
        global dialog
        color = OpenFileButton["bg"]  # get the color which the rest of elements is using at the moment
        self.top = tk.Toplevel(parent, bg=color)
        self.top.protocol("WM_DELETE_WINDOW", self.destroy)
        Window_Title = "Sleeping Tool"
        self.top.title(Window_Title)
        self.top.geometry("300x230+100+100")
        self.top.attributes('-alpha', play_list.windowOpacity)
        if type(allButtonsFont) == StringVar:
            allButtonsFont = allButtonsFont.get()
        self.wakeUpScheduler = None
        self.sleepTimer = 0;
        self.sleepTime = 0;
        self.wakeUpTimer = 0;
        self.wakeUpTime = 0;
        self.sleepingScheduler = None

        InfoLabelText = StringVar()
        InfoLabelText.set("Enter the time interval: \n")
        tk.Label(self.top , textvariable=InfoLabelText, fg=fontColor.get(), font=allButtonsFont, bg=color).pack()
        tk.Label(self.top , text="Timer Value: ", fg=fontColor.get(), font=allButtonsFont, bg=color).pack()

        self.timeInterval = tk.Entry(self.top)
        self.timeInterval.pack(padx=5)
        SleepButton = tk.Button(self.top , text="Set Sleep Timer", command=self.sleeping, fg=fontColor.get(), font=allButtonsFont, bg=color)
        SleepButton.pack(pady=5)

        wakeUpButton = tk.Button(self.top, text="Set WakeUp Timer", command=self.wakeUp, fg=fontColor.get(), font=allButtonsFont,
                                bg=color)
        wakeUpButton.pack(pady=5)

        self.top.bind("<Escape>", self.destroyEsc)
        self.top.bind("<Tab>", self.focus_Input)
        dialog = self

    def eventSleeping(self, event):
        self.sleeping()

    def focus_Input(self, event):
        self.top.wm_attributes("-topmost", 1)
        self.timeInterval.focus_force()

    def wakeUp(self):
        global dialog
        if self.timeInterval.get() != "":
            self.wakeUpTime = computeTimeToSeconds(self.timeInterval.get() )#let assume user entered a value in time format.
            if self.wakeUpTime > 0:
                self.sleepTime=0 #if it was supposed to sleep, overwrite that.
                self.sleepingScheduler=None #if it was supposed to sleep, overwrite that.
                textFallAsleep.set("Fall Asleep: Never") #if it was supposed to sleep, overwrite that.
                self.wakeUpTimer = time.time()
                self.wakeUpScheduler = sched.scheduler(time.time, time.sleep)
                self.wakeUpScheduler.enter(1, 1, lambda : self.whenToWakeUp())
                self.wakeUpScheduler.run()
            else: #maybe user entered only seconds
                try:
                    self.wakeUpTime = int(self.timeInterval.get())
                except Exception as exp:
                    messagebox.showinfo("Information", "An invalid value was entered.")
                else:
                    self.sleepTime=0 #if it was supposed to sleep, overwrite that.
                    self.sleepingScheduler=None #if it was supposed to sleep, overwrite that.
                    textFallAsleep.set("Fall Asleep: Never") #if it was supposed to sleep, overwrite that.
                    self.wakeUpTimer = time.time()
                    self.wakeUpScheduler = sched.scheduler(time.time, time.sleep)
                    self.wakeUpScheduler.enter(1, 1, lambda : self.whenToWakeUp())
                    self.wakeUpScheduler.run()
            self.top.destroy()
            dialog = None

    def take_focus(self):
        self.top.wm_attributes("-topmost", 1)
        self.top.grab_set()
        self.timeInterval.focus_force()
    
    def sleeping(self):
        global dialog
        if self.timeInterval.get() != "":
            self.sleepTime = computeTimeToSeconds(self.timeInterval.get()) #let assume user entered a value in time format.
            if self.sleepTime > 0:
                self.wakeUpTime = 0 #if it was supposed to wake up, overwrite that
                self.wakeUpScheduler=None #if it was supposed to wake up, overwrite that
                textWakeUp.set("Wake Up: Never") #if it was supposed to wake up, overwrite that
                self.sleepTimer = time.time()
                self.sleepingScheduler = sched.scheduler(time.time, time.sleep)
                self.sleepingScheduler.enter(1, 1,  lambda : self.whenToSleep())
                self.sleepingScheduler.run()
                textWakeUp.set("Wake Up: Never")
            else: #maybe user entered only seconds
                try:
                    self.sleepTime = int(self.timeInterval.get())
                except Exception as exp:
                    messagebox.showinfo("Information", "An invalid value was entered.")
                else:
                    self.wakeUpTime = 0 #if it was supposed to wake up, overwrite that
                    self.wakeUpScheduler=None #if it was supposed to wake up, overwrite that
                    textWakeUp.set("Wake Up: Never") #if it was supposed to wake up, overwrite that
                    self.sleepTimer = time.time()
                    self.sleepingScheduler = sched.scheduler(time.time, time.sleep)
                    self.sleepingScheduler.enter(1, 1,  lambda : self.whenToSleep())
                    self.sleepingScheduler.run()
                    textWakeUp.set("Wake Up: Never")
            self.top.destroy()
            dialog = None

    def whenToSleep(self):
        secondsLeft = int(self.sleepTime - (time.time() - self.sleepTimer))
        textFallAsleep.set("Fall Asleep: {:0>8}" .format(str(datetime.timedelta(seconds=secondsLeft))))
        if secondsLeft<=0:
            pause_music()
            self.sleepTime=0
            self.sleepingScheduler = None
            textFallAsleep.set("Fall Asleep: Never")
        else:
            window.update()
            self.sleepingScheduler.enter(1, 1, lambda : self.whenToSleep())

    def whenToWakeUp(self):
        global play_list
        secondsLeft = int(self.wakeUpTime - (time.time() - self.wakeUpTimer))
        textWakeUp.set("Wake Up: {:0>8}".format(str(datetime.timedelta(seconds=secondsLeft))))
        if secondsLeft <= 0:
            self.wakeUpTime = 0
            self.wakeUpScheduler=None
            play_list.VolumeLevel = 1.0
            VolumeScale.set(play_list.VolumeLevel * 100)
            textWakeUp.set("Wake Up: Never")
            play_music()
        else:
            window.update()
            self.wakeUpScheduler.enter(1, 1, lambda : self.whenToWakeUp())

class Customize(Window):
    def __init__(self, parent):
        global allButtonsFont
        global dialog
        global play_list
        color = OpenFileButton["bg"] # get the color which the rest of elements is using at the moment
        self.top = tk.Toplevel(parent, bg=color)
        self.top.protocol("WM_DELETE_WINDOW", self.destroy)
        Window_Title = "Customize"
        self.top.title(Window_Title)
        self.top.geometry("680x590+100+100")
        self.top.attributes('-alpha', play_list.windowOpacity)
        columnOne = 10
        columnTwo = 250
        columnThree = 490
        if type(allButtonsFont) == StringVar:
            allButtonsFont = allButtonsFont.get()
        self.InfoLabelText = StringVar()
        self.InfoLabelText.set("Welcome to Customize capability:\n\n"
                                +"Here you can customize your player appearance\n"
                                 +"in any way you like.\n")
        tk.Label(self.top, textvariable=self.InfoLabelText, fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=180, y=5)
        
        self.labelFontColor = tk.Label(self.top, text="Button&Label Color: ", fg=fontColor.get(), font=allButtonsFont, bg=color)
        self.labelFontColor.place(x=columnOne, y=80)

        self.colorBox = Combobox(self.top, textvariable=SkinColor, values=custom_color_list, state="readonly", font=allButtonsFont)
        self.colorBox.place(x=columnOne, y=102)
        self.colorBox.bind("<<ComboboxSelected>>", changingBackgroundElementColor)

        tk.Label(self.top, text="Font: ", fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=columnOne, y=124)
        
        aux = allButtonsFont
        allButtonsFont = StringVar() #making this string variable.
        allButtonsFont.set(aux)
        self.fontBox = Combobox(self.top, textvariable=allButtonsFont, values=custom_font_list, state="readonly", font=allButtonsFont.get())
        self.fontBox.place(x=columnOne, y=146)
        self.fontBox.bind("<<ComboboxSelected>>", customFontChange)

        tk.Label(self.top, text="Label Background: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=10, y=168)
        self.labelColorBox = Combobox(self.top, textvariable=labelBackground, values=custom_color_list, state="readonly", font=allButtonsFont.get())
        self.labelColorBox.place(x=columnOne, y=190)
        self.labelColorBox.bind("<<ComboboxSelected>>", changingLabelBackgroundColor)

        tk.Label(self.top, text="Font Color: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=columnOne, y=212)
        self.FontMainColorBox = Combobox(self.top, textvariable=fontColor, values=custom_color_list, state="readonly", font=allButtonsFont.get())
        self.FontMainColorBox.place(x=columnOne, y=234)
        self.FontMainColorBox.bind("<<ComboboxSelected>>", changingFontColor)

        tk.Label(self.top, text="Playing Label Transition: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=columnOne, y=256)
        self.FontTransitionText = StringVar()
        self.FontTransitionText.set(play_list.playingFileNameTransition)
        self.FontTransitionBox = Combobox(self.top, textvariable=self.FontTransitionText, values=["none", "separation", "typewriting"], \
                                            state="readonly", font=allButtonsFont.get())
        self.FontTransitionBox.place(x=columnOne, y=278)
        self.FontTransitionBox.bind("<<ComboboxSelected>>", self.changeFileNameTransition)

        tk.Label(self.top, text="Color Picker Result Usage: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=columnOne, y=300)
        self.textColorPickerUsage = StringVar()
        self.textColorPickerUsage.set("No Usage")
        self.ColorPickerUsage = Combobox(self.top, textvariable=self.textColorPickerUsage, font=allButtonsFont.get(),
                                         values=["No Usage", "Button&Label Color", "Label Background", "Font Color"], state="readonly")
        self.ColorPickerUsage.place(x=columnOne, y=322)
        self.ColorPickerUsage.bind("<<ComboboxSelected>>", self.useColorPicked)
        
        tk.Label(self.top, text="ProgressBar Type: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=columnOne, y=344)
        self.textProgressBarType = StringVar()
        self.textProgressBarType.set(play_list.ProgressBarType)
        self.ProgressBarTypeBox = Combobox(self.top, textvariable=self.textProgressBarType, state="readonly",
                                         values=["determinate", "indeterminate"], font=allButtonsFont.get())
        self.ProgressBarTypeBox.place(x=columnOne, y=366)
        self.ProgressBarTypeBox.bind("<<ComboboxSelected>>", self.changeProgressBar)

        tk.Label(self.top, text="Playlist Max. Rows: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(
            x=columnOne, y=388)
        self.textPlaylistRows = StringVar()
        self.textPlaylistRows.set(str(play_list.listboxNoRows))
        self.PlaylistNoRowsBox = Combobox(self.top, textvariable=self.textPlaylistRows, state="readonly", font=allButtonsFont.get(),
                                           values=["22","23","24","25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35"])
        self.PlaylistNoRowsBox.place(x=columnOne, y=410)
        self.PlaylistNoRowsBox.bind("<<ComboboxSelected>>", self.changePlaylistHeight)

        self.TitleTransitionButtonText = StringVar()
        if play_list.usePlayerTitleTransition == True:
            self.TitleTransitionButtonText.set("Title Transition ON")
        else:
            self.TitleTransitionButtonText.set("Title Transition OFF")
        self.TitleTransition = tk.Button(self.top, textvariable=self.TitleTransitionButtonText, command=self.changeTitleTransition, bg=color, fg=fontColor.get(),
                                        font=allButtonsFont.get())
        self.TitleTransition.place(x=columnTwo, y=80)

        tk.Label(self.top, text="Color Bg Labels: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=columnTwo, y=110)
        self.colorBgLabels = tk.IntVar()
        if labelPlaying["fg"] == OpenFileButton["fg"]:
            self.colorBgLabels.set(1)
        else:
            self.colorBgLabels.set(0)
        self.RbFalse = tk.Radiobutton(self.top, text="False", variable=self.colorBgLabels, value=0, width=5, bg=color,
                            command=lambda: changingBackgroundedLabelsColor(self.colorBgLabels,0), fg=fontColor.get(), selectcolor="black", font=allButtonsFont.get())
        self.RbTrue = tk.Radiobutton(self.top, text="True", variable=self.colorBgLabels, value=1, width=5, bg=color,
                            command=lambda: changingBackgroundedLabelsColor(self.colorBgLabels,0), fg=fontColor.get(), selectcolor="black", font=allButtonsFont.get())
        self.RbFalse.place(x=columnTwo, y=130)
        self.RbTrue.place(x=columnTwo+80, y=130)

        self.browseBackgroundPicture = tk.Button(self.top, text="Load Background", command=self.browse_background_picture, bg=color, fg=fontColor.get(),
                                                 font=allButtonsFont.get())
        self.browseBackgroundPicture.place(x=columnTwo, y=160)
        self.startSlideshow = tk.Button(self.top, text="Start Slideshow", command=showSlideshowWindow, bg=color, fg=fontColor.get(), font=allButtonsFont.get())
        self.startSlideshow.place(x=columnTwo, y=190)

        tk.Label(self.top, text="Window Opacity: ", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color).place(x=columnTwo, y=220)
        self.WindowOpacityText = StringVar()
        self.WindowOpacityText.set(play_list.windowOpacity)
        self.WindowOpacityBox = Combobox(self.top, textvariable=self.WindowOpacityText, state="readonly", font=allButtonsFont.get(),
                                          values=["1.0", "0.9", "0.8", "0.7", "0.6", "0.5"])
        self.WindowOpacityBox.place(x=columnTwo, y=240)
        self.WindowOpacityBox.bind("<<ComboboxSelected>>", self.changeWindowOpacity)

        tk.Label(self.top, text="Progress Time: ", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color).place(x=columnTwo, y=262)

        self.ProgressTimeText = StringVar()
        if play_list.progressTime == "Ascending":
            self.ProgressTimeText.set("Playing Time")
        else:
            self.ProgressTimeText.set("Remaining Time")
        self.ProgressTimeBox = Combobox(self.top, textvariable=self.ProgressTimeText, state="readonly", font=allButtonsFont.get(),
                                         values=["Playing Time", "Remaining Time"])
        self.ProgressTimeBox.place(x=columnTwo, y=284)
        self.ProgressTimeBox.bind("<<ComboboxSelected>>", self.changeProgressTime)

        tk.Label(self.top, text="Lyrics Active Source: ", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color).place(x=columnTwo, y=306)
        self.LyricsSourcesText = StringVar()
        self.LyricsSourcesText.set(play_list.LyricsActiveSource)
        self.LyricsSourcesBox = Combobox(self.top, textvariable=self.LyricsSourcesText,  state="readonly", font=allButtonsFont.get(),
                                         values=LyricsOnlineSources)
        self.LyricsSourcesBox.place(x=columnTwo, y=328)
        self.LyricsSourcesBox.bind("<<ComboboxSelected>>", self.changeActiveLyricsSource)


        tk.Label(self.top, text="Playlist Width: ", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color).place(x=columnTwo, y=350)
        self.textPlaylistWidth = StringVar()
        self.textPlaylistWidth.set(play_list.listboxWidth)
        self.PlaylistWidthBox = Combobox(self.top, textvariable=self.textPlaylistWidth, state="readonly", font=allButtonsFont.get(),
                                         values=["Auto", "65", "70", "75", "80", "85", "90", "95"])
        self.PlaylistWidthBox.place(x=columnTwo, y=372)
        self.PlaylistWidthBox.bind("<<ComboboxSelected>>", self.changePlaylistWidth)

        RestoreDefaultsButton = tk.Button(self.top, text="Restore Defaults", command=self.restoreDefaults, fg=fontColor.get(), font=allButtonsFont.get(),
                                bg=color)
        RestoreDefaultsButton.place(x=columnTwo, y=404)

        self.textDanthologyMode = StringVar()

        if play_list.danthologyMode == True:
            self.textDanthologyMode.set("Danthology Mode ON")
        else:
            self.textDanthologyMode.set("Danthology Mode OFF")
        self.danthologyMode = tk.Button(self.top, textvariable=self.textDanthologyMode, command=self.changeDanthologyMode, bg=color, fg=fontColor.get(),
                                        font=allButtonsFont.get())
        self.danthologyMode.place(x=columnThree, y=80)
        self.DanthologyInterval = StringVar()
        self.DanthologyInterval.set(play_list.danthologyDuration)
        tk.Label(self.top, text="Danthology Duration: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=columnThree, y=110)
        self.DanthologySetBox = Combobox(self.top, textvariable=self.DanthologyInterval, values=["0", "10", "30", "60", "90"], state="readonly", font=allButtonsFont.get())
        self.DanthologySetBox.place(x=columnThree, y=130)
        self.DanthologySetBox.bind("<<ComboboxSelected>>", self.changeDanthologyDuration)

        tk.Label(self.top, text="Color Picker: ", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color).place(x=columnThree, y=152)

        self.scaleRed = tk.Scale(self.top, from_=0, to=255, orient=tk.HORIZONTAL, fg=fontColor.get(), font=allButtonsFont.get(), bg=color, length=140, \
                                 sliderlength=10, width=10, bd=1, label="Red:")
        self.scaleRed.place(x=columnThree, y=172)
        self.scaleRed.bind("<ButtonRelease-1>", self.composeColor)

        self.scaleGreen = tk.Scale(self.top, from_=0, to=255, orient=tk.HORIZONTAL, fg=fontColor.get(), length=140, \
                            font=allButtonsFont.get(), bg=color, sliderlength=10, width=10, bd=1, label="Green:")
        self.scaleGreen.place(x=columnThree, y=232)
        self.scaleGreen.bind("<ButtonRelease-1>", self.composeColor)

        self.scaleBlue = tk.Scale(self.top, from_=0, to=255, orient=tk.HORIZONTAL, fg=fontColor.get(),  length=140, \
                            font=allButtonsFont.get(), bg=color, sliderlength=10, width=10, bd=1, label="Blue:")
        self.scaleBlue.place(x=columnThree, y=292)
        self.scaleBlue.bind("<ButtonRelease-1>", self.composeColor)

        self.ColorPickerResult = tk.Label(self.top, text="     Result       ", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg="black")
        self.ColorPickerResult.place(x=columnThree, y=352)

        self.textButtonSpace = StringVar()
        self.textButtonSpace.set(str(play_list.buttonSpacing))
        tk.Label(self.top, text="Element Spacing: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(
            x=columnThree, y=375)
        self.buttonSpacingBox = Combobox(self.top, textvariable=self.textButtonSpace,
                                         values=["15","20", "25", "30", "35", "40", "45", "50", "55", "60"], state="readonly",
                                         font=allButtonsFont.get())
        self.buttonSpacingBox.place(x=columnThree, y=397)
        self.buttonSpacingBox.bind("<<ComboboxSelected>>", self.changeButtonSpacing)
        
        self.MaintainSongsStats = tk.IntVar()
        self.MaintainSongsStats.set(int(play_list.keepSongsStats))

        tk.Checkbutton(self.top, text="Maintain Songs Stats on All Playlists.", fg=fontColor.get(), font=allButtonsFont.get(),
                       bg=color, variable=self.MaintainSongsStats, command=self.enableDisableSongsStatsKeeping,
                       selectcolor="black").place(x=200, y=440)
        
        self.MassFileEditorUsage = tk.IntVar()
        self.MassFileEditorUsage.set(play_list.useMassFileEditor)
        
        tk.Checkbutton(self.top, text="Use mass file editor capabilities.", fg=fontColor.get(), font=allButtonsFont.get(),
                       bg=color, variable=self.MassFileEditorUsage, command=self.enableDisableMassFileEditor,
                       selectcolor="black").place(x=200, y=460)
		
        self.resetSettingsVar = tk.IntVar()
        self.resetSettingsVar.set(int(play_list.resetSettings))
        tk.Checkbutton(self.top, text="Reset Settings on New Playlist.", fg=fontColor.get(), font=allButtonsFont.get(),
                       bg=color, variable=self.resetSettingsVar, command=self.resetSettingsOnNewPlaylist,
                       selectcolor="black").place(x=200, y=480)
        
        self.crossFadeBetweenTracks = tk.IntVar()
        self.crossFadeBetweenTracks.set(int(play_list.useCrossFade))
        tk.Checkbutton(self.top, text="Use cross-fading.", fg=fontColor.get(), font=allButtonsFont.get(),
                       bg=color, variable=self.crossFadeBetweenTracks, command=self.enableDisableCrossFade,
                       selectcolor="black").place(x=columnOne, y=432)
                
        tk.Label(self.top, text="Danthology refers to resuming the next song \n"+
                                "at the duration the current one has ended.\n" +
                                "This feature enables easier browse among \n"+
                                "unknown media.", fg=fontColor.get(),
                        font=allButtonsFont.get(), bg=color).place(x=180, y=510)

        self.top.bind("<Escape>", self.destroyEsc)
        self.top.bind("<Tab>", self.focus_Input)
        dialog = self
    
    def enableDisableSongsStatsKeeping(self):
        global play_list
        if self.MaintainSongsStats.get() == 1:
            play_list.keepSongsStats = True
        else:
            play_list.keepSongsStats = False
    
    def changeButtonSpacing(self, event):
        play_list.buttonSpacing = int(self.textButtonSpace.get())
        reSpacePositionElements()  # respace elements
        showCurrentSongInList() #select/highlight the current song in the listbox

    def changePlaylistWidth(self, event):
        if self.textPlaylistWidth.get()!="Auto":
            play_list.listboxWidth = int(self.textPlaylistWidth.get())
            listbox["width"] = play_list.listboxWidth
        else:
            play_list.listboxWidth = "Auto"
            displayElementsOnPlaylist()
        if play_list.viewModel != "COMPACT":
            if listbox["width"] < 75:
                value = (75 - int(self.textPlaylistWidth.get())) // 5  # value shoud be between 0 and 2
                MoveUpButton["width"] -= value
                MoveDownButton["width"] -= value
                RemoveSongButton["width"] -= value
                SortListButton["width"] -= value
            elif MoveUpButton["width"] != allButtonsWidth:
                MoveUpButton["width"] = allButtonsWidth
                MoveDownButton["width"] = allButtonsWidth
                RemoveSongButton["width"] = allButtonsWidth
                SortListButton["width"] = allButtonsWidth
        changePlaylistView()  # this will rearrange elements and resize the window.
        showCurrentSongInList()  # select/highlight the current song in the listbox

    def changePlaylistHeight(self, event):
        play_list.listboxNoRows = int(self.textPlaylistRows.get())
        if play_list.viewModel!= "COMPACT" and play_list.viewModel!="SMALL PLAYLIST":
            changePlaylistView()
        showCurrentSongInList() #select/highlight the current song in the listbox

    def restoreDefaults(self):
        global play_list
        play_list.VolumeLevel=1.0
        play_list.useMassFileEditor=False
        play_list.danthologyMode=False
        play_list.danthologyDuration=0
        play_list.danthologyTimer=0
        play_list.windowOpacity=1.0
        play_list.progressTime = "Ascending" #possible values: Ascending and Descending
        play_list.skin=0
        play_list.usePlayerTitleTransition = True
        play_list.playingFileNameTransition = "separation" # values : separation, typewriting, none
        play_list.customFont = None
        play_list.customElementBackground = None
        play_list.customLabelBackground = None
        play_list.customBackgroundPicture = None
        play_list.customFontColor = None
        play_list.customChangeBackgroundedLabelsColor = None
        play_list.userCreatedColors = []
        play_list.ProgressBarType = "determinate"
        play_list.LyricsActiveSource = LyricsOnlineSources[0] #default, all sources
        play_list.resetSettings = False
        play_list.useCrossFade = False
        window.attributes('-alpha', play_list.windowOpacity)
        # Restore default skin
        play_list.listboxWidth = "Auto"
        play_list.listboxNoRows = 35
        play_list.buttonSpacing = 50
        play_list.keepSongsStats = True
        SkinColor.set(skinOptions[1][play_list.skin])
        changeSkin("<Double-Button>")
        displayElementsOnPlaylist()
        
    def resetSettingsOnNewPlaylist(self):
        if self.resetSettingsVar.get() == 1:
            play_list.resetSettings = True
        else:
            play_list.resetSettings = False
    
    def changeActiveLyricsSource(self, event):
        play_list.LyricsActiveSource = self.LyricsSourcesText.get()
        showCurrentSongInList() #select/highlight the current song in the listbox

    def changeProgressBar(self, event):
        global play_list
        global progress
        play_list.ProgressBarType = self.textProgressBarType.get()
        progress["mode"] = play_list.ProgressBarType
        showCurrentSongInList() #select/highlight the current song in the listbox
    
    def enableDisableMassFileEditor(self):
        global play_list
        if self.MassFileEditorUsage.get() == 1:
            play_list.useMassFileEditor = True
        else:
            play_list.useMassFileEditor = False
		
    def enableDisableCrossFade(self):
        global play_list
        global temp_SongEndPos
        if len(play_list.validFiles) > 0 and play_list.currentSongIndex!=None:
            if self.crossFadeBetweenTracks.get() == 1:
                play_list.validFiles[play_list.currentSongIndex].fadein_duration = play_list.crossFadeDuration
                play_list.validFiles[play_list.currentSongIndex].fadeout_duration = play_list.crossFadeDuration
                temp_SongEndPos = play_list.validFiles[play_list.currentSongIndex].endPos
                play_list.validFiles[play_list.currentSongIndex].endPos = (play_list.validFiles[play_list.currentSongIndex].Length - play_list.crossFadeGap*3)
                play_list.useCrossFade = True
            else:
                play_list.validFiles[play_list.currentSongIndex].fadein_duration = 0
                play_list.validFiles[play_list.currentSongIndex].fadeout_duration = 0
                if temp_SongEndPos!= None:
                    play_list.validFiles[play_list.currentSongIndex].endPos = temp_SongEndPos
                else: #this should never happen.
                    play_list.validFiles[play_list.currentSongIndex].endPos = play_list.validFiles[play_list.currentSongIndex].Length
                play_list.useCrossFade = False
     
    def changeProgressTime(self, event):
        global play_list
        if self.ProgressTimeText.get() == "Playing Time":
            play_list.progressTime = "Ascending"
        else:
            play_list.progressTime = "Descending"
        showCurrentSongInList() #select/highlight the current song in the listbox

    def useColorPicked(self, event):
        global SkinColor
        global labelBackground
        global fontColor
        if self.ColorPickerValue!="":
            if self.textColorPickerUsage.get() == "Button&Label Color":
                SkinColor.set(self.ColorPickerValue)
                play_list.userCreatedColors.append(self.ColorPickerValue)
                custom_color_list.append(self.ColorPickerValue)
                changingBackgroundElementColor(event)
            elif self.textColorPickerUsage.get() == "Label Background":
                labelBackground.set(self.ColorPickerValue)
                play_list.userCreatedColors.append(self.ColorPickerValue)
                custom_color_list.append(self.ColorPickerValue)
                changingLabelBackgroundColor(event)
            elif self.textColorPickerUsage.get() == "Font Color":
                fontColor.set(self.ColorPickerValue)
                play_list.userCreatedColors.append(self.ColorPickerValue)
                custom_color_list.append(self.ColorPickerValue)
                changingFontColor(event)
        showCurrentSongInList() #select/highlight the current song in the listbox

    def composeColor(self, event):
        global custom_color_list
        red = ""
        if int(self.scaleRed.get()) >=0 and  int(self.scaleRed.get()<10):
            red = str(hex(self.scaleRed.get()))
            red=red.split("x")
            red= "0" + red[1]
        else:
            red = str(hex(self.scaleRed.get()))
            red = red.split("x")
            red = red[1]

        green = ""
        if int(self.scaleGreen.get()) >= 0 and int(self.scaleGreen.get() < 10):
            green = str(hex(self.scaleGreen.get()))
            green = green.split("x")
            green = "0" + green[1]
        else:
            green = str(hex(self.scaleGreen.get()))
            green = green.split("x")
            green = green[1]

        blue = ""
        if int(self.scaleBlue.get()) >= 0 and int(self.scaleBlue.get() < 10):
            blue = str(hex(self.scaleBlue.get()))
            blue = blue.split("x")
            blue = "0" + blue[1]
        else:
            blue = str(hex(self.scaleBlue.get()))
            blue = blue.split("x")
            blue = blue[1]

        self.ColorPickerValue = "#" + red + green + blue
        self.ColorPickerResult["bg"] = self.ColorPickerValue

    def changeDanthologyDuration(self, event):
        global play_list
        play_list.danthologyDuration = int(self.DanthologyInterval.get())
        play_list.danthologyTimer = time.time()
        showCurrentSongInList() #select/highlight the current song in the listbox

    def changeWindowOpacity(self,event):
        global play_list
        play_list.windowOpacity = float(self.WindowOpacityText.get())
        window.attributes('-alpha', play_list.windowOpacity)
        self.top.attributes('-alpha', play_list.windowOpacity)
        showCurrentSongInList() #select/highlight the current song in the listbox

    def changeDanthologyMode(self):
        global play_list
        if play_list.danthologyMode == True:
            play_list.danthologyMode = False
            self.textDanthologyMode.set("Danthology Mode OFF")
            textDanthologyMode.set("Danthology Mode: OFF")
        else:
            play_list.danthologyMode = True
            self.textDanthologyMode.set("Danthology Mode ON")
            textDanthologyMode.set("Danthology Mode: ON")
            if play_list.REPEAT == 0 : #if Repeat Off -> make Repeat All, because we need some sort of REPEAT for this one.
                play_list.REPEAT = 1
                RepeatButtonText.set("Repeat All")
                
    def changeTitleTransition(self):
        global play_list
        if play_list.usePlayerTitleTransition == True:
            play_list.usePlayerTitleTransition = False
            self.TitleTransitionButtonText.set("Title Transition OFF")
            window.title("   PyPlay MP3 Player in Python     ")
        else:
            play_list.usePlayerTitleTransition = True
            self.TitleTransitionButtonText.set("Title Transition ON")
        showCurrentSongInList() #select/highlight the current song in the listbox

    def focus_Input(self, event):
        self.top.wm_attributes("-topmost", 1)
        if self.colorBox.focus_get():
            self.fontBox.focus_force()
        elif self.fontBox.focus_get():
            self.labelColorBox.focus_force()
        elif self.labelColorBox.focus_get():
            self.FontMainColorBox.focus_force()
        elif self.FontMainColorBox.focus_get():
            self.colorBox.focus_force()

    def changeFileNameTransition(self,event):
        global play_list
        global visualSongNameLabel
        play_list.playingFileNameTransition = self.FontTransitionText.get()
        if play_list.playingFileNameTransition == "none":
            visualSongNameLabel = play_list.validFiles[play_list.currentSongIndex].fileName
        elif play_list.playingFileNameTransition == "typewriting":
            visualSongNameLabel = ""
        elif play_list.playingFileNameTransition == "separation":
            visualSongNameLabel = "_" + play_list.validFiles[play_list.currentSongIndex].fileName
        showCurrentSongInList() #select/highlight the current song in the listbox
    
    def take_focus(self):
        self.top.wm_attributes("-topmost", 1)
        self.top.grab_set()
        self.colorBox.focus_force()

    def browse_background_picture(self):
        global play_list
        background = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=(
        ("jpg files", "*.jpg"), ("png files", "*.png"),("gif files", "*.gif"), ("jpeg files", "*.jpeg"),("all files", "*.*")))
        if ".gif" in background:
            play_list.customBackgroundPicture = background
            background_image = tk.PhotoImage(file=play_list.customBackgroundPicture)
            background_label.configure(image=background_image)
            background_label.image = background_image
        elif ".jpg" in background or ".jpeg" in background or ".png" in background:
            play_list.customBackgroundPicture = background
            img = ImageTk.PhotoImage(Image.open(background))
            background_label.configure(image=img)
            background_label.image = img
        else:
            messagebox.showinfo("Information", "The background picture has to be one of following formats: .gif, .jpg, .jpeg, .png.")

class NewPlaylistDialog(Window):
    def __init__(self, parent):
        global allButtonsFont
        global dialog
        color = OpenFileButton["bg"]
        self.top = tk.Toplevel(parent, bg=color)
        self.top.protocol("WM_DELETE_WINDOW", self.destroy)
        Window_Title = "Info"
        self.top.title(Window_Title)
        self.top.geometry("480x200+100+100")
        self.top.attributes('-alpha', play_list.windowOpacity)
        if type(allButtonsFont) == StringVar:
            allButtonsFont = allButtonsFont.get()
        self.labelInfo = tk.Label(self.top, text="One song is currently playing.\n\nDo you wish to stop, or keep it in the playlist?", \
                                  fg=fontColor.get(), font=allButtonsFont, bg=color).pack()
        StopItButton = tk.Button(self.top, text="Stop It", command=self.stopIt , fg=fontColor.get(), font=allButtonsFont, bg=color)
        KeepItButton = tk.Button(self.top, text="Keep It", command=self.keepCurrentSong, fg=fontColor.get(), font=allButtonsFont, bg=color)
        StopItButton.pack(pady=10)
        KeepItButton.pack(pady=10)
        dialog = self
        self.top.bind("<Escape>", self.destroyEsc)

    def stopIt(self):
        global play_list
        global listBox_Song_selected_index
        if play_list.resetSettings == False:
            play_list.isSongPause = False
            play_list.isSongStopped = False
            play_list.dirFilePath = None
            play_list.validFiles = []
            play_list.currentSongIndex = None
            play_list.currentSongPosition = 0
            play_list.RESUMED=False
            play_list.playTime = 0
            play_list.shufflingHistory = []
            play_list.isListOrdered = 17
            play_list.PlaylistListenedTime = 0
            play_list.BornDate = datetime.datetime.now()
        else:
            play_list = Playlist()
            # Restore default skin
            SkinColor.set(skinOptions[1][play_list.skin])
            changeSkin("<Double-Button>")
            window.attributes('-alpha', play_list.windowOpacity)
        stop_music()
        self.destroy()
        clearLabels()
        listBox_Song_selected_index = None
        displayElementsOnPlaylist()

    def keepCurrentSong(self):
        global play_list
        global listBox_Song_selected_index
        songToKeep = play_list.validFiles[play_list.currentSongIndex]
        if play_list.resetSettings == False:
            play_list.dirFilePath = None
            play_list.validFiles = []
            play_list.currentSongIndex = 0
            play_list.RESUMED=False
            play_list.playTime = 0
            play_list.shufflingHistory = []
            play_list.isListOrdered = 17
            play_list.PlaylistListenedTime = 0
            play_list.BornDate = datetime.datetime.now()
        else:
            play_list = Playlist()
            # Restore default skin
            SkinColor.set(skinOptions[1][play_list.skin])
            changeSkin("<Double-Button>")
            window.attributes('-alpha', play_list.windowOpacity)
        if songToKeep!=None:
            play_list.PlaylistListenedTime = songToKeep.SongListenedTime
            play_list.validFiles.append(songToKeep)
            play_list.currentSongIndex = 0
        listBox_Song_selected_index = play_list.currentSongIndex
        del songToKeep
        self.destroy()
        displayElementsOnPlaylist()

class Mp3TagModifierTool(Window):
    def __init__(self, fileIndex=0):
        global allButtonsFont
        global dialog
        self.undoRenameBackupFile = "RENAMEALLFILES.backup"
        self.undoArtistTitleBackupFile = "ALLARTISTTITLE.backup"
        self.undoAlbumYearBackupFile = "PREVIOUSALBUMYEAR.backup"
        color = OpenFileButton["bg"]  # get the color which the rest of elements is using at the moment
        self.top = tk.Toplevel(window, bg=color)
        Window_Title = "Mp3TagModifier Tool"
        columnOne=5
        columnTwo = 150
        columnThree = 290
        FormatComboBoxesXPos = 500
        self.Song = play_list.validFiles[fileIndex]
        self.top.title(Window_Title)
        self.top.protocol("WM_DELETE_WINDOW", self.destroy)
        self.top.attributes('-alpha', play_list.windowOpacity)
        if type(allButtonsFont) == StringVar:
            allButtonsFont = allButtonsFont.get()
        tk.Label(self.top, text="Name:", fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=columnOne, y=5)
        self.NameTag = tk.Entry(self.top, width=80)
        self.NameTag.insert(0, self.Song.fileName)
        self.NameTag.place(x=columnOne, y=25)
        self.NameTag.bind("<Key>", self.setNAOnName)
        
        tk.Label(self.top, text="Naming Case:", fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=500, y=5)
        textConversionValues=["NA","Capitalize", "SemiCapitalize", "Upper Case", "Lower Case"]
        self.nameTextFormat = StringVar()
        self.nameTextFormat.set("NA")
        self.NameFormatBox = Combobox(self.top, textvariable=self.nameTextFormat, values=textConversionValues, width=10, state="readonly", font=allButtonsFont)
        self.NameFormatBox.place(x=FormatComboBoxesXPos, y=25)
        self.NameFormatBox.bind("<<ComboboxSelected>>", self.changeNameFormat)
        
        tk.Label(self.top, text="Genre:", fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=columnOne, y=45)
        self.GenreTag = tk.Entry(self.top, width=15)
        self.GenreTag.insert(0, self.Song.Genre)
        self.GenreTag.place(x=columnOne, y=65)
        self.GenreTag.bind("<Key>", self.setNAOnTags)
        
        tk.Label(self.top, text="Tagging Case:", fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=500, y=65)
        self.tagTextFormat = StringVar()
        self.tagTextFormat.set("NA")
        self.TagFormatBox = Combobox(self.top, textvariable=self.tagTextFormat, values=textConversionValues, width=10, state="readonly", font=allButtonsFont)
        self.TagFormatBox.place(x=FormatComboBoxesXPos, y=85)
        self.TagFormatBox.bind("<<ComboboxSelected>>", self.changeTagFormat)
        
        tk.Label(self.top, text="Year:", fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=columnTwo, y=45)
        self.YearTag = tk.Entry(self.top, width=15)
        self.YearTag.insert(0, self.Song.Year)
        self.YearTag.place(x=columnTwo, y=65)
        self.YearTag.bind("<Key>", self.setNAOnTags)
        
        tk.Label(self.top, text="Album:", fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=columnThree, y=45)
        self.AlbumTag = tk.Entry(self.top, width=30)
        self.AlbumTag.insert(0, self.Song.Album)
        self.AlbumTag.place(x=columnThree, y=65)
        self.AlbumTag.bind("<Key>", self.setNAOnTags)
        
        tk.Label(self.top, text="Artist:", fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=columnOne, y=85)
        self.ArtistTag = tk.Entry(self.top, width=35)
        self.ArtistTag.insert(0, self.Song.Artist)
        self.ArtistTag.place(x=columnOne, y=105)
        self.ArtistTag.bind("<Key>", self.setNAOnTags)
        
        tk.Label(self.top, text="Title:", fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=250, y=85)
        self.TitleTag = tk.Entry(self.top, width=35)
        self.TitleTag.insert(0, self.Song.Title)
        self.TitleTag.place(x=250, y=105)
        self.TitleTag.bind("<Key>", self.setNAOnTags)
        
        RemoveCharsButton = tk.Button(self.top, text="Remove Special Characters", command=self.removeChars, fg=fontColor.get(), font=allButtonsFont,
                                bg=color)
        RemoveCharsButton.place(x=columnOne, y=145)
        
        GrabAlbumYearButton = tk.Button(self.top, text="Grab Album\Year From Web", command=self.grabAlbumAndYear, fg=fontColor.get(), font=allButtonsFont,
                                bg=color)
        GrabAlbumYearButton.place(x=columnOne, y=235)
        
        SaveChangesButton = tk.Button(self.top, text="Save Changes", command=self.SaveChanges, fg=fontColor.get(), font=allButtonsFont,
                                bg=color)
        SaveChangesButton.place(x=columnOne, y=295)
        
        ComposeFileNameButton = tk.Button(self.top, text="Compose Filename from 'Artist - Title'", command=self.composeFileName, fg=fontColor.get(), font=allButtonsFont,
                                        bg=color)
        ComposeFileNameButton.place(x=columnOne, y=175)
        ComposeArtistTitleButton = tk.Button(self.top, text="Compose Artist/Title from Filename", command=self.composeArtistTitle, fg=fontColor.get(), font=allButtonsFont,
                                        bg=color)
        ComposeArtistTitleButton.place(x=columnOne, y=205)

        self.MassRenameButton = tk.Button(self.top, text="Rename All Files to 'Artist - Title.mp3'", command=self.renameAllFiles, fg=fontColor.get(), font=allButtonsFont,
                                      bg=color)
        if play_list.useMassFileEditor:
            self.MassRenameButton.config(state = tk.NORMAL)
        else:
            self.MassRenameButton.config(state = tk.DISABLED)

        self.undoMassRenameButton = tk.Button(self.top, text="Restore Previous Names to All Files.", command=self.restorePreviousNames, fg=fontColor.get(), font=allButtonsFont,
                                      bg=color)
        if os.path.isfile(self.undoRenameBackupFile) and play_list.useMassFileEditor:
            self.undoMassRenameButton.config(state = tk.NORMAL)
        else:
            self.undoMassRenameButton.config(state = tk.DISABLED)

        self.MassArtistTitleComposeButton = tk.Button(self.top, text="Compose Artist/Title from Filename to All Files", command=self.composeArtistTitleAll, fg=fontColor.get(), font=allButtonsFont,
                                      bg=color)
        if play_list.useMassFileEditor:
            self.MassArtistTitleComposeButton.config(state = tk.NORMAL)
        else:
            self.MassArtistTitleComposeButton.config(state = tk.DISABLED)

        self.undoMassArtistTitleComposeButton = tk.Button(self.top, text="Restore Previous Artist/Title to All Files", command=self.undoComposeArtistTitleAll, fg=fontColor.get(), font=allButtonsFont,
                                      bg=color)
        if play_list.useMassFileEditor and os.path.isfile(self.undoArtistTitleBackupFile):
            self.undoMassArtistTitleComposeButton.config(state = tk.NORMAL)
        else:
            self.undoMassArtistTitleComposeButton.config(state = tk.DISABLED)
        
        GrabAlbumYearToAll = tk.Button(self.top, text="Grab missing Album\Year to All Files", command=self.grabAlbumYearToAllFiles, fg=fontColor.get(), font=allButtonsFont,
                              bg=color)
        if play_list.useMassFileEditor:
            GrabAlbumYearToAll.config(state = tk.NORMAL)
        else:
            GrabAlbumYearToAll.config(state = tk.DISABLED)
        
        undoAlbumYearToAll = tk.Button(self.top, text="Undo Album/Year to All Files", command=self.undoAlbumYearToAllFiles, fg=fontColor.get(), font=allButtonsFont,
                              bg=color)
        if play_list.useMassFileEditor and os.path.exists(self.undoArtistTitleBackupFile):
            undoAlbumYearToAll.config(state = tk.NORMAL)
        else:
            undoAlbumYearToAll.config(state = tk.DISABLED)
        
        buttonColumnTwo = columnOne + ComposeFileNameButton.winfo_reqwidth() + 50 #50 will be the margin between the 2 columns
        self.MassRenameButton.place(x=buttonColumnTwo, y=145)
        self.undoMassRenameButton.place(x=buttonColumnTwo, y=175)
        self.MassArtistTitleComposeButton.place(x=buttonColumnTwo, y=205)
        self.undoMassArtistTitleComposeButton.place(x=buttonColumnTwo, y=235)
        GrabAlbumYearToAll.place(x=buttonColumnTwo, y=265)
        undoAlbumYearToAll.place(x=buttonColumnTwo, y=295)
        
        windowWidth = buttonColumnTwo + self.MassArtistTitleComposeButton.winfo_reqwidth() + 20 #  #20 will be the margin between button and end of window.
        if FormatComboBoxesXPos + self.NameFormatBox.winfo_reqwidth()+50 > windowWidth: #make sure this element is also visible in the given window.
            windowWidth = FormatComboBoxesXPos + self.NameFormatBox.winfo_reqwidth()+50
        self.top.geometry(str(windowWidth)+"x360+100+100")
        self.top.bind("<Tab>", self.focus_out)
        self.top.bind("<Escape>", self.destroyEsc)
        dialog = self
        
        #this is for input-speed purposes:
        global progressViewRealTime
        progressViewRealTime = 0.1 # the main progress function will influence the input speed. Make sure it's close to instant while this window is openened. 
    
    def undoAlbumYearToAllFiles(self):
        if os.path.exists(self.undoAlbumYearBackupFile):
            try:
                file = open(self.undoAlbumYearBackupFile, "rb")
                dict_list = pickle.load(file)
                file.close()
            except Exception:
                print("Exception when loading File: " + str(self.undoArtistTitleBackupFile))
                print("The content of backup file has been corrupted.")
            else:
                for song in play_list.validFiles:
                    for element in dict_list:
                        if element['fileName'] == song.fileName:
                            if pygame.mixer.get_init() and play_list.validFiles.index(song) == play_list.currentSongIndex and pygame.mixer.music.get_busy():
                                pygame.mixer.music.stop()
                                pygame.mixer.music.load("clear.mp3") #use this file to release the playback
                            mp3file = EasyID3(song.filePath)
                            song.Album = element['oldAlbum']
                            song.Year = element['oldYear']
                            mp3file["album"] = song.Album
                            mp3file["date"] = song.Year
                            if song.Album == "":
                                song.Album = "Various"
                            if song.Year == "":
                                song.Year = "Various"
                            mp3file.save(v2_version=3)
                            del dict_list[dict_list.index(element)]
                            break
                            
                if len(dict_list) > 0 :
                    message = ""
                    for element in dict_list:
                        message += element['fileName'] + "\n"
                    messagebox.showinfo("Information", "Some files not found within playlist:\n" + message)
                else:
                    messagebox.showinfo("Information", "Operation Done\n\nPrevious Album/Year tags have been restored.")
                self.AlbumTag.delete(0, tk.END)
                self.AlbumTag.insert(0, self.Song.Album)
                self.YearTag.delete(0, tk.END)
                self.YearTag.insert(0, self.Song.Year)
                file = open(self.undoAlbumYearBackupFile, "wb")
                pickle.dump(dict_list, file)
                file.close()
    
    def grabAlbumYearToAllFiles(self): 
        dictionary={}
        dict_list=[]
        not_found = []
        dict_loaded=False
        alreadyContained = False
        if os.path.exists(self.undoAlbumYearBackupFile):
            try:
                file = open(self.undoAlbumYearBackupFile, "rb")
                dict_list = pickle.load(file)
            except Exception:
                dict_list = [] #make sure it's empty
                print("Exception when loading File: " + str(self.undoAlbumYearBackupFile))
                print("Since the content has been corrupted, your file will be replaced.")
            else:
                dict_loaded = True
                file.close()
        
        for song in play_list.validFiles:
            dictionary['fileName'] = song.fileName
            dictionary['oldAlbum'] = song.Album if song.Album != "Various" else ""
            dictionary['oldYear'] = song.Year if song.Year != "Various" else ""
            ret_val = self.grabAlbumAndYear(song)
            if ret_val != None:
                not_found.append(ret_val)
            else:
                dictionary['newAlbum'] = song.Album
                dictionary['newYear'] = song.Year
                if dict_loaded:
                    for element in dict_list:
                        if element["fileName"] == song.fileName:
                            dictionary['oldAlbum'] = element["oldAlbum"]
                            dictionary['oldYear'] = element["oldYear"]
                            break
                dict_list.append(dictionary)
            dictionary = {}
        if len(not_found) > 0:
            messagebox.showinfo("Information", "Operation Done\n\nThe data for the following items could not be retrieved: \n\n" + "\n".join(not_found))
        else:
            messagebox.showinfo("Information", "Operation Done\n\nThe data was collected from the Internet.")

        if len(dict_list) > 0: # we have files changes
            file = open(self.undoAlbumYearBackupFile, "wb") 
            pickle.dump(dict_list, file)
            file.close()
        
    def filterArtistTitleForWebSearch(self, value):
        if value != "Various":
            value = value.replace("'", "")
            value = value.replace(",", "")
            value = value.replace(":", "")
            value = value.replace(".", "")
            value = value.replace("!", "")
            value = value.replace("%", "")
            value = value.replace("?", "")
            value = value.replace("`", "")
            value = value.replace("`", "")
            value = value.replace(" & ", " and ")
            value = value.replace("&", " and ")
            value = value.replace(".mp3", "")
            value = value.replace(".MP3", "")
            value = value.replace(".mP3", "")
            value = value.replace(".Mp3", "")
            value = value.replace(" ", "+")
            return value
        return False
    
    def filterAlbumFromLastFM(self, data): #this filter might not work anymore in time, 
                    #if LastFM decide to change the structure of their webpages.
        text = BeautifulSoup(data, "html.parser")
        text = text.decode("utf-8")
        # Start filtering the html content of the webpage
        if '<div class="source-album-details">' in text:
            text = text.split('<div class="source-album-details">')
            text = text[1].split('</div>')
            text = "".join(text)
            if '<a class' in text:
                text = text.split('<a class')
                text = text[1].split('</a>')
                text = text[0]
                text = text.split(">")
                text = text[1]
                text = "".join(text)
                text = text.strip()
                text = text.strip(" ")
                return text
        return False
    
    def filterYearFromLastFM(self, data): #this filter might not work anymore in time, 
                    #if LastFM decide to change the structure of their webpages.
        text = BeautifulSoup(data, "html.parser")
        text = text.decode("utf-8")
        text = text.replace("\n", "")
        text = text.replace("  ", "")
        # Start filtering the html content of the webpage
        if 'Release Date</dt>' in text:
            text = text.split('Release Date</dt>')
            text = text[1].split('</dd>')
            text = text[0]
            text = text.replace('<dd class="catalogue-metadata-description">', "")
            return text
        return False
    
    def grabAlbumAndYear(self, song_param=None):
        MassFileEditor = True if type(song_param)==Song else False
        if MassFileEditor == False:
            objectSong = self.Song
        else:
            objectSong = song_param
        urllib3.disable_warnings()
        
        artist = objectSong.Artist
        artist = self.filterArtistTitleForWebSearch(artist)
        title = objectSong.Title
        title = self.filterArtistTitleForWebSearch(title)
        if artist!= False and title!=False:
            url = "https://www.last.fm/music/" + artist + "/_/" + title # this is possible to change with time. Let's hope it doesn't
            http = urllib3.PoolManager()
            try:
                response = http.request('GET', url)
            except NewConnectionError as exp:  # This is the correct syntax
                print("Unable to establish connection to the server: last.fm")
                print("Error Message: " + str(exp))
                print("Please check your internet connection before proceed.")
            except Exception:
                print("An exception has been handled. I am sorry but I'm unable to retrieve info.")
            else:
                if response.status == 200:
                    text = self.filterAlbumFromLastFM(response.data)
                    if text != False:
                        if MassFileEditor == False:
                            self.AlbumTag.delete(0, tk.END)
                            self.AlbumTag.insert(tk.END, text)
                        else:
                            mp3file = EasyID3(objectSong.filePath)
                            mp3file["album"] = text
                            objectSong.Album = text
                            mp3file.save(v2_version=3)
                            if objectSong == self.Song:
                                self.AlbumTag.delete(0, tk.END)
                                self.AlbumTag.insert(tk.END, text)
                        text = text.replace(" ", "+")
                        url = "https://www.last.fm/music/" + artist + "/" + text # this is possible to change with time. Let's hope it doesn't
                        try:
                            response = http.request('GET', url)
                        except NewConnectionError as exp:  # This is the correct syntax
                            print("Unable to establish connection to the server: last.fm")
                            print("Error Message: " + str(exp))
                            print("Please check your internet connection before proceed.")
                        except Exception:
                            print("An exception has been handled. I am sorry but I'm unable to retrieve info.")
                        else:
                            if response.status == 200:
                                text = self.filterYearFromLastFM(response.data)
                                if text != False:
                                    year = text.split(" ")[len(text.split(" "))-1] # because the I only want to store the year, discard the day and the month.
                                    if MassFileEditor == False:
                                        self.YearTag.delete(0, tk.END)
                                        self.YearTag.insert(tk.END, year)
                                    else:
                                        mp3file = EasyID3(objectSong.filePath)
                                        mp3file["date"] = year
                                        objectSong.Year = year
                                        mp3file.save(v2_version=3)
                                        if objectSong == self.Song:
                                            self.YearTag.delete(0, tk.END)
                                            self.YearTag.insert(tk.END, year)
                                else:
                                    if MassFileEditor == False:
                                        messagebox.showinfo("Information", "The year could not be found on Web.")
                    else:
                        if MassFileEditor == False:
                            messagebox.showinfo("Information", "There is no webpage available to find the year.")
                        else:
                            return objectSong.fileName #return the name of item which was not found on web
                else:
                    if MassFileEditor == False:
                        messagebox.showinfo("Information", "There is no webpage available for this album.")
                    else:
                        return objectSong.fileName #return the name of item which was not found on web
        else:
            return objectSong.fileName #return the name of item which was not found on web
        return None  #File was found.                  

    def removeSpecialChars(self, originalNameValue):
        originalNameValue = originalNameValue.replace(" & ", " and ")
        originalNameValue = originalNameValue.replace("&", " and ")
        originalNameValue = originalNameValue.replace(" feat. ", " and ")
        originalNameValue = originalNameValue.replace("feat.", " and ")
        originalNameValue = originalNameValue.replace(" vs. ", " and ")
        originalNameValue = originalNameValue.replace(" vs ", " and ")
        originalNameValue = originalNameValue.replace("vs.", " and ")
        originalNameValue = originalNameValue.replace("vs", " and ")
        originalNameValue = originalNameValue.replace(" featuring ", " and ")
        originalNameValue = originalNameValue.replace("+", " plus ")
        originalNameValue = originalNameValue.replace(" + ", " plus ")
        originalNameValue = originalNameValue.replace("%", " percent")
        originalNameValue = originalNameValue.replace(" %", " percent")
        originalNameValue = originalNameValue.replace(" % ", " percent ")
        originalNameValue = originalNameValue.replace("{", "")
        originalNameValue = originalNameValue.replace("}", "")
        originalNameValue = originalNameValue.replace("[", "")
        originalNameValue = originalNameValue.replace("]", "")
        originalNameValue = originalNameValue.replace("|", "")
        originalNameValue = originalNameValue.replace("*", "")
        originalNameValue = originalNameValue.replace("~", "")
        originalNameValue = originalNameValue.replace(". ", "")
        originalNameValue = originalNameValue.replace("=", "")
        originalNameValue = originalNameValue.replace("=", "")
        originalNameValue = originalNameValue.replace(">", "")
        originalNameValue = originalNameValue.replace("<", "")
        originalNameValue = originalNameValue.replace("#", "")
        originalNameValue = originalNameValue.replace("@", "")
        originalNameValue = originalNameValue.replace("`", "'")
        originalNameValue = originalNameValue.replace("^", "")
        originalNameValue = originalNameValue.replace("_", " ")
        originalNameValue = ' '.join(originalNameValue.split()) #remove multiple spaces/tabs
        return originalNameValue
    
    def removeChars(self):
        originalNameValue = self.NameTag.get()
        self.NameTag.delete(0, tk.END)
        self.NameTag.insert(0, self.removeSpecialChars(originalNameValue))
        originalArtistValue = self.ArtistTag.get()
        self.ArtistTag.delete(0, tk.END)
        self.ArtistTag.insert(0, self.removeSpecialChars(originalArtistValue))
        originalGenreValue = self.GenreTag.get()
        self.GenreTag.delete(0, tk.END)
        self.GenreTag.insert(0, self.removeSpecialChars(originalGenreValue))
        originalTitleValue = self.TitleTag.get()
        self.TitleTag.delete(0, tk.END)
        self.TitleTag.insert(0, self.removeSpecialChars(originalTitleValue))
        originalYearValue = self.YearTag.get()
        self.YearTag.delete(0, tk.END)
        self.YearTag.insert(0, self.removeSpecialChars(originalYearValue))
        originalAlbumValue = self.AlbumTag.get()
        self.AlbumTag.delete(0, tk.END)
        self.AlbumTag.insert(0, self.removeSpecialChars(originalAlbumValue))
        
    def tagCapitalizer(self):
        if self.ArtistTag.get()!= "Various":
            newValue=self.ArtistTag.get().split(" ")
            value=""
            for word in newValue:
                value+= word.capitalize() + " "
            self.ArtistTag.delete(0, tk.END) 
            self.ArtistTag.insert(0, value.strip(" ")) 
        if self.GenreTag.get()!= "Various":
            newValue=self.GenreTag.get().split(" ")
            value=""
            for word in newValue:
                value+= word.capitalize() + " "
            self.GenreTag.delete(0, tk.END) 
            self.GenreTag.insert(0, value.strip(" ")) 
        if self.TitleTag.get()!= "Various":
            newValue=self.TitleTag.get().split(" ")
            value=""
            for word in newValue:
                value+= word.capitalize() + " "
            self.TitleTag.delete(0, tk.END) 
            self.TitleTag.insert(0, value.strip(" ")) 
        if self.AlbumTag.get()!= "Various":
            newValue=self.AlbumTag.get().split(" ")
            value=""
            for word in newValue:
                value+= word.capitalize() + " "
            self.AlbumTag.delete(0, tk.END) 
            self.AlbumTag.insert(0, value.strip(" ")) 
        if self.YearTag.get()!= "Various":
            newValue=self.YearTag.get().split(" ")
            value=""
            for word in newValue:
                value+= word.capitalize() + " "
            self.YearTag.delete(0, tk.END) 
            self.YearTag.insert(0, value.strip(" ")) 
    
    def tagSemiCapitalizer(self):
        if self.ArtistTag.get()!= "Various":
            newValue=self.ArtistTag.get().split(" ")
            value=""
            for word in newValue:
                if newValue.index(word) == 0:
                    value+= word.capitalize() + " "
                else:
                    value+= word.lower() + " "
            self.ArtistTag.delete(0, tk.END) 
            self.ArtistTag.insert(0, value.strip(" ")) 
        if self.GenreTag.get()!= "Various":
            newValue=self.GenreTag.get().split(" ")
            value=""
            for word in newValue:
                if newValue.index(word) == 0:
                    value+= word.capitalize() + " "
                else:
                    value+= word.lower() + " "
            self.GenreTag.delete(0, tk.END) 
            self.GenreTag.insert(0, value.strip(" ")) 
        if self.TitleTag.get()!= "Various":
            newValue=self.TitleTag.get().split(" ")
            value=""
            for word in newValue:
                if newValue.index(word) == 0:
                    value+= word.capitalize() + " "
                else:
                    value+= word.lower() + " "
            self.TitleTag.delete(0, tk.END) 
            self.TitleTag.insert(0, value.strip(" ")) 
        if self.AlbumTag.get()!= "Various":
            newValue=self.AlbumTag.get().split(" ")
            value=""
            for word in newValue:
                if newValue.index(word) == 0:
                    value+= word.capitalize() + " "
                else:
                    value+= word.lower() + " "
            self.AlbumTag.delete(0, tk.END) 
            self.AlbumTag.insert(0, value.strip(" ")) 
        if self.YearTag.get()!= "Various":
            newValue=self.YearTag.get().split(" ")
            value=""
            for word in newValue:
                if newValue.index(word) == 0:
                    value+= word.capitalize() + " "
                else:
                    value+= word.lower() + " "
            self.YearTag.delete(0, tk.END) 
            self.YearTag.insert(0, value.strip(" ")) 
    
    def changeTagFormat(self, event):
        if self.tagTextFormat.get() == "Capitalize":
            self.tagCapitalizer()
        elif self.tagTextFormat.get() == "SemiCapitalize":
            self.tagSemiCapitalizer()
        elif self.tagTextFormat.get() == "Upper Case":
            value = self.ArtistTag.get()
            if value!= "Various":
                self.ArtistTag.delete(0, tk.END) 
                self.ArtistTag.insert(0, value.strip(" ").upper()) 
            value = self.GenreTag.get()
            if value!= "Various":
                self.GenreTag.delete(0, tk.END) 
                self.GenreTag.insert(0, value.strip(" ").upper()) 
            value = self.TitleTag.get()
            if value!= "Various":
                self.TitleTag.delete(0, tk.END) 
                self.TitleTag.insert(0, value.strip(" ").upper()) 
            value = self.AlbumTag.get()
            if value!= "Various":
                self.AlbumTag.delete(0, tk.END) 
                self.AlbumTag.insert(0, value.strip(" ").upper()) 
            value = self.YearTag.get()
            if value!= "Various":
                self.YearTag.delete(0, tk.END) 
                self.YearTag.insert(0, value.strip(" ").upper()) 
        elif self.tagTextFormat.get() == "Lower Case":
            value = self.ArtistTag.get()
            if value!= "Various":
                self.ArtistTag.delete(0, tk.END) 
                self.ArtistTag.insert(0, value.strip(" ").lower()) 
            value = self.GenreTag.get()
            if value!= "Various":
                self.GenreTag.delete(0, tk.END) 
                self.GenreTag.insert(0, value.strip(" ").lower()) 
            value = self.TitleTag.get()
            if value!= "Various":
                self.TitleTag.delete(0, tk.END) 
                self.TitleTag.insert(0, value.strip(" ").lower()) 
            value = self.AlbumTag.get()
            if value!= "Various":
                self.AlbumTag.delete(0, tk.END) 
                self.AlbumTag.insert(0, value.strip(" ").lower()) 
            value = self.YearTag.get()
            if value!= "Various":
                self.YearTag.delete(0, tk.END) 
                self.YearTag.insert(0, value.strip(" ").lower()) 
        showCurrentSongInList() #this will maintain selection

    def setNAOnName(self, event):
        self.nameTextFormat.set("NA")

    def setNAOnTags(self, event):
        self.tagTextFormat.set("NA")
    
    def changeNameFormat(self, event):
        if self.nameTextFormat.get() == "Capitalize":
            self.NameCapitalizer()
        elif self.nameTextFormat.get() == "SemiCapitalize":
            self.NameSemiCapitalizer()
        elif self.nameTextFormat.get() == "Upper Case":
            value = self.NameTag.get()
            self.NameTag.delete(0, tk.END)
            if value.count("-") == 1:
                value = value.split("-")    
                self.NameTag.insert(0, value[0].strip(" ").upper() + " - " + value[1].strip(" ").upper()) 
            else:
                self.NameTag.insert(0, value.strip(" ").upper())
        elif self.nameTextFormat.get() == "Lower Case":
            value = self.NameTag.get()
            self.NameTag.delete(0, tk.END)
            if value.count("-") == 1:
                value = value.split("-")    
                self.NameTag.insert(0, value[0].strip(" ").lower() + " - " + value[1].strip(" ").lower()) 
            else:
                self.NameTag.insert(0, value.strip(" ").lower())
        showCurrentSongInList() #this will maintain selection.
    
    def composeArtistTitleAll(self):
        dictionary={}
        dict_list=[]
        dict_loaded=False
        if os.path.exists(self.undoArtistTitleBackupFile):
            try:
                file = open(self.undoArtistTitleBackupFile, "rb")
                dict_list = pickle.load(file)
            except Exception:
                dict_list = [] #make sure it's empty
                print("Exception when loading File: " + str(self.undoArtistTitleBackupFile))
                print("Since the content has been corrupted, your file will be replaced.")
            else:
                dict_loaded = True
                file.close()
            finally:
                file = open(self.undoArtistTitleBackupFile, "wb")
        else:
            file = open(self.undoArtistTitleBackupFile, "wb")
        for song in play_list.validFiles:
            if song.fileName != "":
                alreadyContained = False
                if dict_loaded:
                    for element in dict_list:
                        if element["newArtist"] == song.Artist and element["newTitle"] == song.Title and element["fileName"] == song.fileName:
                            alreadyContained = True
                            break
                if alreadyContained == False and os.path.exists(song.filePath):
                    mp3file = EasyID3(song.filePath)
                    dictionary['fileName'] = song.fileName
                    if song.Artist!= "Various":
                        dictionary['oldArtist'] = song.Artist
                    else:
                        dictionary['oldArtist'] = ""
                    if song.Title != "Various":
                        dictionary['oldTitle'] = song.Title
                    else:
                        dictionary['oldTitle'] = ""
                    if pygame.mixer.get_init() and play_list.validFiles.index(song) == play_list.currentSongIndex and pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("clear.mp3") #use this file to release the playback
                    if "-" in song.fileName:
                        value = song.fileName.split("-")
                        value[0] = [n.capitalize() for n in value[0].split(" ")] #perform Capitalization for Artist Name
                        song.Artist = " ".join(value[0])
                        value[1] = value[1].rstrip(".mp3")
                        value[1] = value[1].rstrip(".MP3")
                        value[1] = value[1].rstrip(".mP3")
                        value[1] = value[1].rstrip(".Mp3")
                        value[1] = value[1].strip(" ")
                        ##this will perform Capitalization and Semi-Capitalization for the Title
                        if len(value[1].split(" ")) > 2:
                            song.Title = value[1][0].capitalize() + value[1][1:].lower()
                        else:
                            value[1] = [n.capitalize() for n in value[1].split(" ")]
                            song.Title = " ".join(value[1])
                        song.Title = song.Title.strip(" ")
                        song.Artist = song.Artist.strip(" ")
                        mp3file["artist"] = song.Artist
                        mp3file["title"] = song.Title
                        dictionary["newArtist"] = song.Artist
                        dictionary["newTitle"] = song.Title
                    else:
                        value[0] = value[0].rstrip(".MP3")
                        value[0] = value[0].rstrip(".mP3")
                        value[0] = value[0].rstrip(".Mp3")
                        value[0] = value[0].rstrip(".mp3")
                        song.Artist = value[0].strip(" ")
                        mp3file["artist"] = song.Artist
                        dictionary["newArtist"] = song.Artist
                        dictionary["newTitle"] = ""
                    dict_list.append(dictionary)
                    dictionary = {}
                    mp3file.save(v2_version=3)
        self.ArtistTag.delete(0, tk.END)
        self.ArtistTag.insert(0, self.Song.Artist)
        self.TitleTag.delete(0, tk.END)
        self.TitleTag.insert(0, self.Song.Title)
        messagebox.showinfo("Information", "Operation Done\n\nArtist/Title tags were changed for all files.")
        pickle.dump(dict_list, file)
        file.close()
        if os.path.isfile(self.undoArtistTitleBackupFile) and play_list.useMassFileEditor:
            self.undoMassArtistTitleComposeButton.config(state = tk.NORMAL)
        else:
            self.undoMassArtistTitleComposeButton.config(state = tk.DISABLED)
    
    def undoComposeArtistTitleAll(self):
        dict_list=[]
        try:
            file = open(self.undoArtistTitleBackupFile, "rb")
            dict_list = pickle.load(file)
            file.close()
        except Exception as exp:
            dict_list = [] #make sure it's empty
            print("Backup File Exception: " + str(exp))
            print("File: " + str(self.undoArtistTitleBackupFile)+ " might be corrupted.")
        for song in play_list.validFiles:
            for element in dict_list:
                if element['fileName'] == song.fileName:
                    if pygame.mixer.get_init() and play_list.validFiles.index(song) == play_list.currentSongIndex and pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("clear.mp3") #use this file to release the playback
                    mp3file = EasyID3(song.filePath)
                    song.Artist = element['oldArtist']
                    song.Title = element['oldTitle']
                    mp3file["artist"] = song.Artist
                    mp3file["title"] = song.Title
                    if song.Artist == "":
                        song.Artist = "Various"
                    if song.Title == "":
                        song.Title = "Various"
                    mp3file.save(v2_version=3)
                    del dict_list[dict_list.index(element)]
                    break
        if len(dict_list) > 0 :
            message = ""
            for element in dict_list:
                message += element['fileName'] + "\n"
            messagebox.showinfo("Information", "Some files not found within playlist:\n" + message)
        else:
            messagebox.showinfo("Information", "Operation Done\n\nPrevious Artist/Title tags have been restored.")
        self.ArtistTag.delete(0, tk.END)
        self.ArtistTag.insert(0, self.Song.Artist)
        self.TitleTag.delete(0, tk.END)
        self.TitleTag.insert(0, self.Song.Title)
        file = open(self.undoArtistTitleBackupFile, "wb")
        pickle.dump(dict_list, file)
        file.close()

    def renameAllFiles(self):
        dictionary = {}
        dict_list = []
        dict_loaded = False
        if os.path.exists(self.undoRenameBackupFile):
            try:
                file = open(self.undoRenameBackupFile, "rb")
                dict_list = pickle.load(file)
            except Exception:
                dict_list = [] #make sure the list is empty now
                print("Exception when reading the content of File: " + str(self.undoRenameBackupFile))
                print("Since the content has been corrupted, your file will be replaced.")
            else:
                dict_loaded = True
                file.close()
            finally:
                file = open(self.undoRenameBackupFile, "wb")
        else:
            file = open(self.undoRenameBackupFile, "wb")
        for song in play_list.validFiles:
            if song.Artist != "Various" and song.Title != "Various":
                newFileName = song.Artist.strip(" ") + " - " + song.Title.strip(" ") + ".mp3"
                pathToFile = song.filePath.split(song.fileName)
                pathToFile = pathToFile[0]
                alreadyContained = False
                if dict_loaded:
                    for element in dict_list:
                        if element['newName'] == pathToFile + newFileName:
                            alreadyContained = True
                            break
                if alreadyContained == False and os.path.exists(song.filePath):
                    dictionary['oldName'] = song.filePath
                    dictionary['newName'] = pathToFile + newFileName
                    dict_list.append(dictionary)
                    dictionary = {}
                    try:
                        if pygame.mixer.get_init():
                            if play_list.validFiles.index(
                                    song) == play_list.currentSongIndex and pygame.mixer.music.get_busy():  # enter here if the file to be renamed is currently playing
                                play_list.isSongPause = True
                                pygame.mixer.music.stop()
                                shutil.copy(song.filePath,
                                            pathToFile + newFileName)  # make a copy of this file to the project locaiton
                                fileToRemove = song.filePath
                                song.fileName = newFileName  # this will update the play_list with the new song info
                                song.filePath = pathToFile + newFileName
                                pygame.mixer.music.load(
                                    song.filePath)  # load the new file in the player, so that the old one gets released
                                os.remove(fileToRemove)  # remove the old one
                        else:
                            os.rename(song.filePath, pathToFile + newFileName)  # this will rename the file
                            song.fileName = newFileName  # this will update the play_list with the new song info
                            song.filePath = pathToFile + newFileName
                    except Exception as Exp:
                        print("Exception during Mass Rename: " + str(Exp))
        displayElementsOnPlaylist()
        showCurrentSongInList()
        self.NameTag.delete(0, tk.END)
        self.NameTag.insert(0, self.Song.fileName)
        pickle.dump(dict_list, file)
        file.close()
        messagebox.showinfo("Information", "Operation Done\n\nAll files were renamed.")
        if os.path.isfile(self.undoRenameBackupFile) and play_list.useMassFileEditor:
            self.undoMassRenameButton.config(state=tk.NORMAL)
        else:
            self.undoMassRenameButton.config(state=tk.DISABLED)

    def restorePreviousNames (self):
        global play_list
        dict_list=[]
        message = ""
        try:
            file = open(self.undoRenameBackupFile, "rb")
            dict_list = pickle.load(file)
            file.close()
        except Exception as exp:
            dict_list = [] #make sure it's empty
            print("Backup File Exception: " + exp)
            print("File: " + str(self.undoRenameBackupFile)+ " might be corrupted.")
        for song in play_list.validFiles:
            for element in dict_list:
                if element['newName'] == song.filePath:
                    filePath = element['newName'].split(song.fileName)
                    filePath = filePath[0]
                    FileName = element['oldName'].split(filePath)
                    FileName = FileName[1]
                    try:
                        if pygame.mixer.get_init():
                            if play_list.validFiles.index(song) == play_list.currentSongIndex and pygame.mixer.music.get_busy():  # enter here if the file to be renamed is currently playing
                                play_list.isSongPause = True
                                pygame.mixer.music.stop()
                                shutil.copy(song.filePath, element['oldName'])  # make a copy of this file to the project location
                                fileToRemove = song.filePath
                                song.fileName = FileName  # this will update the play_list with the new song info
                                song.filePath = element['oldName']
                                pygame.mixer.music.load(song.filePath)  # load the new file in the player, so that the old one gets released
                                os.remove(fileToRemove)  # remove the old one
                        else:
                            os.rename(song.filePath, element['oldName'])  # this will rename the file
                            song.fileName = FileName  # this will update the play_list with the new song info
                            song.filePath = element['oldName']
                    except Exception as Exp:
                        print("Exception during Undo Mass Rename: " + str(Exp))
                    del dict_list[dict_list.index(element)]
                    break
                if dict_list.index(element) == len(dict_list)-1 and element['newName'] != song.filePath:
                    message += song.fileName + "\n"
        displayElementsOnPlaylist()
        showCurrentSongInList()
        self.NameTag.delete(0, tk.END)
        self.NameTag.insert(0, self.Song.fileName)
        file = open(self.undoRenameBackupFile, "wb")
        pickle.dump(dict_list, file)
        file.close()
        if message!="":
            messagebox.showinfo("Information","Some file were not renamed: \n" + message)
        else:
            messagebox.showinfo("Information","Operation Done\n\nPrevious names have been restored to all files.")
        
    def NameCapitalizer(self):
        if "-" in self.NameTag.get():
            value = self.NameTag.get()
            value = value.split("-")
            artist = ""
            title = ""
            for word in value[0].split(" "):
                artist += word.capitalize() + " "
            for word in value[1].split(" "):
                if value[1].split(" ").index(word) < len(value[1].split(" "))-1:
                    title += word.capitalize() + " "
                else:
                    title += word.capitalize()
            
            if len(value) > 2:
                title+=" "
                for i in range(2, len(value)):
                    title+= value[i].capitalize() + " "
            title = title.strip(" ")  # remove the last blank space
            artist = artist.strip(" ")
            if ".mp3" in title:
                value = artist + " - " +title
            else:
                value = artist + " - " + title + ".mp3"
            self.NameTag.delete(0, tk.END)
            self.NameTag.insert(0, value)
        else:
            value = self.NameTag.get()
            value = value.split(" ")
            newValue = ""
            for element in value:
                newValue += element.strip(" ").capitalize() + " "
            self.NameTag.delete(0, tk.END)
            self.NameTag.insert(0, newValue.rstrip(" ")) 

    def composeArtistTitle(self):
        if self.NameTag.get() != "":
            if "-" in self.NameTag.get():
                value = self.NameTag.get()
                value = value.split("-")
                value[0] = value[0].strip(" ")
                value[0] = [n.capitalize() for n in value[0].split(" ")] #perform Capitalization for Artist Name
                self.ArtistTag.delete(0,tk.END)
                value[0] = " ".join(value[0])
                value[0] = value[0].strip(" ")
                self.ArtistTag.insert(0, value[0])
                self.TitleTag.delete(0, tk.END)
                value[1] = value[1].rstrip(".mp3")
                value[1] = value[1].rstrip(".MP3")
                value[1] = value[1].rstrip(".Mp3")
                value[1] = value[1].rstrip(".mP3")
                value[1] = value[1].strip(" ")
                ##this will perform Capitalization and Semi-Capitalization for the Title
                if len(value[1].split(" ")) > 2:
                    val = value[1][0].capitalize() + value[1][1:].lower()
                    self.TitleTag.insert(0, val)
                else:
                    value[1] = [n.capitalize() for n in value[1].split(" ")]
                    value[1] = " ".join(value[1])
                    self.TitleTag.insert(0, value[1].strip(" "))
            else:
                self.ArtistTag.delete(0, tk.END)
                value = self.NameTag.get().rstrip(".mp3")
                value = self.NameTag.get().rstrip(".mP3")
                value = self.NameTag.get().rstrip(".Mp3")
                value = self.NameTag.get().rstrip(".MP3")
                value = value.strip(" ")
                self.ArtistTag.insert(0, value)
        else:
            messagebox.showinfo("Information", "The name should not be empty.")

    def composeFileName(self):
        if self.ArtistTag.get() != "Various" and self.TitleTag.get() != "Various":
            self.NameTag.delete(0,tk.END)
            self.NameTag.insert(0, self.ArtistTag.get() + " - " + self.TitleTag.get())
        else:
            messagebox.showinfo("Information", "The Artist Name nor the Title should be 'Various'.")

    def NameSemiCapitalizer(self):
        if "-" in self.NameTag.get():
            value = self.NameTag.get()
            value = value.split("-")
            artist = ""
            title = ""
            value[0] = value[0].strip(" ")
            for word in value[0].split(" "):
                artist += word.capitalize() + " "
            value[1] = value[1].strip(" ")
            for word in value[1].split(" "):
                if value[1].split(" ").index(word) == 0:
                    title = word.capitalize() + " "
                else:
                    title += word.lower() + " "
            
            if len(value) > 2:
                for i in range(2, len(value)):
                    title+= value[i].lower() + " "
            title = title.strip(" ") #remove the last blank space
            artist = artist.strip(" ")
            if ".mp3" in title:
                value = artist + " - " +title
            else:
                value = artist + " - " + title + ".mp3"
            self.NameTag.delete(0, tk.END)
            self.NameTag.insert(0, value)
        else:
            value = self.NameTag.get()
            value = value.capitalize()
            self.NameTag.delete(0, tk.END)
            self.NameTag.insert(0, value) 

    def SaveChanges(self):
        global play_list
        pathToFile = self.Song.filePath.split(self.Song.fileName)
        pathToFile = pathToFile[0]
        index = play_list.validFiles.index(self.Song)
        if ".mp3" not in self.NameTag.get().lower():
            value = self.NameTag.get()
            self.NameTag = StringVar()
            self.NameTag.set(value + ".mp3")
        try:
            if pygame.mixer.get_init() and index == play_list.currentSongIndex and pygame.mixer.music.get_busy(): # enter here if the file to be renamed is currently playing
                if play_list.RESUMED:
                    play_list.currentSongPosition = math.floor(play_list.currentSongPosition + pygame.mixer.music.get_pos() / 1000)
                else:
                    play_list.currentSongPosition = math.floor(pygame.mixer.music.get_pos()/1000)
                pygame.mixer.music.stop()
                if self.Song.filePath.lower() != (pathToFile+self.NameTag.get()).lower():
                    shutil.copy(self.Song.filePath, pathToFile+self.NameTag.get())
                    fileToRemove = self.Song.filePath
                    self.Song.fileName = self.NameTag.get()  # this will update the play_list with the new song info
                    self.Song.filePath = pathToFile + self.NameTag.get()
                    self.saveMp3Tags()
                    del play_list.validFiles[play_list.currentSongIndex]
                    play_list.validFiles.insert(play_list.currentSongIndex, self.Song)
                    displayElementsOnPlaylist()
                    showCurrentSongInList()
                    pygame.mixer.music.load(play_list.validFiles[play_list.currentSongIndex].filePath) #release the old file, to be able to remove it
                    os.remove(fileToRemove)  # remove the old one
                    play_music() #load the new file in the player, so that the old one gets released
                else: #will enter here is used Capitalize Filename Option
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("clear.mp3") #use this file to release the playback
                    if self.Song.filePath != pathToFile + self.NameTag.get():
                        os.rename(self.Song.filePath, pathToFile + self.NameTag.get())  # this will rename the file
                        self.Song.fileName = self.NameTag.get()  # this will update the play_list with the new song info
                        self.Song.filePath = pathToFile + self.NameTag.get()
                    self.saveMp3Tags()
                    pygame.mixer.music.load(self.Song.filePath)
                    displayElementsOnPlaylist()
                    showCurrentSongInList()
                    play_music()
            else:
                if self.Song.filePath != (pathToFile + self.NameTag.get()):
                    os.rename(self.Song.filePath, pathToFile + self.NameTag.get()) #this will rename the file
                    self.Song.fileName = self.NameTag.get() # this will update the play_list with the new song info
                    self.Song.filePath = pathToFile + self.NameTag.get()
                self.saveMp3Tags()
                displayElementsOnPlaylist()
                showCurrentSongInList()
        except Exception as Exp:
            print("Exception during File Tag Update: " + str(Exp))

    def saveMp3Tags(self):
        mp3file = EasyID3(self.Song.filePath)
        if self.GenreTag.get() != "Various":
            mp3file["genre"] = self.GenreTag.get()
            self.Song.Genre = mp3file["genre"]
            self.Song.Genre = self.Song.Genre[0]
        if self.ArtistTag.get() != "Various":
            mp3file["artist"] = self.ArtistTag.get()
            self.Song.Artist = mp3file["artist"]
            self.Song.Artist = self.Song.Artist[0]
        if self.AlbumTag.get() != "Various":
            mp3file["album"] = self.AlbumTag.get()
            self.Song.Album = mp3file["album"]
            self.Song.Album = self.Song.Album[0]
        if self.YearTag.get() != "Various":
            mp3file["date"] = self.YearTag.get()
            self.Song.Year = mp3file["date"]
            self.Song.Year = self.Song.Year[0]
        if self.TitleTag.get() != "Various":
            mp3file["title"] = self.TitleTag.get()
            self.Song.Title = mp3file["title"]
            self.Song.Title = self.Song.Title[0]
        mp3file.save(v2_version=3)

    def take_focus(self):
        self.top.wm_attributes("-topmost", 1)
        self.top.grab_set()
        self.NameTag.focus_force()

class GrabLyricsTool(Window):
    def __init__(self, index="empty"):
        global allButtonsFont
        global dialog
        self.LyricsDownloads = "LyricsDownloads.lyl"
        if index=="empty":
            index = play_list.currentSongIndex # do not forget that currentSongIndex can be None
        self.songIndex = index
        if self.songIndex != None: # make sure there is a song to search lyrics for.
            color = OpenFileButton["bg"]  # get the color which the rest of elements is using at the moment
            self.top = tk.Toplevel(window, bg=color)
            Window_Title = "Grab Lyrics Tool"
            self.top.title(Window_Title)
            self.top.geometry("580x550+100+100")
            self.top.protocol("WM_DELETE_WINDOW", self.destroy)
            self.top.attributes('-alpha', play_list.windowOpacity)
            allButtonsFont = skinOptions[2][play_list.skin]
            self.welcomeMessage = StringVar()
            self.welcomeMessage.set("Welcome to Grab Lyrics Tool!\n\nThe lyrics are grabbed from various online sources,\n" \
                                +"the results are provided according to your internet connection speed.\n" \
                                +"The Search is based on Artist - Title tags, if these tags are not set\n" \
                                +"accordingly, the lyrics will never be found.")
            tk.Label(self.top, textvariable=self.welcomeMessage, fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=5, y=5)
            self.Lyrics = StringVar()
            self.Lyrics.set("Lyrics")
            tk.Label(self.top, textvariable=self.Lyrics, fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=5, y=115)
            self.frame = tk.Frame(self.top, width=500, height=30, bg=color, borderwidth=1)
            self.frame.place(x=10, y=135)
            self.scrlbar = tk.Scrollbar(self.frame, orient="vertical", width=10)
            self.listboxLyrics = tk.Listbox(self.frame, fg=fontColor.get(), font=allButtonsFont, width=65, bg=color, height=20, \
                         yscrollcommand=self.scrlbar.set)
            self.listboxLyrics.pack(padx=10, pady=10, side = tk.LEFT)
            self.listboxLyrics.bind('<ButtonPress-3>', self.rightClickOnLyrics)
            self.scrlbar.config(command=self.listboxLyrics.yview)
            self.scrlbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.SaveLyrics = tk.Button(self.top, text="Save Lyrics",command=self.saveLyrics, fg=fontColor.get(), font=allButtonsFont,
                                              bg=color, state=tk.DISABLED)
            self.SaveLyrics.place(x=10,y=500)

            self.RemoveLyrics = tk.Button(self.top, text="Remove Lyrics", command=self.removeLyrics, fg=fontColor.get(),
                                        font=allButtonsFont,
                                        bg=color, state=tk.DISABLED)
            self.RemoveLyrics.place(x=120, y=500)

            self.DownloadLyricsAll = tk.Button(self.top, text="Download All Lyrics", command=self.downloadAllLyrics, fg=fontColor.get(),
                                          font=allButtonsFont,
                                          bg=color)
            self.DownloadLyricsAll.place(x=260, y=500)
            self.top.bind("<Tab>", self.focus_out)
            self.top.bind("<Escape>", self.destroyEsc)
            if os.path.exists(self.LyricsDownloads):
                try:
                    file = open(self.LyricsDownloads, "rb")
                    lyricsList = pickle.load(file)
                    file.close()
                    for element in lyricsList:
                        if element["fileName"] == play_list.validFiles[self.songIndex].fileName:
                            for line in element["lyrics_list"]:
                                self.listboxLyrics.insert(tk.END, line)
                            self.Lyrics.set("Lyrics for '" + play_list.validFiles[self.songIndex].Artist + " - " \
                                            + play_list.validFiles[self.songIndex].Title + "' -> were found locally:")
                            self.RemoveLyrics.config(state=tk.NORMAL)
                            break
                    if self.listboxLyrics.size() == 0: #lyrics not found.
                        self.LyricsDisplay()
                except Exception:
                    print("Could not load the file: " + self.LyricsDownloads)
                    print("I will search for lyrics online.")
                    self.LyricsDisplay()
            else:
                self.LyricsDisplay()
            dialog = self

    def downloadAllLyrics(self):
        for i in range(0, len(play_list.validFiles)):
            self.songIndex = i
            text_list, source = self.accessPage()
            if len(text_list) > 0 and source != "":
                self.saveLyrics(text_list)
            else:
                print("Lyrics not found for: " + play_list.validFiles[self.songIndex].fileName)

    def removeLyrics(self):
        filename = play_list.validFiles[self.songIndex].fileName
        lyrics_dictionary = {}
        lyricsList = []
        if os.path.exists(self.LyricsDownloads):
            try:
                file = open(self.LyricsDownloads, "rb")
                lyricsList = pickle.load(file)
                file.close()
            except Exception:
                print("Could not load the file: " + self.LyricsDownloads)
        if len(lyricsList) > 0:
            for element in lyricsList:
                if element["fileName"] == filename:
                    del lyricsList[lyricsList.index(element)]
                    messagebox.showinfo("Info", "The lyrics for this song were removed.")
                    break
            try:
                file = open(self.LyricsDownloads, "wb")
                pickle.dump(lyricsList, file)
                file.close()
                self.RemoveLyrics.config(state=tk.DISABLED)
                self.SaveLyrics.config(state=tk.NORMAL)
            except Exception:
                print("Could not remove Lyrics for: " + filename)

    def saveLyrics(self, list_text=None):
        filename = play_list.validFiles[self.songIndex].fileName
        lyrics_dictionary = {}
        lyricsList = []
        if os.path.exists(self.LyricsDownloads):
            try:
                file = open(self.LyricsDownloads, "rb")
                lyricsList = pickle.load(file)
                file.close()
            except Exception:
                print("Could not load the file: " + self.LyricsDownloads)
        alreadyContained = False
        if len(lyricsList) > 0:
            for element in lyricsList:
                if element["fileName"] == filename:
                    alreadyContained = True
                    messagebox.showinfo("Info", "This lyrics are already stored in your local computer.")
                    break
        if alreadyContained == False:
            lyrics_dictionary["fileName"] = filename
            if list_text == None:
                lyrics_dictionary["lyrics_list"] = list(self.listboxLyrics.get(0,tk.END))
            else:
                lyrics_dictionary["lyrics_list"] = list_text
            lyricsList.append(lyrics_dictionary)
            lyrics_dictionary={}
            del lyrics_dictionary
            try:
                file = open(self.LyricsDownloads, "wb")
                pickle.dump(lyricsList, file)
                file.close()
                self.RemoveLyrics.config(state=tk.NORMAL)
            except Exception:
                print("Could not save Lyrics for: " + filename)

    def accessPage(self):
        urllib3.disable_warnings()
        text_list = []
        source = ""
        if play_list.validFiles[self.songIndex].Artist != "Various" and play_list.validFiles[
            self.songIndex].Title != "Various":
            artist = play_list.validFiles[self.songIndex].Artist
            artist = artist.replace("'", "")
            artist = artist.replace(",", "")
            artist = artist.replace(":", "")
            artist = artist.replace(".", "")
            artist = artist.replace("!", "")
            artist = artist.replace("%", "")
            artist = artist.replace("?", "")
            artist = artist.replace("`", "")
            artist = artist.replace("`", "")
            artist = artist.replace(" & ", " and ")
            artist = artist.replace("&", " and ")
            artist = artist.replace(" ", "-")
            title = play_list.validFiles[self.songIndex].Title
            title = title.replace("'", "")
            title = title.replace(",", "")
            title = title.replace(":", "")
            title = title.replace(".", "")
            title = title.replace("!", "")
            title = title.replace("%", "")
            title = title.replace("?", "")
            title = title.replace("`", "")
            title = title.replace("&", "")
            title = title.replace(".mp3", "")
            title = title.replace(".MP3", "")
            title = title.replace(".mP3", "")
            title = title.replace(".Mp3", "")
            title = title.replace(" ", "-")

            if play_list.LyricsActiveSource == "lyrics.my" or (play_list.LyricsActiveSource == "all" and len(text_list)==0):
                url = "http://www.lyrics.my/artists/" + artist + "/lyrics/" + title  # this is possible to change with time. Let's hope it doesn't
                http = urllib3.PoolManager()
                try:
                    response = http.request('GET', url)
                except NewConnectionError as exp:    # This is the correct syntax
                    print("Unable to establish connection to the server: lyrics.my")
                    print("Error Message: " + str(exp))
                    print("Please check your internet connection before proceed.")
                except Exception:
                    print("An exception has been handled. I am sorry but I'm unable to retrieve lyrics.")
                    print("Please check your internet connection before proceed.")
                else:
                    if response.status == 200:
                        text_list = self.filterTextFromLyricsMy(response.data)
                        source = "lyrics.my"
            if play_list.LyricsActiveSource == "genius.com" or (play_list.LyricsActiveSource == "all" and len(text_list)==0):
                url = "https://genius.com/" + artist + "-" + title + "-lyrics"  # this is possible to change with time. Let's hope it doesn't
                # The URL system for genius.com is structured like this at the moment.
                http = urllib3.PoolManager()
                try:
                    response = http.request('GET', url)
                except NewConnectionError as exp:    # This is the correct syntax
                    print("Unable to establish connection to the server: genius.com")
                    print("Error Message: " + str(exp))
                    print("Please check your internet connection before proceed.")
                except Exception:
                    print("An exception has been handled. I am sorry but I'm unable to retrieve lyrics.")
                    print("Please check your internet connection before proceed.")
                else:
                    if response.status == 200:
                        text_list = self.filterTextFromGeniusCom(response.data)
                        source = "genius.com"
            if play_list.LyricsActiveSource == "lyricsmix.net" or (play_list.LyricsActiveSource == "all" and len(text_list)==0):
                url = "https://lyricsmix.net/" + artist + "-" + title + "-lyrics/"  # this is possible to change with time. Let's hope it doesn't
                http = urllib3.PoolManager()
                try:
                    response = http.request('GET', url)
                except NewConnectionError as exp:    # This is the correct syntax
                    print("Unable to establish connection to the server: lyricsmix.net")
                    print("Error Message: " + str(exp))
                    print("Please check your internet connection before proceed.")
                except Exception:
                    print("An exception has been handled. I am sorry but I'm unable to retrieve lyrics.")
                    print("Please check your internet connection before proceed.")
                else:
                    if response.status == 200:
                        text_list = self.filterTextFromLyricsMixNet(response.data)
                        source = "lyricsmix.net"
            if play_list.LyricsActiveSource == "omnialyrics.it" or (play_list.LyricsActiveSource == "all" and len(text_list)==0):
                url = "https://omnialyrics.it/" + title + "-testo-" + artist +"/"  # this is possible to change with time. Let's hope it doesn't
                http = urllib3.PoolManager()
                try:
                    response = http.request('GET', url)
                except NewConnectionError as exp:    # This is the correct syntax
                    print("Unable to establish connection to the server: omnialyrics.it")
                    print("Error Message: " + str(exp))
                    print("Please check your internet connection before proceed.")
                except Exception:
                    print("An exception has been handled. I am sorry but I'm unable to retrieve lyrics.")
                    print("Please check your internet connection before proceed.")
                else:
                    if response.status == 200:
                        text_list = self.filterTextFromOmniaLyricsIt(response.data)
                        source = "omnialyrics.it"
        return text_list, source

    def filterTextFromOmniaLyricsIt(self, data):
        text = BeautifulSoup(data, "html.parser")
        text = text.decode("utf-8")
        list_text = []
        # Start filtering the html content of the webpage
        if '<div class="article">' in text:  # if this is not found on the page, probably there are no lyrics yet.
            text = text.split('<div class="article">')
            text = text[1].split('</div>')
            text = text[0]
            text = text.replace("   ", "")
            text = text.replace("\n ", "\n")
            text = text.replace('<p>', "")
            text = text.replace('</p>', "")
            text = text.replace("<b>", "")
            text = text.replace("</b>", "")
            text = text.replace("<i>", "")
            text = text.replace("</i>", "")
            text = text.replace("<h2>", "")
            text = text.replace("</h2>", "")
            text = text.replace("<br>", "")
            text = text.replace("<br/>", "")
            text = text.replace("</strong>", "")
            text = text.replace("<strong>", "")
            text = text.replace("[", "")
            text = text.replace("]", "")
            if "<iframe" in text:
                text = text.split("<iframe")
                text = text[0]
            newText = ""
            for i in range(0, len(text)):
                if (text[i] >= "A" and text[i] <= "Z") or (text[i] >= "a" and text[i] <= "z") or (
                                text[i] >= "0" and text[i] <= "9"):
                    newText += text[i]
                elif text[i] == "\n":
                    if newText != "":
                        list_text.append("    " + newText)
                        newText = ""
                    if text[i - 1] == "\n" and text[i] == "\n" and text[i - 2] == "\n" and i > 3:
                        list_text.append("")
                elif i > 0:
                    if (text[i - 1] >= "A" and text[i - 1] <= "Z") or (text[i - 1] >= "a" and text[i - 1] <= "z") \
                            or text[i - 1] == "," or text[i - 1] == ".":  # this is for word spacing.
                        newText += text[i]
        return list_text

    def filterTextFromLyricsMixNet(self, data):
        text = BeautifulSoup(data, "html.parser")
        text = text.decode("utf-8")
        list_text = []
        # Start filtering the html content of the webpage
        if '<div class="entry-content">' in text:  # if this is not found on the page, probably there are no lyrics yet.
            text = text.split('<div class="entry-content">')
            text = text[1].split('<!-- lyrics_afte_post -->')
            text = text[0]
            text = text.replace("   ", "")
            text = text.replace("\n ", "\n")

            text = text.replace('<p style="text-align: center;">', "")
            text = text.replace('<p>', "")
            text = text.replace('</p>', "")
            text = text.replace("<b>", "")
            text = text.replace("</b>", "")
            text = text.replace("<i>", "")
            text = text.replace("</i>", "")
            text = text.replace("</p>", "")
            text = text.replace("<br>", "")
            text = text.replace("<br/>", "")
            text = text.replace("[", "")
            text = text.replace("]", "")
            if "<script " in text:
                text = text.split("<script ")
                text=text[0]
            if "</iframe>" in text:
                text = text.split("</iframe>")
                text = text[1]
            newText = ""
            for i in range(0, len(text)):
                if (text[i] >= "A" and text[i] <= "Z") or (text[i] >= "a" and text[i] <= "z") or (
                                text[i] >= "0" and text[i] <= "9"):
                    newText += text[i]
                elif text[i] == "\n":
                    if newText != "":
                        list_text.append("    " + newText)
                        newText = ""
                    if text[i - 1] == "\n" and text[i] == "\n" and text[i - 2] == "\n" and text[i - 3] == "\n" and i > 3:
                        list_text.append("")
                elif i > 0:
                    if (text[i - 1] >= "A" and text[i - 1] <= "Z") or (text[i - 1] >= "a" and text[i - 1] <= "z") \
                            or text[i - 1] == "," or text[i - 1] == ".":  # this is for word spacing.
                        newText += text[i]
        return list_text

    def filterTextFromGeniusCom(self, data):
        text = BeautifulSoup(data, "html.parser")
        text = text.decode("utf-8")
        list_text = []
        # Start filtering the html content of the webpage
        if '<div class="lyrics">' in text: # if this is not found on the page, probably there are no lyrics yet.
            text = text.split('<div class="lyrics">')
            text = text[1].split('</div>')
            text = text[0]
            text = text.replace("   ", "")
            text = text.replace("\n ", "\n")

            text = text.replace("<p>", "")
            text = text.replace("<b>", "")
            text = text.replace("</b>", "")
            text = text.replace("<i>", "")
            text = text.replace("</i>", "")
            text = text.replace("<!--sse-->", "")
            text = text.replace("<!--/sse-->", "")
            text = text.replace("</p>", "")
            text = text.replace("<br>", "")
            text = text.replace("<br/>", "")
            text = text.replace("[", "")
            text = text.replace("]", "")

            if "<a annotation-fragment" in text:  # if there are any adds between these lyrics, lets remove them.
                text = text.split("<a annotation-fragment=")
                aux = []
                for element in text:
                    if 'prevent-default-click="">' in element:
                        element = element.split('prevent-default-click="">')
                        aux.append(element[1])
                    else:
                        aux.append(element)
                text = "".join(aux)
                text = text.replace("</a>", "")

            newText = ""
            for i in range(0, len(text)):
                if (text[i] >= "A" and text[i] <= "Z") or (text[i] >= "a" and text[i] <= "z") or (
                        text[i] >= "0" and text[i] <= "9"):
                    newText += text[i]
                elif text[i] == "\n":
                    if newText != "":
                        list_text.append("    " + newText)
                        newText = ""
                    if text[i - 1] == "\n" and text[i] == "\n" and text[i - 2] == "\n" and i > 3:
                        list_text.append("")
                elif i > 0:
                    if (text[i - 1] >= "A" and text[i - 1] <= "Z") or (text[i - 1] >= "a" and text[i - 1] <= "z") \
                            or text[i - 1] == "," or text[i - 1] == ".":  # this is for word spacing.
                        newText += text[i]
        return list_text

    def filterTextFromLyricsMy(self, data):
        text = BeautifulSoup(data, "html.parser")
        text = text.decode("utf-8")
        list_text = []
        # Start filtering the html content of the webpage
        if '<div class="show_lyric">' in text: # if this is not found on page, it means there are no lyrics
            text = text.split('<div class="show_lyric">')
            text = text[1].split('</div>')
            text = text[0]
            text = text.replace("   ", "")
            text = text.replace("\n ", "\n")

            text = text.replace("<p>", "")
            text = text.replace("<b>", "")
            text = text.replace("</b>", "")
            text = text.replace("<i>", "")
            text = text.replace("</i>", "")
            text = text.replace("</p>", "")
            text = text.replace("<br>", "")
            text = text.replace("</br>", "")
            text = text.replace("<br/>", "")
            text = text.replace("[", "(")
            text = text.replace("]", ")")
            newText = ""
            for i in range(0, len(text)):
                if (text[i] >= "A" and text[i] <= "Z") or (text[i] >= "a" and text[i] <= "z") or (
                        text[i] >= "0" and text[i] <= "9") or text[i] == "(" or text[i] == ")":
                    newText += text[i]
                elif text[i] == "\n":
                    if newText != "":
                        list_text.append("    " + newText)
                        newText = ""
                    if newText =="" and len(list_text)>1 and list_text[(len(list_text)-1)]!="" and list_text[(len(list_text)-2)]!="":
                        list_text.append("")
                elif i > 0:
                    if (text[i - 1] >= "A" and text[i - 1] <= "Z") or (text[i - 1] >= "a" and text[i - 1] <= "z") \
                            or text[i - 1] == "," or text[i - 1] == "." or text[i - 1] == "?" or text[i - 1] == "!":  # this is for word spacing.
                        newText += text[i]
        return list_text

    def LyricsDisplay(self): #to be continued
        text_list, source = self.accessPage()
        if len(text_list) > 0:
            self.Lyrics.set("Lyrics for '" + play_list.validFiles[self.songIndex].Artist + " - " \
                            + play_list.validFiles[self.songIndex].Title + "' -> were found on " + source + ":")
            for element in text_list:
                self.listboxLyrics.insert(tk.END, element)
                if len(element) > 55 and len(element) > self.listboxLyrics["width"]:  # this will resize the window and the listbox to fit the lyrics.
                    listboxX = len(element) - 55
                    windowX = 580 + (listboxX * 10)  # 580 is the initial value of the window
                    listboxX += 65  # 65 is the initial width of the listbox
                    self.top.geometry(str(windowX) + "x550+100+100")
                    self.listboxLyrics["width"] = listboxX
            self.SaveLyrics.config(state=tk.NORMAL)
        else:
            self.Lyrics.set("Lyrics for '" + play_list.validFiles[self.songIndex].Artist + " - " \
                            + play_list.validFiles[self.songIndex].Title + "' -> were NOT found!\n" +
                            "Make sure you have Artist and Title Tags completed properly.")
        
    def copy_to_clipboard(self, event, value):
        self.top.clipboard_clear() 
        self.top.clipboard_append(value)
    
    def rightClickOnLyrics(self, event):
        listboxSelectedEvent = event.widget
        if len(listboxSelectedEvent.curselection()) > 0:
            index = int(listboxSelectedEvent.curselection()[0])
            value = self.listboxLyrics.get(index)
            aMenu = tk.Menu(window, tearoff=0)
            aMenu.add_command(label='Copy All', command= lambda: self.copy_to_clipboard("<ButtonPress-3>", "\n".join(self.listboxLyrics.get(0, tk.END))))
            if value!="":
                aMenu.add_command(label='Copy Line', command= lambda: self.copy_to_clipboard("<ButtonPress-3>", value))
            aMenu.post(event.x_root, event.y_root)
    
class GrabArtistBio(Window):
    def __init__(self, index="empty"):
        global allButtonsFont
        global dialog
        self.LyricsDownloads = "LyricsDownloads.lyl"
        if index == "empty":
            index = play_list.currentSongIndex  # do not forget that currentSongIndex can be None
        self.songIndex = index
        if self.songIndex != None:  # make sure there is a song to search lyrics for.
            color = OpenFileButton["bg"]  # get the color which the rest of elements is using at the moment
            self.top = tk.Toplevel(window, bg=color)
            Window_Title = "Artist Bio"
            self.top.title(Window_Title)
            self.top.geometry("490x350+100+100")
            self.top.protocol("WM_DELETE_WINDOW", self.destroy)
            self.top.attributes('-alpha', play_list.windowOpacity)
            allButtonsFont = skinOptions[2][play_list.skin]
            self.Message = StringVar()
            self.Message.set("According to LastFM:\n\n")
            tk.Label(self.top, textvariable=self.Message, fg=fontColor.get(), font=allButtonsFont,
                     bg=color).place(x=5, y=5)
            self.BioText = StringVar()
            self.BioText.set("Artist Bio:")
            tk.Label(self.top, textvariable=self.BioText, fg=fontColor.get(), font=allButtonsFont, bg=color).place(x=15, y=45)
            self.frame = tk.Frame(self.top, width=100, height=30, bg=color, borderwidth=1)
            self.frame.place(x=5, y=65)
            self.scrlbar = tk.Scrollbar(self.frame, orient="vertical", width=10)
            self.listboxLyrics = tk.Listbox(self.frame, fg=fontColor.get(), font=allButtonsFont, width=55, bg=color,
                                            height=15, \
                                            yscrollcommand=self.scrlbar.set)
            self.listboxLyrics.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.X)
            self.listboxLyrics.bind('<ButtonPress-3>', self.rightClickOnLyrics)
            self.scrlbar.config(command=self.listboxLyrics.yview)
            self.scrlbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.ArtistBioDisplay()
            self.top.bind("<Tab>", self.focus_out)
            self.top.bind("<Escape>", self.destroyEsc)
            dialog = self

    def accessPage(self):
        urllib3.disable_warnings()
        text_list = []
        if play_list.validFiles[self.songIndex].Artist != "Various":
            artist = play_list.validFiles[self.songIndex].Artist
            artist = artist.replace("'", "")
            artist = artist.replace(",", "")
            artist = artist.replace(":", "")
            artist = artist.replace(".", "")
            artist = artist.replace("!", "")
            artist = artist.replace("%", "")
            artist = artist.replace("?", "")
            artist = artist.replace("`", "")
            artist = artist.replace("`", "")
            artist = artist.replace(" & ", " and ")
            artist = artist.replace("&", " and ")
            artist = artist.replace(".mp3", "")
            artist = artist.replace(".MP3", "")
            artist = artist.replace(".mP3", "")
            artist = artist.replace(".Mp3", "")
            artist = artist.replace(" ", "+")
            url = "https://www.last.fm/music/" + artist + "/+wiki" # this is possible to change with time. Let's hope it doesn't
            http = urllib3.PoolManager()
            try:
                response = http.request('GET', url)
            except NewConnectionError as exp:  # This is the correct syntax
                print("Unable to establish connection to the server: last.fm")
                print("Error Message: " + str(exp))
                print("Please check your internet connection before proceed.")
            except Exception:
                print("An exception has been handled. I am sorry but I'm unable to retrieve info.")
            else:
                if response.status == 200:
                    text_list = self.filterTextFromLastFM(response.data)
        return text_list

    def filterTextFromLastFM(self, data):
        text = BeautifulSoup(data, "html.parser")
        text = text.decode("utf-8")
        list_text = []
        # Start filtering the html content of the webpage
        if '<div class="wiki-content" itemprop="description">' in text: # if condition not fulfilled it means the artist is on lastFM but nothing was written about him.
            text = text.split('<div class="wiki-content" itemprop="description">')
            text = text[1].split('</div>')
            text = text[0]
            text = text.replace("   ", "")

            text = text.replace("<a>", "")
            text = text.replace("</a>", "")
            text = text.replace("<b>", "")
            text = text.replace("</b>", "")
            text = text.replace("<p>", "")
            text = text.replace("</p>", "")
            text = text.replace("<strong>", "")
            text = text.replace("</strong>", "")
            text = text.replace("</br>", "")
            text = text.replace("<br/>", "")
            text = text.replace("<br>", "")
            text = text.replace("<em>", "")
            text = text.replace("</em>", "")
            text = text.replace("<i>", "")
            text = text.replace("</i>", "")
            if "<a " in text:  # if there are any adds between these lyrics, lets remove them.
                text = text.split("<a ")
                aux = []
                for element in text:
                    if '">' in element:
                        element = element.split('">')
                        aux.append(element[1] + " ")
                    else:
                        aux.append(element)
                text = "".join(aux)
                text = text.replace("</a>", "")
            if "<sup " in text:  # if there are any adds between these lyrics, lets remove them.
                text = text.split("<sup ")
                aux = []
                for element in text:
                    if '</sup>' in element:
                        element = element.split('</sup>')
                        aux.append(element[1])
                    else:
                        aux.append(element)
                text = "".join(aux)
                text = text.replace("</a>", "")
            newText = ""
            splitParagraph = False
            for i in range(0, len(text)):
                if text[i] != "\n":
                    newText += text[i]
                if (text[i] == "." and i < len(text)-1 and text[i+1]==" ") and (len(list_text)%5==0 or splitParagraph): #make a new paragraph after each 5 sentences.
                    list_text.append("  " + newText)
                    newText = ""
                    list_text.append("") #add an empty line
                elif len(newText)>=45 and (text[i]==" " or text[i] =="-"):
                    list_text.append("  " +newText)
                    newText=""
                if len(list_text) % 5 > 0 and len(list_text) % 5 < 3 and len(list_text) > 5:
                    splitParagraph = True
            if newText!="":
                list_text.append("  " +newText)
                newText=""
        return list_text

    def ArtistBioDisplay(self): #to be continued
        text_list = self.accessPage()
        if len(text_list) > 0:
            for element in text_list:
                self.listboxLyrics.insert(tk.END, element)
        else:
            self.listboxLyrics.insert(tk.END, "No information found")
    
    def copy_to_clipboard(self, event, value):
        self.top.clipboard_clear() 
        self.top.clipboard_append(value)
    
    def rightClickOnLyrics(self, event):
        listboxSelectedEvent = event.widget
        if len(listboxSelectedEvent.curselection()) > 0:
            index = int(listboxSelectedEvent.curselection()[0])
            value = self.listboxLyrics.get(index)
            aMenu = tk.Menu(window, tearoff=0)
            aMenu.add_command(label='Copy All', command= lambda: self.copy_to_clipboard("<ButtonPress-3>", "\n".join(self.listboxLyrics.get(0, tk.END))))
            if value!="":
                aMenu.add_command(label='Copy Line', command= lambda: self.copy_to_clipboard("<ButtonPress-3>", value))
            aMenu.post(event.x_root, event.y_root)
  
automaticallyBackupFile = "PlayListBackup.pypl"
allButtonsWidth = 14
allButtonsHeight = 1

LyricsOnlineSources = ["all", "genius.com", "lyrics.my", "lyricsmix.net", "omnialyrics.it"]

custom_color_list = ["green", "yellow", "purple", "black", "brown", "sienna", "cyan", "magenta", "pink", "blue", "darkblue", "darkgreen", "deeppink", "red", \
                                            "orange", "gold", "silver", "indigo"]

radioButtonsDefaultColor = "lightgray"

custom_font_list = ["Arial 10", "Consolas 10", "Courier 9", "Verdana 9", "Georgia 9", "Tahoma 9", "Rockwell 10", "Fixedsys 11", "Candara 10", "Impact 9", \
                                    "Calibri 10 italic", "Modern 10 bold", "Harrington 10 bold", "Stencil 10 italic", "Forte 10", "System 11", "Times 11", \
                                    "Unispace 9", "Stencil 9", "Haettenschweiler 12"]
progressViewRealTime = 0.8 #0.8 - for 0.8 second
play_list = Playlist()

listBox_Song_selected_index = None
APPLICATION_EXIT = False
skinOptions = [["default.gif", "minilights.gif", "road.gif", "darkg.gif", "leaves.gif", "darkblue.gif", "map.gif", "space.gif", "universe.gif"],\
               ["blue", "red", "gray", "green", "deeppink", "darkblue", "sienna", "indigo", "black", "custom"],\
               ["Consolas 10 bold", "Rockwell 10 bold", "Arial 10 italic", "Candara 10 bold", "Arial 10 bold", "Calibri 10 bold", "Harrington 10 bold", "Fixedsys 11", "Stencil 10"]]

progressBarMargin = 10

SongStatsFileName = "SongStats.sts"

visualSongNameLabel = None

allButtonsFont = skinOptions[2][play_list.skin] #default Font value Arial 10 bold:
#default value of play_list.skin is 0
dialog = None

s_rate = None
channels = None
temp_SongEndPos = None #this variable will only be used when CrossFade is enabled.

def load_file(): #this function is called when clicking on Open File Button.
    global play_list
    global listBox_Song_selected_index
    fileToPlay = filedialog.askopenfilenames(initialdir = "/",title = "Select file",filetypes = (("mp3 files","*.mp3"),("pypl files","*.pypl"),("all files","*.*")))
    if fileToPlay:
        fileToPlay = list(fileToPlay)
        startIndex = len(play_list.validFiles)
        for file in fileToPlay:
            if ".mp3" in file.lower():
                fileName = re.split("/", file)
                fileName = fileName[len(fileName) - 1]
                fileSize = os.path.getsize(file) / (1024 * 1024)
                fileSize = float("{0:.2f}".format(fileSize))
                song = Song(fileName, file, fileSize)
                play_list.validFiles.append(song)
                play_list.currentSongIndex = 0
                listBox_Song_selected_index = 0
                SongName.set("Paused: " + play_list.validFiles[play_list.currentSongIndex].fileName)
                textFilesToPlay.set("Files: " + str(len(play_list.validFiles)))
                play_list.playTime += play_list.validFiles[play_list.currentSongIndex].Length
            elif ".pypl" in file:
                loadPlaylistFile(file)
                break
        displayElementsOnPlaylist()
        showCurrentSongInList()
        play_list.isListOrdered = 17 #this will mean Custom Sorting
        updateSortButton()
        if play_list.keepSongsStats:
            loadSongStats(startIndex)

def loadPlaylistFile(fileURL): #this function is called at startup if there is a backup Playlist file -> automaticallyBackupFile.
    global play_list
    global allButtonsFont
    global fontColor
    global custom_color_list
    global listBox_Song_selected_index
    try:
        file = open(fileURL, "rb")
        content = pickle.load(file)
        file.close()
    except Exception as exp:
        print("Load Playlist File Exception: " + str(exp))
        print("File: " + str(fileURL)+ " might be corrupted.")
    else:
        if isinstance(content, Playlist):
            play_list = content
            del content
            textFilesToPlay.set("Files: " + str(len(play_list.validFiles)))
            custom_color_list += play_list.userCreatedColors
            if play_list.listboxWidth != "Auto":
                listbox["width"] = play_list.listboxWidth
                if play_list.listboxWidth < 75:
                    value = (75 - play_list.listboxWidth)// 5 #value shoud be between 0 and 2
                    MoveUpButton["width"] -= value
                    MoveDownButton["width"] -= value
                    RemoveSongButton["width"] -= value
                    SortListButton["width"] -= value
            buttonAdjustments()
            reSpacePositionElements()  # respace elements
            if play_list.customBackgroundPicture!=None: #this will load the custom background
                if os.path.exists(play_list.customBackgroundPicture):
                    if ".gif" in play_list.customBackgroundPicture:
                        background_image = tk.PhotoImage(file=play_list.customBackgroundPicture)
                        background_label.configure(image=background_image)
                        background_label.image = background_image
                    elif ".jpg" in play_list.customBackgroundPicture or ".jpeg" in play_list.customBackgroundPicture or ".png" in play_list.customBackgroundPicture:
                        img = ImageTk.PhotoImage(Image.open(play_list.customBackgroundPicture))
                        background_label.configure(image=img)
                        background_label.image = img
                else:
                    print("I was not able to load the background image: " + str(play_list.customBackgroundPicture))
                    print("The file could not be found.")
            #Enter here if the skin was not customized, and put the predefined skin.
            if play_list.customElementBackground == None and play_list.customLabelBackground == None and play_list.customFont == None \
                    and play_list.customBackgroundPicture==None and play_list.customChangeBackgroundedLabelsColor == None and \
                            play_list.customFontColor == None:
                SkinColor.set(skinOptions[1][play_list.skin])
                changeSkin("<Double-Button>")
            else: #enter here is the skin was customized
                if play_list.customElementBackground != None:
                    SkinColor.set(custom_color_list[play_list.customElementBackground])
                else:
                    SkinColor.set(skinOptions[1][play_list.skin]) #predefined skin color
                
                if play_list.customLabelBackground!= None:
                    labelBackground.set(custom_color_list[play_list.customLabelBackground])
                else:
                    labelBackground.set("lightgray")  # default value
                
                if play_list.customFont != None:
                    allButtonsFont = custom_font_list[play_list.customFont]
                else:
                    allButtonsFont = skinOptions[2][play_list.skin]
                
                if play_list.customFontColor != None:
                    fontColor.set(custom_color_list[play_list.customFontColor])
                else:
                    fontColor.set("white")  # default value
                changingBackgroundElementColor("<<ComboboxSelected>>")
                changingLabelBackgroundColor("<<ComboboxSelected>>")
                changeFonts()
                changingFontColor("<<ComboboxSelected>>")
            if play_list.customChangeBackgroundedLabelsColor != None: 
                changingBackgroundedLabelsColor("not important") #the parameter will not be used in this context
                #this function will invert the colors of the labels. when hitting the Radiobutton True in Customize Tool.
            displayElementsOnPlaylist()
            if play_list.currentSongIndex != None and len(play_list.validFiles) > 0:
                SongName.set("Paused: " + play_list.validFiles[play_list.currentSongIndex].fileName)
                SongSize.set("Size: " + str(play_list.validFiles[play_list.currentSongIndex].fileSize) + " MB")
                if play_list.progressTime == "Ascending":
                    SongDuration.set("Time Elapsed: {:0>8}".format(str(datetime.timedelta(seconds=play_list.currentSongPosition))))
                else:
                    SongLength = int(play_list.validFiles[play_list.currentSongIndex].Length - play_list.currentSongPosition)
                    SongDuration.set("Time Left: {:0>8}".format(str(datetime.timedelta(seconds=SongLength))))
                #Update Length
                songLength = float("{0:.0f}".format(play_list.validFiles[play_list.currentSongIndex].Length))  # no decimals needed
                textLength.set("Length: {:0>8}".format(str(datetime.timedelta(seconds=songLength))))
                textGenre.set("Genre: " + str(play_list.validFiles[play_list.currentSongIndex].Genre))
                textArtist.set("Artist: " + str(play_list.validFiles[play_list.currentSongIndex].Artist))
                textAlbum.set("Album: " + str(play_list.validFiles[play_list.currentSongIndex].Album))
                textTitle.set("Title: " + str(play_list.validFiles[play_list.currentSongIndex].Title))
                textYear.set("Year: " + str(play_list.validFiles[play_list.currentSongIndex].Year))
                textSongListenedTime.set("Song Listened Time: {:0>8}" .format(str(datetime.timedelta(seconds=int(play_list.validFiles[play_list.currentSongIndex].SongListenedTime)))))
                textPlaylistListenedTime.set("Playlist Listened Time: {:0>8}" .format(str(datetime.timedelta(seconds=int(play_list.PlaylistListenedTime)))))
                startPos = int(play_list.validFiles[play_list.currentSongIndex].startPos)
                textStartTime.set("Start Time: {:0>8}".format(str(datetime.timedelta(seconds=startPos))))
                endPos = int(play_list.validFiles[play_list.currentSongIndex].endPos)
                textEndTime.set("End Time: {:0>8}".format(str(datetime.timedelta(seconds=endPos))))
                textFadeIn.set("FadeIn: " + str(play_list.validFiles[play_list.currentSongIndex].fadein_duration)+"s")
                textFadeOut.set("FadeOut: " + str(play_list.validFiles[play_list.currentSongIndex].fadeout_duration) +"s")
                mode = "Stereo" if play_list.validFiles[play_list.currentSongIndex].channels == 2 else "Mono"
                textMonoStereoMode.set("Mode: " + mode)
                textNofPlays.set("No. of Plays: " + str(play_list.validFiles[play_list.currentSongIndex].NumberOfPlays))
                textSampleRate.set("Sample Rate: " + str(play_list.validFiles[play_list.currentSongIndex].sample_rate))
                textTotalPlayTime.set("PlayTime: {:0>8}" .format(str(datetime.timedelta(seconds=int(play_list.playTime)))))
                danMode = "ON" if play_list.danthologyMode == True else "OFF"
                textDanthologyMode.set("Danthology Mode: " + danMode)
                VolumeScale.set(play_list.VolumeLevel*100) #put the volume level on the scale.
                updateRadioButtons()
            updateSortButton()
            progress["mode"] = play_list.ProgressBarType
            window.attributes('-alpha', play_list.windowOpacity) #set the opacity
            changePlaylistView()
            showCurrentSongInList()
            if play_list.SHUFFLE:
                ShuffleButtonText.set("Shuffle On")
            if play_list.REPEAT == 0:
                RepeatButtonText.set("Repeat Off")
            elif play_list.REPEAT == 1:
                RepeatButtonText.set("Repeat All")
            elif play_list.REPEAT == 2:
                RepeatButtonText.set("Repeat One")
            elif play_list.REPEAT == 3:
                RepeatButtonText.set("Repeat None")
            return True
        else:
            print("Playlist file has been corrupted.")
            return False  
            
def load_directory(): #this function is called when clicking on Open Directory Button.
    global play_list
    global listBox_Song_selected_index
    play_list.dirFilePath = filedialog.askdirectory()
    if play_list.dirFilePath:
        startIndex = len(play_list.validFiles)
        searchFilesInDirectories(play_list.dirFilePath)
        play_list.currentSongIndex = 0
        play_list.currentSongPosition = 0
        textFilesToPlay.set("Files: " + str(len(play_list.validFiles)))
        if play_list.keepSongsStats:
            loadSongStats(startIndex)
        displayElementsOnPlaylist()
        showCurrentSongInList()
        SongName.set("Paused: " + play_list.validFiles[play_list.currentSongIndex].fileName)
        play_list.isListOrdered = 17 #this will mean Custom Sorting
        updateSortButton()

def searchFilesInDirectories(dir): #this function is called when loading a directory.
    global play_list
    for root, dirs, files in os.walk(dir):
        for file in files:
            if ".mp3" in file.lower():
                fileSize = os.path.getsize(root + "/" + file) / (1024 * 1024)
                fileSize = float("{0:.2f}".format(fileSize))
                song = Song(file, root + "/" + file, fileSize)
                play_list.validFiles.append(song)
                play_list.playTime += song.Length

def play_music(): #this function is called when clicking on Play Button.
    global play_list
    global visualSongNameLabel
    global s_rate
    global channels
    global temp_SongEndPos
    if len(play_list.validFiles) > 0 and play_list.currentSongIndex!=None:
        try:
            if s_rate != play_list.validFiles[play_list.currentSongIndex].sample_rate or channels != play_list.validFiles[play_list.currentSongIndex].channels \
                    or s_rate == None or channels == None:
                s_rate = play_list.validFiles[play_list.currentSongIndex].sample_rate
                channels = play_list.validFiles[play_list.currentSongIndex].channels
                if pygame.mixer.get_init():
                    pygame.mixer.quit() # quit it, to make sure it is reinitialized
                    pygame.mixer.pre_init(frequency=s_rate, size=-16, channels=channels, buffer=4096)
                else:
                    pygame.mixer.pre_init(frequency=s_rate, size=-16, channels=channels, buffer=4096)
                pygame.mixer.init()
            if play_list.useCrossFade == True and play_list.currentSongPosition <= play_list.validFiles[play_list.currentSongIndex].startPos :
                #let the next song start from seconds stored in play_list.crossFadeGap
                play_list.currentSongPosition = play_list.crossFadeGap

                play_list.validFiles[play_list.currentSongIndex].fadein_duration = play_list.crossFadeDuration
                play_list.validFiles[play_list.currentSongIndex].fadeout_duration = play_list.crossFadeDuration
                temp_SongEndPos = play_list.validFiles[play_list.currentSongIndex].endPos
                play_list.validFiles[play_list.currentSongIndex].endPos = (play_list.validFiles[play_list.currentSongIndex].Length - play_list.crossFadeGap*3)
            if (play_list.validFiles[play_list.currentSongIndex].fadein_duration == 0  \
                    or play_list.currentSongPosition > play_list.validFiles[play_list.currentSongIndex].fadein_duration): 
                pygame.mixer.music.set_volume(play_list.VolumeLevel) # you can set the Volume
            else: # enter here if song uses fadein
                pygame.mixer.music.set_volume(0.0) #the volume will start from 0.0 and will increase progressively
            if listBox_Song_selected_index != None and type(dialog) != SearchTool:
                if listBox_Song_selected_index != play_list.currentSongIndex:
                    play_list.currentSongIndex = listBox_Song_selected_index
                    play_list.currentSongPosition = play_list.validFiles[play_list.currentSongIndex].startPos
                    play_list.RESUMED = False
                showCurrentSongInList()
            elif listBox_Song_selected_index == play_list.currentSongIndex and type(dialog) == SearchTool:
                if play_list.danthologyMode == False:
                    play_list.currentSongPosition=0
                #otherwise keep the currentSongPosition from the previous one.
            pygame.mixer.music.load(play_list.validFiles[play_list.currentSongIndex].filePath)
            pygame.mixer.music.play()
            PausedButtonText.set("Pause")
            play_list.isSongPause = False
            if play_list.danthologyDuration == 0 and play_list.danthologyMode: #start song from the beginning.
                play_list.currentSongPosition = play_list.validFiles[play_list.currentSongIndex].startPos
            if play_list.currentSongPosition > 0:
                pygame.mixer.music.set_pos(play_list.currentSongPosition)
                play_list.RESUMED = True
            elif play_list.validFiles[play_list.currentSongIndex].startPos > 0:
                start_pos = play_list.validFiles[play_list.currentSongIndex].startPos
                if play_list.currentSongPosition == 0:
                    if play_list.danthologyMode == False:
                        play_list.currentSongPosition = start_pos
                    # otherwise keep the currentSongPosition from the previous one.
                pygame.mixer.music.set_pos(start_pos)
                play_list.RESUMED = True
            if play_list.danthologyDuration > 0 and play_list.danthologyMode:
                play_list.danthologyTimer = time.time()
        except Exception as e:
            print("Play Music Function: " + str(e))
        else:
            SongName.set("Playing: " + play_list.validFiles[play_list.currentSongIndex].fileName)
            SongSize.set("Size: " + str(play_list.validFiles[play_list.currentSongIndex].fileSize) + " MB")
            songLength = float("{0:.0f}".format(play_list.validFiles[play_list.currentSongIndex].Length))  # no decimals needed
            textLength.set("Length: {:0>8}".format(str(datetime.timedelta(seconds=songLength))))
            textGenre.set("Genre: " + str(play_list.validFiles[play_list.currentSongIndex].Genre))
            textArtist.set("Artist: " + str(play_list.validFiles[play_list.currentSongIndex].Artist))
            textAlbum.set("Album: " + str(play_list.validFiles[play_list.currentSongIndex].Album))
            textTitle.set("Title: " + str(play_list.validFiles[play_list.currentSongIndex].Title))
            textYear.set("Year: " + str(play_list.validFiles[play_list.currentSongIndex].Year))
            textSongListenedTime.set("Song Listened Time: {:0>8}" .format(str(datetime.timedelta(seconds=int(play_list.validFiles[play_list.currentSongIndex].SongListenedTime)))))
            startPos = int(play_list.validFiles[play_list.currentSongIndex].startPos)
            textStartTime.set("Start Time: {:0>8}" .format(str(datetime.timedelta(seconds=startPos))))
            endPos = int(play_list.validFiles[play_list.currentSongIndex].endPos)
            textEndTime.set("End Time: {:0>8}" .format(str(datetime.timedelta(seconds=endPos))))
            textFadeIn.set("FadeIn: " + str(play_list.validFiles[play_list.currentSongIndex].fadein_duration)+"s")
            textFadeOut.set("FadeOut: " + str(play_list.validFiles[play_list.currentSongIndex].fadeout_duration) +"s")
            mode = "Stereo" if play_list.validFiles[play_list.currentSongIndex].channels == 2 else "Mono"
            textMonoStereoMode.set("Mode: " + mode)
            textSampleRate.set("Sample Rate: " + str(play_list.validFiles[play_list.currentSongIndex].sample_rate))
            progress["maximum"] = play_list.validFiles[play_list.currentSongIndex].Length
            songRating.set(str(play_list.validFiles[play_list.currentSongIndex].Rating))
            if play_list.playingFileNameTransition == "none":
                visualSongNameLabel = play_list.validFiles[play_list.currentSongIndex].fileName
            elif play_list.playingFileNameTransition == "typewriting":
                visualSongNameLabel = ""
            elif play_list.playingFileNameTransition == "separation":
                visualSongNameLabel = "_" + play_list.validFiles[play_list.currentSongIndex].fileName
            updateRadioButtons()
            play_list.validFiles[play_list.currentSongIndex].NumberOfPlays+=1
            textNofPlays.set("No. of Plays: " + str(play_list.validFiles[play_list.currentSongIndex].NumberOfPlays))
            try:
                scheduler.enter(progressViewRealTime, 1, viewProgress)
                scheduler.run()
            except Exception as exp:
                print("Play Music Function - starting scheduler: " + str(exp))

def pause_music(): #this function is called when clicking on Pause Button.
    global play_list
    if pygame.mixer.get_init():
        try:
            if play_list.isSongPause == False and pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                PausedButtonText.set("Resume")
                play_list.isSongPause = True
                if len(play_list.validFiles) > 0 :
                    SongName.set("Paused: " + play_list.validFiles[play_list.currentSongIndex].fileName)
                else:
                    SongName.set("Paused: ")
            elif play_list.isSongPause == True and pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
                PausedButtonText.set("Pause")
                play_list.isSongPause = False
                if len(play_list.validFiles) > 0:
                    SongName.set("Playing: " + play_list.validFiles[play_list.currentSongIndex].fileName)
                else:
                    SongName.set("Playing: ")
                scheduler.enter(progressViewRealTime, 1, viewProgress)
                scheduler.run()
        except Exception as e:
            print("Pause Music Function: " + str(e))

def stop_music(): #this function is called when clicking on Stop Button.
    global play_list
    if pygame.mixer.get_init():
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                SongName.set("Playing: ")
                progress["value"] = 0
                textLength.set("Length: ")
                textGenre.set("Genre: ")
                textAlbum.set("Album: ")
                textYear.set("Year: ")
                textTitle.set("Title: ")
                textArtist.set("Artist: ")
                textNofPlays.set("No. of Plays: ")
                textEndTime.set("End Time: ")
                textStartTime.set("Start Time: ")
                textMonoStereoMode.set("Mode: ")
                textFadeIn.set("FadeIn: ")
                textFadeOut.set("FadeOut: ")
                textSampleRate.set("Sample Rate: ")
                if play_list.progressTime == "Ascending":
                    SongDuration.set("Time Elapsed: ")
                else:
                    SongDuration.set("Time Left: ")
                SongSize.set("Size: ")
                play_list.isSongStopped = True
                if play_list.danthologyMode == False:
                    play_list.currentSongPosition=0
                play_list.RESUMED = False
                PausedButtonText.set("Pause")
                play_list.isSongPause = False
        except Exception as e:
            print("Stop Music Function: " +str(e))

def handleDanthology(): #this function is called when changing a song, with DanthologyMode enabled.
    global play_list
    if play_list.currentSongPosition >= math.floor(play_list.validFiles[play_list.currentSongIndex].endPos):
        play_list.currentSongPosition = 0
    else:
        if play_list.RESUMED:
            play_list.currentSongPosition = math.floor(play_list.currentSongPosition + pygame.mixer.music.get_pos() / 1000)
        else:
            play_list.RESUMED = True

def next_song(): #this function is called when clicking on Next Button.
    global listBox_Song_selected_index
    global play_list
    if len(play_list.validFiles) > 0 and play_list.currentSongIndex!=None:
        if (play_list.SHUFFLE==False):
            try:
                play_list.currentSongIndex+=1
                if play_list.currentSongIndex >= len(play_list.validFiles):
                    if play_list.REPEAT==3: #End of playlist, do not repeat.
                        play_list.currentSongIndex = len(play_list.validFiles)-1 #last file on playlist
                        stop_music() 
                        clearLabels()
                        return #silence must be heard.
                    else:
                        play_list.currentSongIndex = 0
                else:
                    pass
            except Exception as exp:
                print("Next Song Function" + str(exp))
        else:
            play_list.shufflingHistory.append(play_list.currentSongIndex)
            if shuffling_playlist() == False:
                play_list.currentSongIndex = 0 
                stop_music() 
                clearLabels()
                play_list.shufflingHistory=[] # this will enable restart on this pattern.
                return #stop it here, playlist has ended.
        listBox_Song_selected_index = play_list.currentSongIndex #without this the song will not change
        if play_list.danthologyMode == False:
            play_list.currentSongPosition=0
        else:
            handleDanthology()
        play_music()

def previous_song(): #this function is called when clicking on Previous Button.
    global listBox_Song_selected_index
    global play_list
    if len(play_list.validFiles) > 0 and play_list.currentSongIndex!=None:
        if(play_list.SHUFFLE==False):
            try:
                play_list.currentSongIndex -= 1
                if play_list.currentSongIndex < 0:
                    play_list.currentSongIndex = len(play_list.validFiles)-1
                else:
                    pass
            except Exception as exp:
                print("Previous Song Function: " + str(exp))
        else:
            if len(play_list.shufflingHistory) > 0 : 
                play_list.currentSongIndex = play_list.shufflingHistory[len(play_list.shufflingHistory)-1] # load the last item added to history.
                del play_list.shufflingHistory[len(play_list.shufflingHistory)-1] #remove from history the song which was loaded.
        listBox_Song_selected_index = play_list.currentSongIndex #without this the song will not change
        if play_list.danthologyMode == False:
            play_list.currentSongPosition = 0
        else:
            handleDanthology()
        play_music()

def addFontTransitions():
    global visualSongNameLabel
    global Project_Title
    if play_list.usePlayerTitleTransition:
        Project_Title = fontTitleTransition(Project_Title)
        window.title(Project_Title)  # add animation to font when playing music
    if play_list.playingFileNameTransition == "typewriting":
        visualSongNameLabel = fontTypeWritingTransition(visualSongNameLabel)
    elif play_list.playingFileNameTransition == "separation":
        visualSongNameLabel = fontSeparatedTransition(visualSongNameLabel)
    SongName.set("Playing: " + visualSongNameLabel)

def makeProgress(value):
    global progress
    global play_list
    if play_list.progressTime == "Ascending":
        SongDuration.set("Time Elapsed: {:0>8}".format(str(datetime.timedelta(seconds=int(value)))))
    else:
        SongLength = int(play_list.validFiles[play_list.currentSongIndex].Length - value)
        SongDuration.set("Time Left: {:0>8}".format(str(datetime.timedelta(seconds=SongLength))))
    progress["value"] = value
    if play_list.validFiles[play_list.currentSongIndex].fadein_duration > 0:
        if value <= play_list.validFiles[play_list.currentSongIndex].fadein_duration+1:
            fadein(value - play_list.validFiles[play_list.currentSongIndex].startPos)
    if play_list.validFiles[play_list.currentSongIndex].fadeout_duration > 0:
        if value >= play_list.validFiles[play_list.currentSongIndex].endPos - \
                                play_list.validFiles[play_list.currentSongIndex].fadeout_duration:
            if play_list.useCrossFade:
                fadeout(play_list.validFiles[play_list.currentSongIndex].endPos-value+play_list.crossFadeGap) 
                #delay fadeout, song should end with 0.3 volume, same volume the next one is supposed to start
            else:
                fadeout(play_list.validFiles[play_list.currentSongIndex].endPos-value) 
    if play_list.danthologyMode and play_list.danthologyDuration > 0:
        if time.time() - play_list.danthologyTimer >  play_list.danthologyDuration:
            #Danthology
            next_song()
    if value >= math.floor(play_list.validFiles[play_list.currentSongIndex].endPos):
        if play_list.useCrossFade: #hurry things up if using crossfade, so there will be no gaps between tracks
            play_list.validFiles[play_list.currentSongIndex].fadein_duration = 0
            play_list.validFiles[play_list.currentSongIndex].fadeout_duration = 0
            if temp_SongEndPos!= None:
                play_list.validFiles[play_list.currentSongIndex].endPos = temp_SongEndPos
            else: #this should never happen.
                play_list.validFiles[play_list.currentSongIndex].endPos = play_list.validFiles[play_list.currentSongIndex].Length
            
            if  play_list.REPEAT == 1 or play_list.REPEAT == 3:
                next_song()
            elif play_list.REPEAT==0: #Repeat Off
                stop_music()
                clearLabels()
            else: #play_list.REPEAT==2 means Repeat One
                play_list.RESUMED = False
                play_list.currentSongPosition=0
                play_music()#play the same song again.
        else:
            stop_music()
            play_list.isSongPause = False
            play_list.isSongStopped = False #song is not stopped in this circumstances, song has finished
            #Playback will take 1 second break before next song.

gifImageObjectFrame = 0
def animateGifImageBackground(): #NOT USED
    global gifImageObjectFrame
    if play_list.customBackgroundPicture != None and ".gif" in play_list.customBackgroundPicture:
        imageObject = Image.open(play_list.customBackgroundPicture)
        if imageObject.is_animated:
            imageObject.seek(gifImageObjectFrame)
            background_image = ImageTk.PhotoImage(imageObject)
            background_label.configure(image=background_image)
            background_label.image = background_image
            gifImageObjectFrame+=1
            if gifImageObjectFrame >= imageObject.n_frames:
                gifImageObjectFrame = 0
                               
def viewProgress(): #this function is called in every second, when a song is being played.
    global play_list
    if play_list.usingSlideShow == True:
        Slideshow.countSeconds()
    if APPLICATION_EXIT == False:
        if pygame.mixer.music.get_busy() and play_list.isSongPause == False:
            addFontTransitions()
            if play_list.RESUMED:
                local_position = play_list.currentSongPosition + pygame.mixer.music.get_pos() / 1000
                makeProgress(local_position)
            else:
                play_list.currentSongPosition = pygame.mixer.music.get_pos()/1000
                makeProgress(play_list.currentSongPosition)
            if play_list.VolumeLevel > 0.0: #only if Volume not Muted means listening to it.
                play_list.validFiles[play_list.currentSongIndex].SongListenedTime+=progressViewRealTime #if entered here, means song is playing with volume!=0
                play_list.PlaylistListenedTime += progressViewRealTime #if entered here, means song is playing with volume!=0
                textSongListenedTime.set("Song Listened Time: {:0>8}" .format(str(datetime.timedelta(seconds=int(play_list.validFiles[play_list.currentSongIndex].SongListenedTime)))))
                textPlaylistListenedTime.set("Playlist Listened Time: {:0>8}" .format(str(datetime.timedelta(seconds=int(play_list.PlaylistListenedTime)))))
            try:
                window.update()  # Force an update of the GUI
                #without this the window will freeze.
            except Exception as exp: 
                #Enter here when the program is destroyed
                print("Application destroyed in View Progress Function")

                #Make a backup of everything:
                file = open(automaticallyBackupFile, "wb")
                pickle.dump(play_list, file)
                file.close()
                sys.exit()
            else:
                scheduler.enter(progressViewRealTime, 1, viewProgress)
        elif pygame.mixer.music.get_busy() == False and play_list.isSongPause == False and play_list.isSongStopped == False:
            play_list.RESUMED = False
            if(play_list.REPEAT==1 or play_list.REPEAT==3):
                next_song() #this will keep repeating the playlist
            elif play_list.REPEAT==2:
                play_music() #this will repeat the current song

def volume_down(): #this function is called when changing Volume from Keyboard using < Button
    global play_list
    if pygame.mixer.get_init():
        play_list.VolumeLevel-=0.1
        if (play_list.VolumeLevel < 0.0):
            play_list.VolumeLevel = 0.0
        if play_list.currentSongPosition - play_list.validFiles[play_list.currentSongIndex].startPos > \
                play_list.validFiles[play_list.currentSongIndex].fadein_duration and play_list.currentSongPosition < \
                play_list.validFiles[play_list.currentSongIndex].endPos - play_list.validFiles[play_list.currentSongIndex].fadeout_duration:
            pygame.mixer.music.set_volume(play_list.VolumeLevel)
        VolumeScale.set(play_list.VolumeLevel*100)

def volume_up(): #this function is called when changing Volume from Keyboard using > Button
    global play_list
    if pygame.mixer.get_init():
        play_list.VolumeLevel+=0.1
        if(play_list.VolumeLevel>1.0):
            play_list.VolumeLevel=1.0
        if play_list.currentSongPosition - play_list.validFiles[play_list.currentSongIndex].startPos > \
            play_list.validFiles[play_list.currentSongIndex].fadein_duration and play_list.currentSongPosition < \
                play_list.validFiles[play_list.currentSongIndex].endPos - play_list.validFiles[play_list.currentSongIndex].fadeout_duration:
            pygame.mixer.music.set_volume(play_list.VolumeLevel)
        VolumeScale.set(play_list.VolumeLevel * 100)

def shuffle(): #this function is called when clicking on SHUFFLE Button.
    global play_list
    if(play_list.SHUFFLE):
        ShuffleButtonText.set("Shuffle Off")
        play_list.SHUFFLE = False
        play_list.shufflingHistory = [] #empty the history
    else:
        ShuffleButtonText.set("Shuffle On")
        play_list.SHUFFLE = True

def shuffling_playlist():
    global play_list
    if len(play_list.validFiles) > 1:
        if play_list.REPEAT == 3:
            temp_list = []
            if len(play_list.shufflingHistory) < len(play_list.validFiles):
                for index in range(0, len(play_list.validFiles)):
                    for item in play_list.shufflingHistory:
                        if item == index:
                            break
                    else: # will enter here only if break was avoided.
                        temp_list.append(index)
                rand = random.randint(0, len(temp_list)-1) #endpoints included
                play_list.currentSongIndex = temp_list[rand]
            else:
                #here we need to stop it, because we reached end of playlist.
                return False
        else:
            rand = random.randint(0, len(play_list.validFiles)-1) #endpoints included
            play_list.currentSongIndex = rand
        return True

def save_playlist(): #this function is called when clicking on Save Playlist Button.
    global play_list
    window.filename = filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                                 filetypes=(("pypl files", "*.pypl"), ("all files", "*.*")))
    if window.filename:
        if ".pypl" in window.filename:
            file = open(window.filename, "wb")
        else:
            file = open(window.filename + ".pypl", "wb")
        if pygame.mixer.get_init():
            if play_list.RESUMED:
                play_list.currentSongPosition += math.floor(pygame.mixer.music.get_pos() / 1000)
            else:
                play_list.currentSongPosition = math.floor(pygame.mixer.music.get_pos() / 1000)
        pickle.dump(play_list, file)
        file.close()

def clearLabels(): #this function is called on New Playlist Button, and on Stop Button, or at the end of the playlist.
    textFilesToPlay.set("Files: " + str(len(play_list.validFiles)))
    VolumeScale.set(play_list.VolumeLevel * 100)
    textGenre.set("Genre: ")
    textArtist.set("Artist: ")
    SongName.set("Playing: ")
    textAlbum.set("Album: ")
    textTitle.set("Title: ")
    textYear.set("Year: ")
    textSongListenedTime.set("Song Listened Time: ")
    textPlaylistListenedTime.set("Playlist Listened Time: ")
    textFadeIn.set("FadeIn: ")
    textFadeOut.set("FadeOut: ")
    SongSize.set("Size: ")
    textMonoStereoMode.set("Mode: ")
    textNofPlays.set("No. of Plays: ")
    danMode = "OFF" if play_list.danthologyMode==False else "ON"
    textDanthologyMode.set("Danthology Mode: " + danMode)
    textSampleRate.set("Sample Rate: ")
    textEndTime.set("End Time: ")
    textStartTime.set("Start Time")
    textLength.set("Length: ")
    if play_list.progressTime == "Ascending":
        SongDuration.set("Time Elapsed: ")
    else:
        SongDuration.set("Time Left: ")

def savingSongStats(): #this function is called when canceling the window
    file = open(SongStatsFileName, "wb")
    dict_list = []
    dictionary = {}
    for song in play_list.validFiles:
        dictionary ["fileName"] = song.fileName
        dictionary ["Rating"] = song.Rating
        dictionary ["NumberOfPlays"] = song.NumberOfPlays
        dictionary ["fadein_duration"] = song.fadein_duration
        dictionary ["fadeout_duration"] = song.fadeout_duration
        dictionary ["endPos"] = song.endPos
        dictionary ["startPos"] = song.startPos
        dictionary ["SongListenedTime"] = song.SongListenedTime
        dict_list.append(dictionary)
        dictionary = {}
    pickle.dump(dict_list, file)
    file.close()

def loadSongStats(startIndex=0): #this function is called when loading songs to a playlist if MaintainSongsStats is true
    global play_list
    dict_list = []
    if os.path.isfile(SongStatsFileName):
        try:
            file = open(SongStatsFileName, "rb")
            dict_list = pickle.load(file)
            file.close()
        except:
            print("Could not load the songs stats. File might be corrupted.")
            return
        else:
            for song in play_list.validFiles[startIndex:]:
                for dictionary in dict_list:
                    if song.fileName == dictionary["fileName"]:
                        if dictionary["Rating"] > song.Rating: #will solve duplicates
                            song.Rating = dictionary["Rating"]
                        if dictionary["NumberOfPlays"] > song.NumberOfPlays: #will solve duplicates
                            song.NumberOfPlays += dictionary["NumberOfPlays"]
                        song.fadein_duration = dictionary ["fadein_duration"]
                        song.fadeout_duration = dictionary ["fadeout_duration"]
                        song.endPos = dictionary ["endPos"]
                        song.startPos = dictionary ["startPos"]
                        if dictionary["SongListenedTime"] > song.SongListenedTime: #will solve duplicates
                            song.SongListenedTime = dictionary["SongListenedTime"]
                        play_list.PlaylistListenedTime += song.SongListenedTime # calculating playlistListenedTime
    
def new_playlist(): #this function is called when clicking on New Playlist Button.
    global play_list
    global listBox_Song_selected_index
    savingSongStats() #saving song stats.
    if dialog != None:
        dialog.destroy()
    if pygame.mixer.get_init():
        if pygame.mixer.music.get_busy():
            NewPlaylistDialog(window)
        else:
            if play_list.resetSettings == False:
                play_list.isSongPause = False
                play_list.isSongStopped = False
                play_list.dirFilePath = None
                play_list.validFiles = []
                play_list.currentSongIndex = None
                play_list.currentSongPosition = 0
                play_list.RESUMED=False
                play_list.playTime = 0
                play_list.shufflingHistory = []
                play_list.isListOrdered = 17
                play_list.PlaylistListenedTime = 0
                play_list.BornDate = datetime.datetime.now()
            else:
                play_list = Playlist()
                # Restore default skin
                SkinColor.set(skinOptions[1][play_list.skin])
                changeSkin("<Double-Button>")
                window.attributes('-alpha', play_list.windowOpacity)
            clearLabels()
            displayElementsOnPlaylist()
            listBox_Song_selected_index = None
    else:
        if play_list.resetSettings == False:
            play_list.isSongPause = False
            play_list.isSongStopped = False
            play_list.dirFilePath = None
            play_list.validFiles = []
            play_list.currentSongIndex = None
            play_list.currentSongPosition = 0
            play_list.RESUMED=False
            play_list.playTime = 0
            play_list.shufflingHistory = []
            play_list.isListOrdered = 17
            play_list.PlaylistListenedTime = 0
            play_list.BornDate = datetime.datetime.now()
        else:
            play_list = Playlist()
            window.attributes('-alpha', play_list.windowOpacity)
            # Restore default skin
            SkinColor.set(skinOptions[1][play_list.skin])
            changeSkin("<Double-Button>")
        listBox_Song_selected_index=None
        clearLabels()
        displayElementsOnPlaylist()

def elementPlaylistDoubleClicked(event):
    global play_list
    if listbox.size():
        if type(dialog) != SearchTool:
            widget = event.widget
            index = int(widget.curselection()[0])
            #value = widget.get(index)
            play_list.currentSongIndex = index
            if play_list.danthologyMode == False: #else will let the next song continue where this one left
                play_list.currentSongPosition = play_list.validFiles[play_list.currentSongIndex].startPos
            elif pygame.mixer.get_init():
                play_list.currentSongPosition += math.floor(pygame.mixer.music.get_pos() / 1000)
            play_music()
        else:
            widget = event.widget
            index = int(widget.curselection()[0])
            value = widget.get(index)
            value=value.split(". ")
            play_list.currentSongIndex = int(value[0])
            if play_list.danthologyMode == False: #else will let the next song continue where this one left
                play_list.currentSongPosition = play_list.validFiles[play_list.currentSongIndex].startPos
            elif pygame.mixer.get_init():
                play_list.currentSongPosition += math.floor(pygame.mixer.music.get_pos() / 1000)
            play_music()

def updateSortButton(): 
    # 0-onrating, 1-sorted, 2-reversed, 3-random
    if play_list.isListOrdered == 0:
        SortButtonText.set("By Rating")
    elif play_list.isListOrdered == 1:
        SortButtonText.set("By Name")
    elif play_list.isListOrdered == 2:
        SortButtonText.set("Name Reversed")
    elif play_list.isListOrdered == 3:
        SortButtonText.set("Random")
    elif play_list.isListOrdered == 4:
        SortButtonText.set("Rating Reversed")
    elif play_list.isListOrdered == 5:
        SortButtonText.set("By Length")
    elif play_list.isListOrdered == 6:
        SortButtonText.set("Length Reversed")
    elif play_list.isListOrdered == 7:
        SortButtonText.set("By Genre")
    elif play_list.isListOrdered == 8:
        SortButtonText.set("Genre Reversed")
    elif play_list.isListOrdered == 9:
        SortButtonText.set("By Plays")
    elif play_list.isListOrdered == 10:
        SortButtonText.set("Plays Reversed")
    elif play_list.isListOrdered == 11:
        SortButtonText.set("By Year")
    elif play_list.isListOrdered == 12:
        SortButtonText.set("Year Reversed")
    elif play_list.isListOrdered == 13:
        SortButtonText.set("By Album")
    elif play_list.isListOrdered == 14:
        SortButtonText.set("Album Reversed")
    elif play_list.isListOrdered == 15:
        SortButtonText.set("By Title")
    elif play_list.isListOrdered == 16:
        SortButtonText.set("Title Reversed")
    elif play_list.isListOrdered == 17:
        SortButtonText.set("Custom")
    elif play_list.isListOrdered == 18:
        SortButtonText.set("Least Listened")
    elif play_list.isListOrdered == 19:
        SortButtonText.set("Most Listened")
        
def displayElementsOnPlaylist():
    global listbox
    listbox.delete(0, tk.END)
    for element in play_list.validFiles:
        listbox.insert(play_list.validFiles.index(element), str(play_list.validFiles.index(element))+". "+element.fileName)
        if len(str(play_list.validFiles.index(element))+". "+element.fileName) > listbox["width"] and play_list.listboxWidth=="Auto": # this will resize the playlist in case there is not enough room to see the string
            listbox["width"] = len(str(play_list.validFiles.index(element))+". "+element.fileName) + 5 # let there be 5 empty spaces before the end of playlist
    textTotalPlayTime.set("PlayTime: {:0>8}" .format(str(datetime.timedelta(seconds=int(play_list.playTime)))))
    if play_list.viewModel == "SMALL PLAYLIST" or play_list.viewModel == "PLAYLIST":
        changePlaylistView() # this will readjust the window.
            
def changingBackgroundElementColor(event):
    global play_list
    #changing buttons
    OpenFileButton["bg"]=SkinColor.get()
    OpenDirectoryButton["bg"]=SkinColor.get()
    PlayButton["bg"]=SkinColor.get()
    PauseButton["bg"]=SkinColor.get()
    StopButton["bg"]=SkinColor.get()
    NextButton["bg"]=SkinColor.get()
    PreviousButton["bg"]=SkinColor.get()
    ShuffleButton["bg"]=SkinColor.get()
    SavePlaylistButton["bg"]=SkinColor.get()
    NewPlaylistButton["bg"]=SkinColor.get()
    ViewPlaylistButton["bg"]=SkinColor.get()
    RepeatButton["bg"]=SkinColor.get()
    RemoveSongButton["bg"]=SkinColor.get()
    SortListButton["bg"]=SkinColor.get()
    MoveUpButton["bg"]=SkinColor.get()
    MoveDownButton["bg"]=SkinColor.get()
    SearchButton["bg"]=SkinColor.get()
    SleepButton["bg"]=SkinColor.get()
    #changing listbox
    listbox["bg"]=SkinColor.get()
    listbox["selectforeground"] = SkinColor.get()
    frame["bg"]=SkinColor.get()
    SkinFrame["bg"]=SkinColor.get()
    labelSkin["bg"]=SkinColor.get()
    #changing volume scale:
    VolumeScale["bg"] = SkinColor.get()
    VolumeScale["highlightbackground"] = SkinColor.get()
    #changing radiobutton:
    updateRadioButtons()
    #changing style of progress bar:
    styl.configure("Horizontal.TProgressbar", background = SkinColor.get())	
    #changing labels
    labelPlaying["fg"]=SkinColor.get()
    labelDuration["fg"]=SkinColor.get()
    labelSize["fg"]=SkinColor.get()
    labelFilesToPlay["fg"]=SkinColor.get()
    labelLength["fg"]=SkinColor.get()
    labelGenre["fg"]=SkinColor.get()
    labelStartTime["fg"]=SkinColor.get()
    labelEndTime["fg"]=SkinColor.get()
    labelTotalPlayTime["fg"]=SkinColor.get()
    labelFallAsleep["fg"]=SkinColor.get()
    labelWakeUp["fg"]=SkinColor.get()
    labelFadeIn["fg"]=SkinColor.get()
    labelFadeOut["fg"]=SkinColor.get()
    labelMonoStereoMode["fg"]=SkinColor.get()
    labelSampleRate["fg"]=SkinColor.get()
    labelNofPlays["fg"]=SkinColor.get()
    labelDanthologyMode["fg"]=SkinColor.get()
    labelArtist["fg"]=SkinColor.get()
    labelAlbum["fg"]=SkinColor.get()
    labelTitle["fg"]=SkinColor.get()
    labelSongListenedTime["fg"]=SkinColor.get()
    labelPlaylistListenedTime["fg"]=SkinColor.get()
    labelYear["fg"]=SkinColor.get()
    if type(dialog) == Customize: #if entered here means setting a custom color
        play_list.customElementBackground = custom_color_list.index(SkinColor.get())
        dialog.destroy()
        Customize(window)
        showCurrentSongInList()

def customFontChange(event):
    global dialog
    global allButtonsFont
    global play_list
    allButtonsFont = allButtonsFont.get()
    play_list.customFont = custom_font_list.index(allButtonsFont)
    changeFonts()
    changePlaylistView() #this will reposition elements according to the new font.
    dialog.destroy()
    Customize(window)
    if listbox.size() > 0 and play_list.currentSongIndex < listbox.size(): #make playing song visible
        listbox.see(play_list.currentSongIndex)  # Makes sure the given list index is visible. You can use an integer index,
        listbox.selection_clear(0, tk.END)  # clear existing selection
        listbox.select_set(play_list.currentSongIndex)

def changeSkin(event): #this function is called when clicking on Skin ComboBox
    global backgroundFile
    global skinOptions
    global background_label
    global dialog
    global play_list
    global allButtonsFont
    global labelBackground
    if SkinColor.get() == "custom":
        showCustomizeWindow()
    else:
        changingBackgroundElementColor(event)
        #changing background
        play_list.customElementBackground = None
        play_list.customLabelBackground = None
        play_list.customChangeBackgroundedLabelsColor = None
        play_list.customFontColor=None
        play_list.customBackgroundPicture = None
        play_list.customFont = None
        if SkinColor.get() in skinOptions[1]: # if using predefined skins, with predefined backgrounds.
            index = skinOptions[1].index(SkinColor.get())
            backgroundFile = skinOptions[0][index]
            if os.path.exists(backgroundFile) and os.path.isfile(backgroundFile):
                play_list.customBackgroundPicture = backgroundFile
                background_image = tk.PhotoImage(file=backgroundFile)
                background_label.configure(image=background_image)
                background_label.image = background_image
                play_list.skin = index
            else:
                print("File: " + str(backgroundFile) + " could not be found.")
                print("I improvised: only Skin Color was changed.")
        allButtonsFont = skinOptions[2][play_list.skin]
        changeFonts() #change the font that comes with the new skin
        labelBackground.set("lightgray") #default value
        fontColor.set("white") #default value
        changingFontColor(event)
        changingLabelBackgroundColor(event)
        showCurrentSongInList()
        if(dialog != None):
            if type(dialog) == CuttingTool:
                dialog.destroy()
                CuttingTool(window)
            elif type(dialog) == SearchTool:
                dialog.destroy()
                SearchTool(window)
            elif type(dialog) == SleepingTool:
                dialog.destroy()
                SleepingTool(window)
            elif type(dialog) == Customize:
                dialog.destroy()
                Customize(window)
            elif type(dialog) == NewPlaylistDialog:
                dialog.destroy()
                NewPlaylistDialog(window)
            elif type(dialog) == Mp3TagModifierTool:
                dialog.destroy()
                Mp3TagModifierTool()
            elif type(dialog) == GrabLyricsTool:
                index = dialog.songIndex # store the index of the song for which the lyrics are shown
                dialog.destroy()
                GrabLyricsTool(index)
            elif type(dialog) == GrabArtistBio:
                index = dialog.songIndex # store the index of the song for which the lyrics are shown
                dialog.destroy()
                GrabArtistBio(index)
        if Slideshow.top != None:
            #destroy it
            Slideshow.top.destroy()
            #rebuild it
            Slideshow()

def calculateScreenHeightWidth():
    global allButtonsFont
    CurrentFont= allButtonsFont.get() if  type(allButtonsFont) == StringVar else allButtonsFont
    fontFam = font.Font(family=CurrentFont.split(" ")[0], size=CurrentFont.split(" ")[1])
    if len(CurrentFont.split(" ")) == 3 and CurrentFont.split(" ")[2] == "bold":
        fontFam = font.Font(family=CurrentFont.split(" ")[0], size=CurrentFont.split(" ")[1], weight=CurrentFont.split(" ")[2])
    
    screenHeight = fontFam.metrics("linespace")
    screenHeight*=listbox["height"]
    screenHeight+=10 # the margin on Y axis of the frame.
    screenHeight+= 60 if listbox["height"] == 20 else 80
    
    buttonWidth = (listbox.winfo_reqwidth()+scroll.winfo_reqwidth())/4
    frameXPos = getPlayListFramePlacement()
    frame.place(x=frameXPos, y=10)
    RemoveSongButton.place(x=frameXPos, y=screenHeight)
    SortListButton.place(x=frameXPos+buttonWidth, y=screenHeight)
    MoveUpButton.place(x=frameXPos+2*buttonWidth, y=screenHeight)
    MoveDownButton.place(x=frameXPos+3*buttonWidth, y=screenHeight)
    
    screenWidth = frameXPos+ listbox.winfo_reqwidth()+scroll.winfo_reqwidth()+50
    return screenHeight, screenWidth

def getPlayListFramePlacement():
    return int(OpenFileButton.winfo_reqwidth()*4.5) + int(play_list.buttonSpacing*(play_list.buttonSpacing/60)) 
    # playlist will be placed in the left side after the buttons 

def calculateLetterWidthPixels(): #NOT BEING USED
    global allButtonsFont
    CurrentFont = allButtonsFont.get() if type(allButtonsFont) == StringVar else allButtonsFont
    fontFam = font.Font(family=CurrentFont.split(" ")[0], size=CurrentFont.split(" ")[1])
    if len(CurrentFont.split(" ")) == 3 and CurrentFont.split(" ")[2] == "bold":
        fontFam ["weight"] = CurrentFont.split(" ")[2]
    return (fontFam.measure("0") + fontFam.measure("A") + fontFam.measure("a"))/3 #compute average width

def view_playlist(): #this function is called when clicking on View Playlist Button.
    aMenu = tk.Menu(window, tearoff=0)
    aMenu.add_command(label='Compact View', command=seeCompact)
    aMenu.add_command(label='Block View', command=seeBlock)
    aMenu.add_command(label='Tiny View', command=seeTinyPlaylist)
    aMenu.add_command(label='Playlist View', command=seePlaylist)
    aMenu.add_command(label='Fullscreen View', command=seeFullScreen)
    #these coordinates are set to be below View Playlist Button
    x = ViewPlaylistButton.winfo_rootx() 
    y = ViewPlaylistButton.winfo_rooty()+30
    aMenu.post(x, y)

def seeCompact():
    play_list.viewModel = "COMPACT"
    changePlaylistView()

def seeBlock():
    play_list.viewModel = "BLOCK"
    changePlaylistView()
    
def seeTinyPlaylist():
    play_list.viewModel = "SMALL PLAYLIST"
    changePlaylistView()
    
def seePlaylist():
    play_list.viewModel = "PLAYLIST"
    changePlaylistView()
    
def seeFullScreen():
    play_list.viewModel = "FULLSCREEN"
    changePlaylistView()

def changePlaylistView():
    global play_list
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    if play_list.playerXPos > (screen_width-50) or play_list.playerXPos < 0: #in case the last player position was off the screen. 
        #50 is a gap. The player will never be out of screen entirely, but it could be invisible, because of start bar/ task bar or other widgets.
        play_list.playerXPos = 100

    if  play_list.playerYPos > (screen_height-50) or play_list.playerYPos < 0: #in case the last player position was off the screen
        #50 is a gap. The player will never be out of screen entirely, but it could be invisible, because of start bar/ task bar or other widgets.
        play_list.playerYPos = 100
    
    if play_list.viewModel == "COMPACT":
        ViewPlaylistButtonText.set("Compact View")
        window.wm_attributes("-fullscreen", False)
        lineDistancePixels = OpenFileButton.winfo_reqwidth()*3 + play_list.buttonSpacing*2 + 10 #10 comes from 5 pixels padding on the first button column and 5 after the last column
        window.geometry(str(lineDistancePixels)+"x450+" + str(play_list.playerXPos) + "+" + str(play_list.playerYPos))# build a window
    elif play_list.viewModel == "BLOCK":
        ViewPlaylistButtonText.set("Block View")
        window.wm_attributes("-fullscreen", False)
        lineDistancePixels = OpenFileButton.winfo_reqwidth()*3 + play_list.buttonSpacing*2 + 10 #10 comes from 5 pixels padding on the first button column and 5 after the last column
        window.geometry(str(lineDistancePixels)+"x650+" + str(play_list.playerXPos) + "+" + str(play_list.playerYPos))# build a window
    elif play_list.viewModel == "SMALL PLAYLIST":
        ViewPlaylistButtonText.set("Tiny View")
        window.wm_attributes("-fullscreen", False)
        listbox["height"] = 20
        screenHeight, screenWidth = calculateScreenHeightWidth() # this will rearange the buttons under the playlist
        window.geometry(str(screenWidth) + "x450+" + str(play_list.playerXPos) + "+" + str(play_list.playerYPos))# build a window

    elif play_list.viewModel == "PLAYLIST":
        ViewPlaylistButtonText.set("Playlist View")
        window.wm_attributes("-fullscreen", False)
        listbox["height"] = play_list.listboxNoRows
        screenHeight, screenWidth = calculateScreenHeightWidth()  # this will rearrage the buttons under the playlist
        screenHeight += 40  # the margin added until the window finishes
        window.geometry(str(screenWidth) + "x" + str(screenHeight) + "+" + str(play_list.playerXPos) + "+" + str(
            play_list.playerYPos))  # build a window
    elif play_list.viewModel == "FULLSCREEN":
        ViewPlaylistButtonText.set("Fullscreen View")
        window.wm_attributes("-fullscreen", True)
        listbox["height"] = play_list.listboxNoRows
        calculateScreenHeightWidth() #this will rearrage the buttons under the playlist.
        
def repeat(): #this function is called when clicking on REPEAT button.
    global play_list
    if (play_list.REPEAT==0):
        RepeatButtonText.set("Repeat All")
        play_list.REPEAT = 1
    elif (play_list.REPEAT==1 and play_list.danthologyMode==False):
        RepeatButtonText.set("Repeat One")
        play_list.REPEAT = 2
    elif (play_list.REPEAT==2):
        RepeatButtonText.set("Repeat None")
        play_list.REPEAT = 3
    else:
        if play_list.danthologyMode: #skip Repeat Off is danthology Mode is enabled.
            RepeatButtonText.set("Repeat All")
            play_list.REPEAT = 1
        else:
            RepeatButtonText.set("Repeat Off")
            play_list.REPEAT = 0

def randomize():
    if len(play_list.validFiles) > 0:
        #Changing list to set, the set is automatically randomized, then changing it back again
        random.shuffle(play_list.validFiles)
        # 0-onrating, 1-sorted, 2-reversed, 3-random
        play_list.isListOrdered = 3 #3 - is the value for randomized
        displayElementsOnPlaylist()
        updateSortButton() #put the correct message on the Sort Button

def navigationSound(event): #this function is called when clicking on the progressBar
    global play_list
    global progressBarLength
    if len(play_list.validFiles) > 0 and play_list.currentSongIndex!= None:
        x =  (play_list.validFiles[play_list.currentSongIndex].Length / progressBarLength)
        play_list.currentSongPosition = math.floor(event.x * x)
        if pygame.mixer.get_init():
            pygame.mixer.music.play() #this will restart the song
            pygame.mixer.music.set_pos(play_list.currentSongPosition) #this will set the desired position on the playback
            if play_list.validFiles[play_list.currentSongIndex].fadein_duration > 0 and play_list.currentSongPosition > (play_list.validFiles[play_list.currentSongIndex].startPos + 
            	play_list.validFiles[play_list.currentSongIndex].fadein_duration):
            	if pygame.mixer.music.get_volume() < play_list.VolumeLevel: #in case the user shifted position from beggining when there was fadein enabled.
                    pygame.mixer.music.set_volume(play_list.VolumeLevel)
            if play_list.validFiles[play_list.currentSongIndex].fadeout_duration > 0 and play_list.currentSongPosition > (play_list.validFiles[play_list.currentSongIndex].endPos - 
            	play_list.validFiles[play_list.currentSongIndex].fadeout_duration):
            	if pygame.mixer.music.get_volume() < play_list.VolumeLevel: #in case the user shifted position from end when there was fadeout enabled.
                    pygame.mixer.music.set_volume(play_list.VolumeLevel)
        progress["value"] = play_list.currentSongPosition
        play_list.RESUMED = True
        if play_list.isSongPause:
            PausedButtonText.set("Pause")
            play_list.isSongPause = False
            SongName.set("Playing: " + play_list.validFiles[play_list.currentSongIndex].fileName)
        if play_list.isSongStopped:
            play_music()

def windSongRight():
    if len(play_list.validFiles) > 0 and play_list.currentSongIndex!= None:
        play_list.currentSongPosition += 5
        progress["value"] = play_list.currentSongPosition

def windSongLeft():
    if len(play_list.validFiles) > 0 and play_list.currentSongIndex!= None:
        play_list.currentSongPosition -= 5
        progress["value"] = play_list.currentSongPosition

def squareBracketsReleased(event):
    if pygame.mixer.get_init():
        pygame.mixer.music.play()
        pygame.mixer.music.set_pos(play_list.currentSongPosition)        

def on_closing(): #this function is called only when window is canceled/closed
    global APPLICATION_EXIT
    global play_list
    APPLICATION_EXIT = True
    # Make a backup of everything:
    if(len(play_list.validFiles) == 0):
        #if empty set these field so that when next song will be added they won't take effect
        play_list.isSongPause = False
        play_list.isSongStopped = False
        play_list.isListOrdered = 0  # 0-onrating ; 1-sorted 2-reversed; 3-random;
        play_list.currentSongIndex = None
        play_list.currentSongPosition = 0
        play_list.RESUMED = False
    elif pygame.mixer.get_init():
        if play_list.RESUMED: #it means there are songs in the playlist
            play_list.currentSongPosition += math.floor(pygame.mixer.music.get_pos() / 1000)
        else:
            play_list.currentSongPosition = math.floor(pygame.mixer.music.get_pos() / 1000)
    #copy window coordinates:
    play_list.playerXPos = window.winfo_x()
    play_list.playerYPos = window.winfo_y()
    file = open(automaticallyBackupFile, "wb")
    pickle.dump(play_list, file)
    file.close()
    window.quit()
    sys.exit()

def remove_song():
    global listBox_Song_selected_index
    if listBox_Song_selected_index!=None:
        if listBox_Song_selected_index < len(play_list.validFiles):
            if play_list.SHUFFLE:
                del play_list.shufflingHistory[len(play_list.shufflingHistory)-1] #this entry will no longer be valid, since the song was removed.
            del play_list.validFiles[listBox_Song_selected_index]
            displayElementsOnPlaylist()
            textFilesToPlay.set("Files: " + str(len(play_list.validFiles)))
            #listBox_Song_selected_index=None #initialize this if u want to remove only onebyone

def list_selected_item(event):
    if listbox.size() > 0:
        global listBox_Song_selected_index
        if type(dialog) != SearchTool:
            listboxSelectedEvent = event.widget
            index = int(listboxSelectedEvent.curselection()[0])
            value = listbox.get(index)
            value = value.split(". ")
            listBox_Song_selected_index = int(value[0])
        else:
            listboxSelectedEvent = event.widget
            index = int(listboxSelectedEvent.curselection()[0])
            value = listbox.get(index)
            value = value.split(". ")
            listBox_Song_selected_index = int(value[0])
            play_list.currentSongIndex = int(value[0])
            listBox_Song_selected_index = play_list.currentSongIndex
            
def sortByFileName():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 1
    play_list.validFiles.sort(key=lambda Song: Song.fileName)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortByFileNameReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 2
    play_list.validFiles.sort(key=lambda Song: Song.fileName)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortRandomized():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    randomize() #let them be randomized
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    showCurrentSongInList()

def sortByRating():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 0
    play_list.validFiles.sort(key=lambda Song: Song.Rating, reverse=True)  # sort the list according to Rating
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortByRatingReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 4
    play_list.validFiles.sort(key=lambda Song: Song.Rating, reverse=True)  # sort the list according to Rating
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortByLength():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 5
    play_list.validFiles.sort(key=lambda Song: Song.Length)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortByLengthReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 6
    play_list.validFiles.sort(key=lambda Song: Song.Length)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortByGenre():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 7
    play_list.validFiles.sort(key=lambda Song: Song.Genre)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortByGenreReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 8
    play_list.validFiles.sort(key=lambda Song: Song.Genre)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortByNoOfPlays():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 9
    play_list.validFiles.sort(key=lambda Song: Song.NumberOfPlays)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortByNoOfPlaysReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 10
    play_list.validFiles.sort(key=lambda Song: Song.NumberOfPlays)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortByYear():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 11
    play_list.validFiles.sort(key=lambda Song: Song.Year)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortByYearReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 12
    play_list.validFiles.sort(key=lambda Song: Song.Year)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortByAlbum():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 13
    play_list.validFiles.sort(key=lambda Song: Song.Album)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortByAlbumReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 14
    play_list.validFiles.sort(key=lambda Song: Song.Album)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortByTitle():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 15
    play_list.validFiles.sort(key=lambda Song: Song.Title)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortByTitleReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 16
    play_list.validFiles.sort(key=lambda Song: Song.Title)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()

def sortByListenedTime():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 18
    play_list.validFiles.sort(key=lambda Song: Song.SongListenedTime)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()    

def sortByListenedTimeReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 19
    play_list.validFiles.sort(key=lambda Song: Song.SongListenedTime)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortButton()
    showCurrentSongInList()
    
def sort_list(): #this function is called when clicking Sort Button.
    # 0-onrating, 1-sorted, 2-reversed, 3-random...
    global play_list
    aMenu = tk.Menu(window, tearoff=0)
    aMenu.add_command(label='Sort By Name', command=sortByFileName)
    aMenu.add_command(label='Sort By Name Reversed', command=sortByFileNameReversed)
    aMenu.add_command(label='Sort Randomize', command=sortRandomized)
    aMenu.add_command(label='Sort By Rating', command=sortByRating)
    aMenu.add_command(label='Sort By Rating Reversed', command=sortByRatingReversed)
    aMenu.add_command(label='Sort By Length', command=sortByLength)
    aMenu.add_command(label='Sort By Length Reversed', command=sortByLengthReversed)
    aMenu.add_command(label='Sort By Genre', command=sortByGenre)
    aMenu.add_command(label='Sort By Genre Reversed', command=sortByGenreReversed)
    aMenu.add_command(label='Sort By No. Of Plays', command=sortByNoOfPlays)
    aMenu.add_command(label='Sort By No. Of Plays Reversed', command=sortByNoOfPlaysReversed)
    aMenu.add_command(label='Sort By Year', command=sortByYear)
    aMenu.add_command(label='Sort By Year Reversed', command=sortByYearReversed)
    aMenu.add_command(label='Sort By Album', command=sortByAlbum)
    aMenu.add_command(label='Sort By Album Reversed', command=sortByAlbumReversed)
    aMenu.add_command(label='Sort By Title', command=sortByTitle)
    aMenu.add_command(label='Sort By Title Reversed', command=sortByTitleReversed)
    aMenu.add_command(label='Sort By Least Listened', command=sortByListenedTime)
    aMenu.add_command(label='Sort By Most Listened', command=sortByListenedTimeReversed)
    #these coordinates are set to be above Sort Button
    x = SortListButton.winfo_rootx() 
    y = SortListButton.winfo_rooty()-10
    aMenu.post(x, y)

def UpdateSongRating():
    global play_list
    global listBox_Song_selected_index
    if len(play_list.validFiles) > 0 and play_list.currentSongIndex:
        if pygame.mixer.get_init() != None:
            if pygame.mixer.music.get_busy() or play_list.isSongPause:
                play_list.validFiles[play_list.currentSongIndex].Rating = int(songRating.get())
                updateRadioButtons()
                if play_list.isListOrdered==0 and SortButtonText.get() != "Custom": #if playlist is ordered by rating, update it in real time, since rating has changed
                    Song = play_list.validFiles[play_list.currentSongIndex]
                    play_list.validFiles.sort(key=lambda Song: Song.Rating, reverse=True)  # sort the list according to Rating
                    play_list.currentSongIndex=play_list.validFiles.index(Song)
                    displayElementsOnPlaylist()

def updateRadioButtons(): #this function is called when clicking on Song Rating - radio buttons.
    color = OpenFileButton["bg"]  # get the same color as every element
    if (int(songRating.get()) == 1):
        labelSongRating["bg"] = color
        labelSongRating["fg"] = fontColor.get()
        R1["bg"] = color
        R1["fg"] = fontColor.get()
        R2["bg"] = radioButtonsDefaultColor
        R2["fg"] = color
        R3["bg"] = radioButtonsDefaultColor
        R3["fg"] = color
        R4["bg"] = radioButtonsDefaultColor
        R4["fg"] = color
        R5["bg"] = radioButtonsDefaultColor
        R5["fg"] = color
    elif (int(songRating.get()) == 2):
        labelSongRating["bg"] = color
        labelSongRating["fg"] = fontColor.get()
        R1["bg"] = color
        R1["fg"] = fontColor.get()
        R2["bg"] = color
        R2["fg"] = fontColor.get()
        R3["bg"] = radioButtonsDefaultColor
        R3["fg"] = color
        R4["bg"] = radioButtonsDefaultColor
        R4["fg"] = color
        R5["bg"] = radioButtonsDefaultColor
        R5["fg"] = color
    elif (int(songRating.get()) == 3):
        labelSongRating["bg"] = color
        labelSongRating["fg"] = fontColor.get()
        R1["bg"] = color
        R1["fg"] = fontColor.get()
        R2["bg"] = color
        R2["fg"] = fontColor.get()
        R3["bg"] = color
        R3["fg"] = fontColor.get()
        R4["bg"] = radioButtonsDefaultColor
        R4["fg"] = color
        R5["bg"] = radioButtonsDefaultColor
        R5["fg"] = color
    elif (int(songRating.get()) == 4):
        labelSongRating["bg"] = color
        labelSongRating["fg"] = fontColor.get()
        R1["bg"] = color
        R1["fg"] = fontColor.get()
        R2["bg"] = color
        R2["fg"] = fontColor.get()
        R3["bg"] = color
        R3["fg"] = fontColor.get()
        R4["bg"] = color
        R4["fg"] = fontColor.get()
        R5["bg"] = radioButtonsDefaultColor
        R5["fg"] = color
    elif (int(songRating.get()) == 5):
        labelSongRating["bg"] = color
        labelSongRating["fg"] = fontColor.get()
        R1["bg"] = color
        R1["fg"] = fontColor.get()
        R2["bg"] = color
        R2["fg"] = fontColor.get()
        R3["bg"] = color
        R3["fg"] = fontColor.get()
        R4["bg"] = color
        R4["fg"] = fontColor.get()
        R5["bg"] = color
        R5["fg"] = fontColor.get()
    else: #put the default color
        labelSongRating["bg"] = radioButtonsDefaultColor
        labelSongRating["fg"] = color
        R1["bg"] = radioButtonsDefaultColor
        R1["fg"] = color
        R2["bg"] = radioButtonsDefaultColor
        R2["fg"] = color
        R3["bg"] = radioButtonsDefaultColor
        R3["fg"] = color
        R4["bg"] = radioButtonsDefaultColor
        R4["fg"] = color
        R5["bg"] = radioButtonsDefaultColor
        R5["fg"] = color
    if len(play_list.validFiles) > 0 and play_list.currentSongIndex!=None:
        songRating.set(str(play_list.validFiles[play_list.currentSongIndex].Rating))

def changingFontColor(event):
    global play_list
    OpenFileButton["fg"] = fontColor.get()
    OpenDirectoryButton["fg"] = fontColor.get()
    PlayButton["fg"] = fontColor.get()
    PauseButton["fg"] = fontColor.get()
    StopButton["fg"] = fontColor.get()
    NextButton["fg"] = fontColor.get()
    PreviousButton["fg"] = fontColor.get()
    VolumeScale["fg"] = fontColor.get()
    ShuffleButton["fg"] = fontColor.get()
    SavePlaylistButton["fg"] = fontColor.get()
    NewPlaylistButton["fg"] = fontColor.get()
    ViewPlaylistButton["fg"] = fontColor.get()
    RepeatButton["fg"] = fontColor.get()
    RemoveSongButton["fg"] = fontColor.get()
    labelSkin["fg"] = fontColor.get()
    SortListButton["fg"] = fontColor.get()
    MoveUpButton["fg"] = fontColor.get()
    MoveDownButton["fg"] = fontColor.get()
    SearchButton["fg"] = fontColor.get()
    SleepButton["fg"] = fontColor.get()
    # changing listbox
    listbox["fg"] = fontColor.get()
    listbox["selectbackground"] = fontColor.get()
    if fontColor.get() != "white": #white is the default value which cannot be customized
        play_list.customFontColor = custom_color_list.index(fontColor.get())
    #destroy and rebuild the window so the the colors will also change on the customizer
    if type(dialog) == Customize: # this condition is true only when Customize window is opened
        dialog.destroy()
        Customize(window)
        showCurrentSongInList()

def changingLabelBackgroundColor(event):
    global play_list;
    # changing labels
    labelPlaying["background"] = labelBackground.get()
    labelDuration["background"] = labelBackground.get()
    labelSize["background"] = labelBackground.get()
    labelFilesToPlay["background"] = labelBackground.get()
    labelLength["background"] = labelBackground.get()
    labelGenre["background"] = labelBackground.get()
    labelStartTime["background"] = labelBackground.get()
    labelEndTime["background"] = labelBackground.get()
    labelTotalPlayTime["background"] = labelBackground.get()
    labelFallAsleep["background"] = labelBackground.get()
    labelWakeUp["background"] = labelBackground.get()
    labelFadeIn["background"] = labelBackground.get()
    labelFadeOut["background"] = labelBackground.get()
    labelMonoStereoMode["background"] = labelBackground.get()
    labelSampleRate["background"] = labelBackground.get()
    labelNofPlays["background"] = labelBackground.get()
    labelDanthologyMode["background"] = labelBackground.get()
    labelArtist["background"] = labelBackground.get()
    labelAlbum["background"] = labelBackground.get()
    labelTitle["background"] = labelBackground.get()
    labelSongListenedTime["background"] = labelBackground.get()
    labelPlaylistListenedTime["background"] = labelBackground.get()
    labelYear["background"] = labelBackground.get()
    if labelBackground.get() != "lightgray": #lightgray is the default color, if condition is true, means user cutomized it
        play_list.customLabelBackground = custom_color_list.index(labelBackground.get())
        showCurrentSongInList()

def changingBackgroundedLabelsColor(value, loading=1):
    global play_list
    if loading!=1:
        play_list.customChangeBackgroundedLabelsColor = int(value.get())
    if play_list.customChangeBackgroundedLabelsColor == True:
        labelPlaying["fg"] = fontColor.get()
        labelDuration["fg"] = fontColor.get()
        labelSize["fg"] = fontColor.get()
        labelFilesToPlay["fg"] = fontColor.get()
        labelLength["fg"] = fontColor.get()
        labelGenre["fg"] = fontColor.get()
        labelStartTime["fg"] = fontColor.get()
        labelEndTime["fg"] = fontColor.get()
        labelTotalPlayTime["fg"] = fontColor.get()
        labelFallAsleep["fg"] = fontColor.get()
        labelWakeUp["fg"] = fontColor.get()
        labelFadeOut["fg"] = fontColor.get()
        labelFadeIn["fg"] = fontColor.get()
        labelMonoStereoMode["fg"] = fontColor.get()
        labelSampleRate["fg"] = fontColor.get()
        labelNofPlays["fg"] = fontColor.get()
        labelDanthologyMode["fg"] = fontColor.get()
        labelArtist["fg"] = fontColor.get()
        labelAlbum["fg"] = fontColor.get()
        labelTitle["fg"] = fontColor.get()
        labelSongListenedTime["fg"] = fontColor.get()
        labelPlaylistListenedTime["fg"] = fontColor.get()
        labelYear["fg"] = fontColor.get()
    else:
        color = OpenFileButton["bg"] #put the same color as button background
        labelPlaying["fg"] = color
        labelDuration["fg"] = color
        labelSize["fg"] = color
        labelFilesToPlay["fg"] = color
        labelLength["fg"] = color
        labelGenre["fg"] = color
        labelStartTime["fg"] = color
        labelEndTime["fg"] = color
        labelTotalPlayTime["fg"] = color
        labelFallAsleep["fg"] = color
        labelWakeUp["fg"] = color
        labelFadeOut["fg"] = color
        labelFadeIn["fg"] = color
        labelMonoStereoMode["fg"] = color
        labelSampleRate["fg"] = color
        labelNofPlays["fg"] = color
        labelDanthologyMode["fg"] = color
        labelArtist["fg"] = color
        labelAlbum["fg"] = color
        labelTitle["fg"] = color
        labelSongListenedTime["fg"] = color
        labelPlaylistListenedTime["fg"] = color
        labelYear["fg"] = color
    showCurrentSongInList()

def move_up(): #this function is called when clicking Move Up Button
    global listBox_Song_selected_index
    if listBox_Song_selected_index != None:
        Song = play_list.validFiles[listBox_Song_selected_index] #this is the auxiliar variable
        if(listBox_Song_selected_index-1 >= 0):
            #interchanging values
            play_list.validFiles[listBox_Song_selected_index] = play_list.validFiles[listBox_Song_selected_index-1]
            play_list.validFiles[listBox_Song_selected_index - 1] = Song
            listBox_Song_selected_index -=1
        else:
            last_position = len(play_list.validFiles) - 1
            play_list.validFiles[listBox_Song_selected_index] = play_list.validFiles[last_position]
            play_list.validFiles[last_position] = Song
            listBox_Song_selected_index = last_position
        displayElementsOnPlaylist()
        listbox.select_set(listBox_Song_selected_index)
        listbox.see(listBox_Song_selected_index)
        # listBox_Song_selected_index=None #initialize this if u want to move only onebyone
        play_list.isListOrdered = 17 #this will mean Custom Sorting
        updateSortButton()

def move_down(): #this function is called when clicking Move Down Button
    global listBox_Song_selected_index
    if listBox_Song_selected_index != None:
        Song = play_list.validFiles[listBox_Song_selected_index]  # this is the auxiliar variable
        if (listBox_Song_selected_index + 1 < len(play_list.validFiles)):
            # interchanging values
            play_list.validFiles[listBox_Song_selected_index] = play_list.validFiles[listBox_Song_selected_index + 1]
            play_list.validFiles[listBox_Song_selected_index + 1] = Song
            listBox_Song_selected_index += 1
        else:
            play_list.validFiles[listBox_Song_selected_index] = play_list.validFiles[0]
            play_list.validFiles[0] = Song
            listBox_Song_selected_index = 0
        displayElementsOnPlaylist()
        listbox.select_set(listBox_Song_selected_index)
        listbox.see(listBox_Song_selected_index)
        # listBox_Song_selected_index=None #initialize this if u want to move only onebyone
        play_list.isListOrdered = 17 #this will mean Custom Sorting
        updateSortButton()

def changeFonts():
    OpenFileButton["font"] = allButtonsFont
    OpenDirectoryButton["font"] = allButtonsFont
    PlayButton["font"] = allButtonsFont
    PauseButton["font"] = allButtonsFont
    StopButton["font"] = allButtonsFont
    NextButton["font"] = allButtonsFont
    PreviousButton["font"] = allButtonsFont
    VolumeScale["font"] = allButtonsFont
    ShuffleButton["font"] = allButtonsFont
    SavePlaylistButton["font"] = allButtonsFont
    NewPlaylistButton["font"] = allButtonsFont
    ViewPlaylistButton["font"] = allButtonsFont
    RepeatButton["font"] = allButtonsFont
    RemoveSongButton["font"] = allButtonsFont
    SortListButton["font"] = allButtonsFont
    MoveUpButton["font"] = allButtonsFont
    MoveDownButton["font"] = allButtonsFont
    SearchButton["font"] = allButtonsFont
    SleepButton["font"] = allButtonsFont
    # changing labels
    labelPlaying["font"] = allButtonsFont
    labelDuration["font"] = allButtonsFont
    labelSize["font"] = allButtonsFont
    labelFilesToPlay["font"] = allButtonsFont
    labelLength["font"] = allButtonsFont
    labelGenre["font"] = allButtonsFont
    labelStartTime["font"] = allButtonsFont
    labelEndTime["font"] = allButtonsFont
    labelTotalPlayTime["font"] = allButtonsFont
    labelFallAsleep["font"] = allButtonsFont
    labelWakeUp["font"] = allButtonsFont
    labelFadeOut["font"] = allButtonsFont
    labelFadeIn["font"] = allButtonsFont
    labelMonoStereoMode["font"] = allButtonsFont
    labelSampleRate["font"] = allButtonsFont
    labelNofPlays["font"] = allButtonsFont
    labelDanthologyMode["font"] = allButtonsFont
    labelArtist["font"] = allButtonsFont
    labelAlbum["font"] = allButtonsFont
    labelTitle["font"] = allButtonsFont
    labelSongListenedTime["font"] = allButtonsFont
    labelPlaylistListenedTime["font"] = allButtonsFont
    labelYear["font"] = allButtonsFont
    labelSkin["font"] = allButtonsFont
    # changing listbox
    listbox["font"] = allButtonsFont
    option["font"] = allButtonsFont
    #changing radiobuttons:
    R1["font"] = allButtonsFont
    R2["font"] = allButtonsFont
    R3["font"] = allButtonsFont
    R4["font"] = allButtonsFont
    R5["font"] = allButtonsFont
    labelSongRating["font"] = allButtonsFont
    buttonAdjustments()
    reSpacePositionElements()  # respace elements

def packPositionButton(): #function called only at the startup to place the buttons for COMPACT view
    # column1:
    global play_list
    horizontalButtonsColumnStartCoord = 5
    horizontalSpaceBetweenButtonColumns = 168

    RepeatButton.place(x=horizontalButtonsColumnStartCoord, y=5)
    ViewPlaylistButton.place(x=horizontalButtonsColumnStartCoord, y=37)
    PreviousButton.place(x=horizontalButtonsColumnStartCoord, y=69)
    ShuffleButton.place(x=horizontalButtonsColumnStartCoord, y=101)
    play_list.buttonSpacing = horizontalSpaceBetweenButtonColumns - ShuffleButton.winfo_reqwidth()

    # column2:
    horizontalButtonsColumnStartCoord += horizontalSpaceBetweenButtonColumns
    OpenFileButton.place(x=horizontalButtonsColumnStartCoord, y=5)
    OpenDirectoryButton.place(x=horizontalButtonsColumnStartCoord, y=37)
    PlayButton.place(x=horizontalButtonsColumnStartCoord, y=69)
    PauseButton.place(x=horizontalButtonsColumnStartCoord, y=101)

    # column3:
    horizontalButtonsColumnStartCoord += horizontalSpaceBetweenButtonColumns
    SavePlaylistButton.place(x=horizontalButtonsColumnStartCoord, y=5)
    NewPlaylistButton.place(x=horizontalButtonsColumnStartCoord, y=37)
    NextButton.place(x=horizontalButtonsColumnStartCoord, y=69)
    StopButton.place(x=horizontalButtonsColumnStartCoord, y=101)
    SleepButton.place(x=horizontalButtonsColumnStartCoord, y=133)
    SearchButton.place(x=horizontalButtonsColumnStartCoord, y=159)

def reSpacePositionElements(): #function called when changing skin, fonts or appearance to reposition the elements (buttons, listbox, labels, progressbar)
    global progressBarLength

    spaceReq = OpenFileButton.winfo_reqwidth()
    # column2
    OpenFileButton.place(x=spaceReq + play_list.buttonSpacing, y=5)
    OpenDirectoryButton.place(x=spaceReq + play_list.buttonSpacing, y=37)
    PlayButton.place(x=spaceReq + play_list.buttonSpacing, y=69)
    PauseButton.place(x=spaceReq + play_list.buttonSpacing, y=101)
    SkinFrame.place(x=spaceReq + play_list.buttonSpacing, y=133)

    # column3:
    SavePlaylistButton.place(x= (2 * spaceReq) + (2 * play_list.buttonSpacing), y=5)
    NewPlaylistButton.place(x=(2 * spaceReq) + (2 * play_list.buttonSpacing), y=37)
    NextButton.place(x=(2 * spaceReq) + (2 * play_list.buttonSpacing), y=69)
    StopButton.place(x=(2 * spaceReq) + (2 * play_list.buttonSpacing), y=101)
    SleepButton.place(x=(2 * spaceReq) + (2 * play_list.buttonSpacing), y=133)
    SearchButton.place(x=(2 * spaceReq) + (2 * play_list.buttonSpacing), y=159)

    #labels column2
    labelFilesToPlay.place(x=190+play_list.buttonSpacing, y=210)
    labelTotalPlayTime.place(x=190+play_list.buttonSpacing, y=230)
    labelSampleRate.place(x=190+play_list.buttonSpacing, y=250)
    labelFadeIn.place(x=190+play_list.buttonSpacing, y=270)
    labelFadeOut.place(x=190+play_list.buttonSpacing, y=290)
    labelFallAsleep.place(x=190+play_list.buttonSpacing, y=310)
    labelWakeUp.place(x=190+play_list.buttonSpacing, y=330)
    labelDanthologyMode.place(x=190+play_list.buttonSpacing, y=350)

    #progressbar
    progressBarLength = (3 * spaceReq) + (2 * play_list.buttonSpacing) - progressBarMargin
    progress["length"] = progressBarLength
    labelPlaying["wraplength"] = progressBarLength
    
    changePlaylistView()

def packPositionLabels(): #function called only at the start, to position the labels.
    # Placing the labels
    labelDuration.place(x=10, y=210)
    labelSize.place(x=10, y=230)
    labelLength.place(x=10, y=250)
    labelGenre.place(x=10, y=270)
    labelStartTime.place(x=10, y=290)
    labelEndTime.place(x=10, y=310)
    labelNofPlays.place(x=10, y=330)
    labelMonoStereoMode.place(x=10, y=350)

    labelFilesToPlay.place(x=250, y=210)
    labelTotalPlayTime.place(x=250, y=230)
    labelSampleRate.place(x=250, y=250)
    labelFadeIn.place(x=250, y=270)
    labelFadeOut.place(x=250, y=290)
    labelFallAsleep.place(x=250, y=310)
    labelWakeUp.place(x=250, y=330)
    labelDanthologyMode.place(x=250, y=350)
    #under progressBar:
    labelPlaying.place(x=10, y=405)

    labelArtist.place(x=10, y=490)
    labelYear.place(x=10, y=510)
    labelTitle.place(x=10, y=530)
    labelAlbum.place(x=10, y=550)
    labelSongListenedTime.place(x=10, y=570)
    labelPlaylistListenedTime.place(x=10, y=590)

def pressedEnter(event):
    if pygame.mixer.get_init():
        if pygame.mixer.music.get_busy():
            next_song()
        else:
            play_music()
    else:
        play_music()

def pressedShiftRight(event):
    if pygame.mixer.get_init():
        if pygame.mixer.music.get_busy():
            previous_song()
        else:
            play_music()
    else:
        play_music()
        
def pressedTab(event):
    if dialog != None:
        #it means there is another window opened:
        dialog.take_focus()
    elif Slideshow.top!=None:
        Slideshow.take_focus()

def pressedShiftLeft(event):
    move_up()

def pressedCtrlLeft(event):
    move_down()
    
def pressedDelete(event):
    remove_song()

def pressedKeyShortcut(event):
    if event.char == " ":
        pause_music()
    elif event.char == "m" or event.char == "M":
        if pygame.mixer.get_init():
            if pygame.mixer.music.get_volume()>0:
                pygame.mixer.music.set_volume(0)
                play_list.VolumeLevel = 0.0
                VolumeScale.set(play_list.VolumeLevel)
            else:
                pygame.mixer.music.set_volume(play_list.VolumeLevel)
                VolumeScale.set(play_list.VolumeLevel * 100)
    elif event.char == ",":
        volume_up()
    elif event.char == ".":
        volume_down()
    elif event.char == "r" or event.char == "R":
        repeat()
    elif event.char == "c" or event.char == "C":
        view_playlist()
    elif event.char =="s" or event.char =="S":
        shuffle()
    elif event.char =="d" or event.char =="D":
        stop_music()
    elif event.char == "1":
        if pygame.mixer.get_init():
            play_list.VolumeLevel = 0.1
            pygame.mixer.music.set_volume(play_list.VolumeLevel)
            VolumeScale.set(play_list.VolumeLevel * 100)
    elif event.char == "2":
        if pygame.mixer.get_init():
            play_list.VolumeLevel = 0.2
            pygame.mixer.music.set_volume(play_list.VolumeLevel)
            VolumeScale.set(play_list.VolumeLevel * 100)
    elif event.char == "3":
        if pygame.mixer.get_init():
            play_list.VolumeLevel = 0.3
            pygame.mixer.music.set_volume(play_list.VolumeLevel)
            VolumeScale.set(play_list.VolumeLevel * 100)
    elif event.char == "4":
        if pygame.mixer.get_init():
            play_list.VolumeLevel = 0.4
            pygame.mixer.music.set_volume(play_list.VolumeLevel)
            VolumeScale.set(play_list.VolumeLevel * 100)
    elif event.char == "5":
        if pygame.mixer.get_init():
            play_list.VolumeLevel = 0.5
            pygame.mixer.music.set_volume(play_list.VolumeLevel)
            VolumeScale.set(play_list.VolumeLevel * 100)
    elif event.char == "6":
        if pygame.mixer.get_init():
            play_list.VolumeLevel = 0.6
            pygame.mixer.music.set_volume(play_list.VolumeLevel)
            VolumeScale.set(play_list.VolumeLevel * 100)
    elif event.char == "7":
        if pygame.mixer.get_init():
            play_list.VolumeLevel = 0.7
            pygame.mixer.music.set_volume(play_list.VolumeLevel)
            VolumeScale.set(play_list.VolumeLevel * 100)
    elif event.char == "8":
        if pygame.mixer.get_init():
            play_list.VolumeLevel = 0.8
            pygame.mixer.music.set_volume(play_list.VolumeLevel)
            VolumeScale.set(play_list.VolumeLevel * 100)
    elif event.char == "9":
        if pygame.mixer.get_init():
            play_list.VolumeLevel = 0.9
            pygame.mixer.music.set_volume(play_list.VolumeLevel)
            VolumeScale.set(play_list.VolumeLevel * 100)
    elif event.char == "0":
        if pygame.mixer.get_init():
            play_list.VolumeLevel = 1.0
            pygame.mixer.music.set_volume(play_list.VolumeLevel)
            VolumeScale.set(play_list.VolumeLevel * 100)
    elif event.char == "a" or event.char == "A":
        if Slideshow.top==None:
            Slideshow()
    elif event.char == "p" or event.char == "P":
        Customize(window)
    elif event.char == "i" or event.char == "I":
        messagebox.showinfo("Information", "Congratulation for discovering navigational keys! \n\n"
                + "As you might not know all the keys, here is a full guide:\n\n"
                + "S - is equivalent to Shuffle Button.\n"
                + "D - is equivalent to Stop Button.\n"
                + "R - is equivalent to Repeat Button.\n"
                + "SHIFT_R - is equivalent to Previous Button.\n"
                + "ENTER - is equivalent to Next Button.\n"
                + "C - is equivalent to View Button.\n"
                + "M - is equivalent to Mute.\n"
                + "Q - is equivalent to Cut Selected Button\n"
                + "T - is equivalent to Sleep\Wake Button\n"
                + "L - is equivalent to GrabLyrics\n"
				+ "G - is equivalent to ArtistBio\n"
                + "J - is equivalent to Search Button\n"
                + "P - is equivalent to Customize Option\n"
                + "A - is equivalent to Slideshow\n"
                + "[ ] - will move Song Progress to Left or Right\n"
                + "[0-9] - are equivalent to Volume Set 10% - 100%.\n"
                + "SPACE - is equivalent to Pause, or press the active button selected using Tab.\n"
                + "TAB - slides between the opened windows, or active elements.\n"
                + "L_SHIFT - is equivalent to Move Up on the current playlist song selection.\n"
                + "L_CTRL - is equivalent to Move Down on the current playlist song selection.\n"
                + "Delete - is equivalent to Remove on the current playlist song selection.\n"
                + ", or < key - is equivalent to Volume Up.\n"
                + ". or > key - is equivalent to Volume Down.\n"
                + "Page Up or Up - can be used to navigate the playlist UP.\n"
                + "Page Down or Down - can be used to navigate the playlist DOWN.\n"
                + "i - will show you this message again.")
    elif event.char == "q" or event.char == "Q":
        showCuttingTool()
    elif event.char =="j" or event.char =="J":
        searchSongInPlaylist()
    elif event.char == "t" or event.char == "T":
        showSleepingTool()
    elif event.char == "h" or event.char == "H":
        Mp3TagModifierTool()
    elif event.char == "l" or event.char == "L":
        showGrabLyricsWindow()
    elif event.char == "g" or event.char == "G":
        showArtistBioWindow()
    elif event.char == "]":
        windSongRight() #this will move song progress to the right
    elif event.char == "[":
        windSongLeft() #this will move song progress to the left

def listboxShortcuts(event):
    if event.char == "w":
        if dialog == None:
            if listBox_Song_selected_index!=None and type(dialog) != SearchTool:
                Mp3TagModifierTool(listBox_Song_selected_index)
                dialog.ComposeNameCheckButtonVar.set(1)
                dialog.checkUncheckNameComposal(event)
                dialog.SaveChanges()
                dialog.destroy()
        else:
            messagebox.showinfo("Information", "Please close the other component window to do this.")

def songInfo():
    element = play_list.validFiles[listBox_Song_selected_index]
    messagebox.showinfo("Song Info", "Info About File: \n\n"
                                    + "Filename: " + str(element.fileName) + "\n"
                                    + "Path: " + str(element.filePath) + "\n"
                                    + "Size: " + str(element.fileSize) + " MB\n"
                                    
                                    +"\nFile Tags:\n\n"
                                    + "Album: " + str(element.Album) + "\n"
                                    + "Year: " + str(element.Year) + "\n"
                                    + "Genre: " + str(element.Genre) + "\n"
                                    + "Artist: " + str(element.Artist) + "\n"
                                    + "Title: " + str(element.Title) + "\n"
                                    + "Length: {:0>8}" .format(str(datetime.timedelta(seconds = int(element.Length))) ) + "\n"
                                    
                                    + "\nInternal Player Settings:\n\n"
                                    + "Rating: " + str(element.Rating) + "\n"
                                    + "FadeIn: " + str(element.fadein_duration) + "\n"
                                    + "FadeOut: " + str(element.fadeout_duration) + "\n"
                                    + "Start Time: {:0>8}" .format(str(datetime.timedelta(seconds = int(element.startPos))) ) + "\n"
                                    + "End Time: {:0>8}" .format(str(datetime.timedelta(seconds = int(element.endPos))) ) + "\n"
                                    + "Number Of Plays: " + str(element.NumberOfPlays) + "\n")

def openFileInExplorer():
    file = play_list.validFiles[listBox_Song_selected_index].filePath
    FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
    subprocess.Popen([FILEBROWSER_PATH, '/select,', os.path.normpath(file)])

def rightClickListboxElement(event):
    if listBox_Song_selected_index != None:
        listboxSelectedEvent = event.widget
        if len(listboxSelectedEvent.curselection()) > 0:
            if type(dialog) != SearchTool:
                index = int(listboxSelectedEvent.curselection()[0])
            else:
                index = int(listboxSelectedEvent.curselection()[0])
                value = listbox.get(index)
                value = value.split(". ")
                index = int(value[0])
            aMenu = tk.Menu(window, tearoff=0)
            aMenu.add_command(label='Randomize List', command=sortRandomized)
            aMenu.add_command(label='Delete', command=remove_song)
            aMenu.add_command(label='File Info', command=songInfo)
            aMenu.add_command(label='Move Up', command=move_up)
            aMenu.add_command(label='Move Down', command=move_down)
            aMenu.add_command(label='Open in Explorer', command=openFileInExplorer)
            aMenu.add_command(label='Show Current Song', command=showCurrentSongInList)
            aMenu.add_command(label='MP3 Tag Modifier', command= lambda:showMp3TagModifierWindow(index))
            aMenu.add_command(label='Grab Song Lyrics', command= lambda:showGrabLyricsWindow(index))
            aMenu.add_command(label='Grab Artist Bio', command= lambda:showArtistBioWindow(index))
            aMenu.add_command(label='Cut File', command= lambda:showCuttingTool(index))
            aMenu.post(event.x_root, event.y_root)

def showCurrentSongInList():
    global listBox_Song_selected_index
    if listbox.size() > 0 and play_list.currentSongIndex < listbox.size(): #make playing song visible
        listbox.see(play_list.currentSongIndex)
        listBox_Song_selected_index = play_list.currentSongIndex
        listbox.selection_clear(0, tk.END)  # clear existing selection
        listbox.select_set(listBox_Song_selected_index)

def showMp3TagModifierWindow(index):
    if dialog == None:
        Mp3TagModifierTool(index)
    else:
        messagebox.showinfo("Information", "Please close the other component window before proceed.")
        
def showAboutWindow():
    messagebox.showinfo("About",
            "Hello!\n"+
            "\nWelcome To PyPlay Mp3 Player,\n\n"+
            "This Application was developed by Dragos Vacariu from 14 June 2019 to 21 July 2019, "+
            "with the main purpose of testing programming capabilities, especially python skills.\n"+
            "Work efforts were around 140 hours, so "+
            "there might still be bugs left behind for me to find out later.\n"+
            "\nMy Contact Details are the following:\n" +
            "Email: dragos.vacariu@mail.com\n" +
            "LinkedIn: www.linkedin.com/in/dragos-vacariu-em\n"+
            "\nOther projects I test my skills on, are available at:\n"+
            "GitHub Repository: github.com/dragos-vacariu/ \n"
            "\nThank you for trying PyPlay!\n")

def showCustomizeWindow():
    if dialog == None:
        Customize(window)
    else:
        messagebox.showinfo("Information", "Please close the other component window before proceed.")

def showGrabLyricsWindow(index="empty"):
    if dialog == None:
        GrabLyricsTool(index)
    else:
        messagebox.showinfo("Information", "Please close the other component window before proceed.")

def showArtistBioWindow(index="empty"):
    if dialog == None:
        GrabArtistBio(index)
    else:
        messagebox.showinfo("Information", "Please close the other component window before proceed.")

def showSlideshowWindow():
    if Slideshow.top == None:
        Slideshow()
    else:
        messagebox.showinfo("Information", "Slideshow is already opened.")

def rightClickOnWindow(event):
    if window.winfo_containing(event.x_root, event.y_root) != listbox: # don't execute this if the cursor is inside the listbox
        aMenu = tk.Menu(window, tearoff=0)
        aMenu.add_command(label='About', command=showAboutWindow)
        aMenu.add_command(label='Customize', command=showCustomizeWindow)
        aMenu.add_command(label='Slideshow', command=showSlideshowWindow)
        aMenu.add_command(label='Sleeping Tool', command=showSleepingTool)
        aMenu.add_command(label='Cutting Tool', command=showCuttingTool)
        aMenu.add_command(label='Search Tool', command=searchSongInPlaylist)
        aMenu.add_command(label='Grab Lyrics', command=showGrabLyricsWindow)
        aMenu.add_command(label='Artist Bio', command=showArtistBioWindow)
        aMenu.add_command(label='Playlist Info', command=showPlaylistInfo)
        aMenu.post(event.x_root, event.y_root)  

def calculatePlaylistNumberOfPlays():
    totalPlays = 0
    for song in play_list.validFiles:
        totalPlays+= song.NumberOfPlays
    return totalPlays   

def calculatePlaylistFilesSize():
    totalSize = 0
    for song in play_list.validFiles:
        totalSize+= song.fileSize
    return totalSize      

def calculatePlaylistCutLength():
    cutLength = 0
    for song in play_list.validFiles:
        cutLength+= song.Length - (song.endPos-song.startPos)
    return cutLength 
    
def findFavoriteGenre():
    genres = {}
    for song in play_list.validFiles:
        if song.Genre not in genres.keys():
            genres[song.Genre] = song.SongListenedTime
        else:
            genres[song.Genre] += song.SongListenedTime
    
    genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
    most_wanted = genres[0]
    return [str(most_wanted[0]), int(most_wanted[1])]

def findFavoriteTrack():
    if len(play_list.validFiles) > 0:
        favoriteSong = play_list.validFiles[0]
        for song in play_list.validFiles:
            if favoriteSong.SongListenedTime < song.SongListenedTime:
                favoriteSong = song
        return favoriteSong
    else:
        return "NA"
    
def showPlaylistInfo():
    favoriteSong = findFavoriteTrack()
    if favoriteSong=="NA":
        messagebox.showinfo("Playlist Info", "OVERALL:" +"\n"
                                        +"Number of Files: \t\t" + str(len(play_list.validFiles)) +"\n"
                                        +"Number of Plays: \t\t" + str(calculatePlaylistNumberOfPlays())+ "\n"
                                        +"Total Length: \t\t" + str(datetime.timedelta(seconds=int(play_list.playTime))) + "\n"
                                        +"Cutted Length: \t\t" + str(datetime.timedelta(seconds=int(calculatePlaylistCutLength()))) + "\n"
                                        +"Playable Length: \t\t" + str(datetime.timedelta(seconds=int(play_list.playTime - calculatePlaylistCutLength()))) + "\n"
                                        +"Total Size: \t\t" + str(round(calculatePlaylistFilesSize())) + "MB\n"
                                        +"Time Listened: \t\t" +str(datetime.timedelta(seconds=int(play_list.PlaylistListenedTime))) + "\n"
                                        +"Created On: \t\t" +str(play_list.BornDate)[:19] + "\n")
    else:
        messagebox.showinfo("Playlist Info", "OVERALL:" +"\n"
                                            +"Number of Files: \t\t" + str(len(play_list.validFiles)) +"\n"
                                            +"Number of Plays: \t\t" + str(calculatePlaylistNumberOfPlays())+ "\n"
                                            +"Total Length: \t\t" + str(datetime.timedelta(seconds=int(play_list.playTime))) + "\n"
                                            +"Cutted Length: \t\t" + str(datetime.timedelta(seconds=int(calculatePlaylistCutLength()))) + "\n"
                                            +"Playable Length: \t\t" + str(datetime.timedelta(seconds=int(play_list.playTime - calculatePlaylistCutLength()))) + "\n"
                                            +"Total Size: \t\t" + str(round(calculatePlaylistFilesSize())) + "MB\n"
                                            +"Time Listened: \t\t" +str(datetime.timedelta(seconds=int(play_list.PlaylistListenedTime))) + "\n"
                                            +"Created On: \t\t" +str(play_list.BornDate)[:19] + "\n" #[:19] will cut so that miliseconds won't be displayed in date
                                            +"\nFAVORITE GENRE:\n"
                                            +"Favorite Music Genre: \t" + findFavoriteGenre()[0] + "\n"
                                            + findFavoriteGenre()[0] + " listened: \t\t" + str(datetime.timedelta(seconds=findFavoriteGenre()[1])) + "\n"
                                            +"\nMOST LISTENED:\n"
                                            + favoriteSong.fileName + "\n"
                                            + "Listen Time: \t\t" + str(datetime.timedelta(seconds=int(favoriteSong.SongListenedTime))) + "\n"
                                            + "Number of Plays: \t\t" + str(favoriteSong.NumberOfPlays) + "\n"
                                            + "Song Rating: \t\t" + "NA" if favoriteSong.Rating==0 else str(favoriteSong.Rating) + "\n")
        
def packPositionListScrolOptionProgRadio(): #function called only at the start, to place the listbox, scrollbar, combobox, radiobuttons, progressbar,
    #Here are set position, events, controls, styling for listbox, progressbar, scrollbar, option, radiobuttons
    listbox.pack(side = tk.LEFT, padx=2, pady=6) #this will place listbox on the leftside of the FRAME
    listbox.bind('<Double-Button>', elementPlaylistDoubleClicked)
    listbox.bind('<ButtonPress-3>', rightClickListboxElement)
    listbox.bind('<<ListboxSelect>>', list_selected_item)
    listbox.bind("<Return>", pressedEnter)
    listbox.bind("<Key>", listboxShortcuts)
    #listbox.bind("<Right>", changeListboxElementView)
    window.bind("<Return>", pressedEnter)
    window.bind("<Shift_R>", pressedShiftRight)
    window.bind("<Tab>", pressedTab)
    window.bind("<Key>", pressedKeyShortcut)
    window.bind("<Shift_L>", pressedShiftLeft)
    window.bind("<Control_L>", pressedCtrlLeft)
    window.bind("<KeyRelease-]>", squareBracketsReleased)
    window.bind("<KeyRelease-[>", squareBracketsReleased)
    window.bind("<Delete>", pressedDelete)
    window.bind('<ButtonPress-3>', rightClickOnWindow)
  
    scroll.config(command=listbox.yview)
    scroll.pack(side = tk.RIGHT, fill=tk.Y) #this will place scrollbar on the right side of FRAME, if width is adjusted, they will be next to each other
    option.bind("<<ComboboxSelected>>", changeSkin)
    labelSkin.pack(pady=2, anchor=tk.W)
    option.pack(anchor=tk.W, pady=0)
    styl.theme_use('clam')
    styl.configure("Horizontal.TProgressbar", foreground='red', background='blue')
    progress.bind("<Button>", navigationSound)
    progress.place(x=progressBarMargin, y=380)

    radioButtonLineHeight = 450
    labelSongRating.place(x=10, y=radioButtonLineHeight)
    RadioButtonsPosX=labelSongRating.winfo_reqwidth()+10 #10 - the X margin of the label
    R1.place(x=RadioButtonsPosX, y=radioButtonLineHeight)
    R2.place(x=RadioButtonsPosX+45, y=radioButtonLineHeight)
    R3.place(x=RadioButtonsPosX+90, y=radioButtonLineHeight)
    R4.place(x=RadioButtonsPosX+135, y=radioButtonLineHeight)
    R5.place(x=RadioButtonsPosX+180, y=radioButtonLineHeight)
    VolumeScale.place(x=5, y=133)
    VolumeScale.bind("<ButtonRelease-1>", setLinearVolume)
    SkinFrame.place(x=173, y=133)
    SkinFrame.pack_propagate(False) #frame will have fixed size
    
    calculateScreenHeightWidth() #this will draw the listbox

def buttonAdjustments(): #this function will adjust some buttons (which are near labels) when the font gets changed
    # Adjust these elements
    VolumeScale["length"] = PlayButton.winfo_reqwidth() - 7  # make the volume scale have same width as the rest of the buttons , -7 because of the borders
    SkinFrame["width"] = PlayButton.winfo_reqwidth() - 2  # -2 because of border
    SkinFrame["height"] = VolumeScale.winfo_reqheight() - 2  # -2 because of border
    radioButtonLineHeight = 450
    labelSongRating.place(x=10, y=radioButtonLineHeight)
    RadioButtonsPosX = labelSongRating.winfo_reqwidth() + 10 #the X margin of the label
    R1.place(x=RadioButtonsPosX, y=radioButtonLineHeight)
    R2.place(x=RadioButtonsPosX + 45, y=radioButtonLineHeight)
    R3.place(x=RadioButtonsPosX + 90, y=radioButtonLineHeight)
    R4.place(x=RadioButtonsPosX + 135, y=radioButtonLineHeight)
    R5.place(x=RadioButtonsPosX + 180, y=radioButtonLineHeight)

def setLinearVolume(event): #function called when moving the Volume Slider
    global play_list
    if pygame.mixer.get_init():
        play_list.VolumeLevel = VolumeScale.get()/100
        if play_list.currentSongPosition - play_list.validFiles[play_list.currentSongIndex].startPos > \
                play_list.validFiles[play_list.currentSongIndex].fadein_duration and play_list.currentSongPosition < \
                        play_list.validFiles[play_list.currentSongIndex].endPos - play_list.validFiles[
                    play_list.currentSongIndex].fadeout_duration:
            pygame.mixer.music.set_volume(play_list.VolumeLevel)

def showCuttingTool(index=None): 
    if listbox.size() and listBox_Song_selected_index!= None:
        if dialog == None:
            if play_list.useCrossFade == False:
                CuttingTool(window, index)
            else:
                messagebox.showinfo("Information", "Sorry!\n\nYou cannot use this feature while cross-fading is enabled.\n\n"+
                "Cross-fading readjust the length of your tracks so that you won't hear gaps between them.")
        else:
            messagebox.showinfo("Information", "Please close the other component window before proceed.")
    else:
        messagebox.showinfo("No file selected", "Use the playlist to select a song.")

def showSleepingTool():
    if dialog == None:
        SleepingTool(window)
    else:
        messagebox.showinfo("Information","Please close the other component window before proceed.")

def fontTitleTransition(Message):
    Message = list(Message)
    for x in range(0, len(Message)):
        if(x+1<len(Message)):
            aux = Message[x+1]
            Message[x] = Message[x+1]
            Message[x+1] = aux
        else:
            aux = Message[0]
            Message[x] = Message[0]
            Message[0] = aux
    return "".join(Message)

def fontSeparatedTransition(Message):
    Message = list(Message)
    for x in range(0, len(Message)):
        if Message[x] == "_":
            if x+1 < len(Message):
                aux = Message[x+1]
                Message[x+1] = Message[x]
                Message[x] = aux
            else:
                Message ="".join(Message)
                Message = Message.split("_")
                Message = Message[0]
                Message = "_" + Message
            break
    return "".join(Message)
    
def fontTypeWritingTransition(Message):
    if Message == play_list.validFiles[play_list.currentSongIndex].fileName:
        Message = ""
    else:
        Message += play_list.validFiles[play_list.currentSongIndex].fileName[len(Message)]
    return Message

def searchSongInPlaylist(): #this function will show the Search Tool.
    if dialog == None:
        SearchTool(window)
    else:
        messagebox.showinfo("Information","Please close the other component window before proceed.")

def fadein(Position): 
    pygame.mixer.music.set_volume(Position/play_list.validFiles[play_list.currentSongIndex].fadein_duration)

def fadeout(Position):
    pygame.mixer.music.set_volume(Position/play_list.validFiles[play_list.currentSongIndex].fadeout_duration)

def computeTimeToSeconds(time):
        time = time.split(":")
        returnVal = 0
        for entity in time:
            if entity!="":
                index = time.index(entity)
                try:
                    entity=int(entity)
                except Exception:
                    messagebox.showinfo("Information", "An invalid value was entered.")
                    return -1
                else:
                    returnVal += entity* (60**(len(time)-1-index))
            else:
                messagebox.showinfo("Information", "Miss-use of ':' symbol, the entered value is invalid.")
                return -1
        return returnVal    
    
window = tk.Tk() #tk.Tk() return a widget which is window
Project_Title = "   PyPlay MP3 Player in Python     "
window.title(Project_Title)

window.geometry("500x430+" + str(play_list.playerXPos) + "+" + str(play_list.playerYPos))# build a window 500x430 pixels, at specified position
window.protocol("WM_DELETE_WINDOW", on_closing) #delete the window when clicking cancel, on closing is the function to deal with it

if os.path.isfile("headphone.ico"):
    window.wm_iconbitmap("headphone.ico")
else:
    print("File: 'headphone.ico' was not found in the project directory.\nNo icon was set.")
SkinColor = StringVar()
SkinColor.set(skinOptions[1][play_list.skin])
backgroundFile = skinOptions[0][play_list.skin]

fontColor = StringVar()
fontColor.set("white")

background_label = tk.Label(window)
background_label.pack()
background_label.place(x=0, y=0, relwidth=1, relheight=1)

#Loading default background
if os.path.exists(backgroundFile) and os.path.isfile(backgroundFile):
    play_list.customBackgroundPicture = backgroundFile
    background_image = tk.PhotoImage(file=backgroundFile)
    background_label.configure(image=background_image)
    background_label.image = background_image
else:
    print("File: " + str(backgroundFile) + " could not be found.")

OpenFileButton = tk.Button(window,  #the first parameter is the widget
                   text='Open File',  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=load_file, #the width of the button, and the function which get called when clicking it
                   bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

OpenDirectoryButton = tk.Button(window,  #the first parameter is the widget
                   text='Open Directory',  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=load_directory, #the width of the button, and the function which get called when clicking it
                    bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

PlayButton = tk.Button(window,  #the first parameter is the widget
                   text='Play',  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=play_music, #the width of the button, and the function which get called when clicking it
                    bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

PausedButtonText = StringVar()
PausedButtonText.set("Pause")
PauseButton = tk.Button(window,  #the first parameter is the widget
                   textvariable=PausedButtonText,  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=pause_music, #the width of the button, and the function which get called when clicking it
                    bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

StopButton = tk.Button(window,  #the first parameter is the widget
                   text="Stop",  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=stop_music, #the width of the button, and the function which get called when clicking it
                    bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                    font=allButtonsFont) #this is the font, size and type

NextButton = tk.Button(window,  #the first parameter is the widget
                   text="Next",  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=next_song, #the width of the button, and the function which get called when clicking it
                       bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

PreviousButton = tk.Button(window,  #the first parameter is the widget
                   text="Previous",  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=previous_song, #the width of the button, and the function which get called when clicking it
                           bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

ShuffleButtonText = StringVar()
ShuffleButtonText.set("Shuffle Off")

ShuffleButton = tk.Button(window,  #the first parameter is the widget
                   textvariable=ShuffleButtonText,  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=shuffle, #the width of the button, and the function which get called when clicking it
                    bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

SavePlaylistButton = tk.Button(window,  #the first parameter is the widget
                   text="Save Playlist",  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=save_playlist, #the width of the button, and the function which get called when clicking it
                    bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

NewPlaylistButton = tk.Button(window,  #the first parameter is the widget
                   text="New Playlist",  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=new_playlist, #the width of the button, and the function which get called when clicking it
                    bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

ViewPlaylistButtonText = StringVar()
ViewPlaylistButtonText.set("Compact View")

ViewPlaylistButton = tk.Button(window,  #the first parameter is the widget
                   textvariable=ViewPlaylistButtonText,  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=view_playlist, #the width of the button, and the function which get called when clicking it
                    bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

RepeatButtonText = StringVar()
RepeatButtonText.set("Repeat All")

RepeatButton = tk.Button(window,  #the first parameter is the widget
                   textvariable=RepeatButtonText,  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=repeat, #the width of the button, and the function which get called when clicking it
                    bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

RemoveSongButton = tk.Button(window,  #the first parameter is the widget
                   text="Remove Song",  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=remove_song, #the width of the button, and the function which get called when clicking it
                    bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

SortButtonText = StringVar()
SortButtonText.set("Sorted")

SortListButton = tk.Button(window,  #the first parameter is the widget
                   textvariable=SortButtonText,  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=sort_list, #the width of the button, and the function which get called when clicking it
                    bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

MoveUpButton = tk.Button(window,  #the first parameter is the widget
                   text="Move Up",  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=move_up, #the width of the button, and the function which get called when clicking it
                    bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

MoveDownButton = tk.Button(window,  #the first parameter is the widget
                   text="Move Down",  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=move_down, #the width of the button, and the function which get called when clicking it
                    bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

SearchButton = tk.Button(window,  #the first parameter is the widget
                   text="Search File",  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=searchSongInPlaylist, #the width of the button, and the function which get called when clicking it
                    bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

SleepButton = tk.Button(window,  #the first parameter is the widget
                   text="Sleep \ Wake",  # the text on the button
                    height=allButtonsHeight,
                   width=allButtonsWidth, command=showSleepingTool, #the width of the button, and the function which get called when clicking it
                    bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                   font=allButtonsFont) #this is the font, size and type

packPositionButton()

labelBackground = StringVar()
labelBackground.set("lightgray")
labelPadX=2
#Building the labels
SongName = StringVar()
SongName.set("Playing: ")

labelPlaying = tk.Label(window, textvariable=SongName, anchor=tk.W, compound=tk.CENTER, padx=labelPadX, bd=3, relief=tk.GROOVE \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())  # creating a label on the window

SongDuration = StringVar()
SongDuration.set("Time Elapsed: ")

labelDuration = tk.Label(window, textvariable=SongDuration, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())  # creating a label on the window

SongSize = StringVar()
SongSize.set("Size: ")

labelSize = tk.Label(window, textvariable=SongSize, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())  # creating a label on the window

textFilesToPlay = StringVar()
textFilesToPlay.set("Files: " + str(len(play_list.validFiles)))
labelFilesToPlay = tk.Label(window, textvariable=textFilesToPlay, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())  # creating a label on the window

textLength = StringVar()
textLength.set("Length: ")
labelLength = tk.Label(window, textvariable=textLength, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())  # creating a label on the window

textGenre = StringVar()
textGenre.set("Genre: ")
labelGenre = tk.Label(window, textvariable=textGenre, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())  # creating a label on the window

textStartTime = StringVar()
textStartTime.set("Start Time: ")
labelStartTime = tk.Label(window, textvariable=textStartTime, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())  # creating a label on the window

textEndTime = StringVar()
textEndTime.set("End Time: ")
labelEndTime = tk.Label(window, textvariable=textEndTime, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())  # creating a label on the window

textTotalPlayTime = StringVar()
textTotalPlayTime.set("PlayTime: ")
labelTotalPlayTime = tk.Label(window, textvariable=textTotalPlayTime, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())  # creating a label on the window

textFallAsleep = StringVar()
textFallAsleep.set("Fall Asleep: Never")
labelFallAsleep = tk.Label(window, textvariable=textFallAsleep, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())  # creating a label on the window						

textWakeUp = StringVar()
textWakeUp.set("Wake Up: Never")
labelWakeUp = tk.Label(window, textvariable=textWakeUp, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())  # creating a label on the window

textFadeIn = StringVar()
textFadeIn.set("FadeIn: ")
labelFadeIn = tk.Label(window, textvariable=textFadeIn, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())  # creating a label on the window

textFadeOut = StringVar()
textFadeOut.set("FadeOut: ")
labelFadeOut = tk.Label(window, textvariable=textFadeOut, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())

textMonoStereoMode = StringVar()
textMonoStereoMode.set("Mode: ")
labelMonoStereoMode = tk.Label(window, textvariable=textMonoStereoMode, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())

textSampleRate = StringVar()
textSampleRate.set("Sample Rate: ")
labelSampleRate = tk.Label(window, textvariable=textSampleRate, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())

textNofPlays = StringVar()
textNofPlays.set("No. of Plays: ")
labelNofPlays = tk.Label(window, textvariable=textNofPlays, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())

textDanthologyMode = StringVar()
textDanthologyMode.set("Danthology Mode: OFF")
labelDanthologyMode = tk.Label(window, textvariable=textDanthologyMode, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())

textArtist = StringVar()
textArtist.set("Artist: ")
labelArtist = tk.Label(window, textvariable=textArtist, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())         

textAlbum = StringVar()
textAlbum.set("Album: ")
labelAlbum = tk.Label(window, textvariable=textAlbum, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())      

textTitle = StringVar()
textTitle.set("Title: ")
labelTitle = tk.Label(window, textvariable=textTitle, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())         

textYear = StringVar()
textYear.set("Year: ")
labelYear = tk.Label(window, textvariable=textYear, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())                           

textSongListenedTime = StringVar()
textSongListenedTime.set("Song Listened Time: ")
labelSongListenedTime = tk.Label(window, textvariable=textSongListenedTime, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())                         

textPlaylistListenedTime = StringVar()
textPlaylistListenedTime.set("Playlist Listened Time: ")
labelPlaylistListenedTime = tk.Label(window, textvariable=textPlaylistListenedTime, compound=tk.CENTER, padx=labelPadX \
                        , fg=SkinColor.get(), font=allButtonsFont, background = labelBackground.get())                         
packPositionLabels()

#Creating a listbox
frame = tk.Frame(window, borderwidth=2, bg=SkinColor.get(), relief = tk.SUNKEN)
scroll = tk.Scrollbar(frame, orient="vertical", width=15)
listbox = tk.Listbox(frame, fg=fontColor.get(), font=allButtonsFont, width=70, bg=SkinColor.get(), height=35, relief=tk.GROOVE,\
                     yscrollcommand=scroll.set, borderwidth=2, selectbackground = fontColor.get(), selectforeground = SkinColor.get())

if play_list.listboxWidth!="Auto":
    listbox["width"] = play_list.listboxWidth

#create the Skin widget:
SkinFrame = tk.Frame(window, borderwidth=1, bg=SkinColor.get(), relief = tk.SUNKEN, width=106, height=50)
labelSkin = tk.Label(SkinFrame, text="Skin: ", compound=tk.CENTER, padx=10 \
                        , fg=fontColor.get(), font=allButtonsFont, background = SkinColor.get(), borderwidth=0, width=allButtonsWidth)
option = Combobox(SkinFrame, textvariable=SkinColor, values = skinOptions[1], font=allButtonsFont, state="readonly")

#Creating Volume:
VolumeScale = tk.Scale(window, from_=0, to=100, orient=tk.HORIZONTAL, fg=fontColor.get(), label="Volume Level:", length=100, sliderlength=10, width=10,
                       highlightbackground=SkinColor.get(), bd=1, relief = tk.SUNKEN, font=allButtonsFont, bg=SkinColor.get())
VolumeScale.set(play_list.VolumeLevel*100)
#Creating style for progressbar
styl = ttk.Style()

#Creating Progress bar
progressBarLength = 470
progress = Progressbar(orient=tk.HORIZONTAL, length=progressBarLength, mode=play_list.ProgressBarType, value=0, maximum = 100, \
                       style="Horizontal.TProgressbar",) #using the same style

#Setting the width of labelPlaying same as progressbar
labelPlaying["wraplength"] = progressBarLength

#Creating RadioButton
songRating = StringVar()
songRating.set("0") # initialize

R1 = tk.Radiobutton(window, text="1", variable=songRating, value=1, width=3, bg=radioButtonsDefaultColor, command=UpdateSongRating, fg = SkinColor.get(), selectcolor="black", font=allButtonsFont, borderwidth=3, relief=tk.GROOVE)
R2 = tk.Radiobutton(window, text="2", variable=songRating, value=2, width=3, bg=radioButtonsDefaultColor, command=UpdateSongRating, fg = SkinColor.get(), selectcolor="black", font=allButtonsFont, borderwidth=3, relief=tk.GROOVE)
R3 = tk.Radiobutton(window, text="3", variable=songRating, value=3, width=3, bg=radioButtonsDefaultColor, command=UpdateSongRating, fg = SkinColor.get(), selectcolor="black", font=allButtonsFont, borderwidth=3, relief=tk.GROOVE)
R4 = tk.Radiobutton(window, text="4", variable=songRating, value=4, width=3, bg=radioButtonsDefaultColor, command=UpdateSongRating, fg = SkinColor.get(), selectcolor="black", font=allButtonsFont, borderwidth=3, relief=tk.GROOVE)
R5 = tk.Radiobutton(window, text="5", variable=songRating, value=5, width=3, bg=radioButtonsDefaultColor, command=UpdateSongRating, fg = SkinColor.get(), selectcolor="black", font=allButtonsFont, borderwidth=3, relief=tk.GROOVE)
labelSongRating = tk.Label(window, text="Song Rating: ", compound=tk.LEFT, padx=10, pady=3, \
                        fg=SkinColor.get(), font=allButtonsFont, background = radioButtonsDefaultColor, borderwidth=3, relief=tk.GROOVE)

packPositionListScrolOptionProgRadio()

scheduler = sched.scheduler(time.time, time.sleep)

#Load backup if possible
if os.path.exists(automaticallyBackupFile):
    loadPlaylistFile(automaticallyBackupFile)

window.mainloop() #loop through the window