import numpy as np
import pandas as pd
import pyttsx3
import speech_recognition as sr
import wikipedia
import webbrowser
import requests
import json
import os
import sys
import platform
import pafy
import subprocess
import re
import pygame
import time
import urllib.request
#from urllib.parse import * ## avoid using (*) ---- use only what is required; else software will slow-down
from bs4 import BeautifulSoup
from random import randint
from datetime import datetime
from glob import glob
from time import sleep
from Levenshtein import ratio
from mutagen.mp3 import MP3
from winsound import Beep

from pdb import set_trace as debug

# Currently Mainly 'voice enabled music streamer'
# TODO: Guide music through voice commands; control device tasks; etc.


utils_dir = assets_dir = datasets_dir = ''
# ----- Access Other Directories on Particular Platform ----- #
if platform.system() == 'Linux':
    utils_dir = os.path.realpath('../Utils') + '/'
    sys.path.insert(0, utils_dir)
    from Music import Music
    assets_dir = os.path.realpath('../assets') + '/'
    sys.path.insert(0, assets_dir)
    datasets_dir = os.path.realpath('../assets/datasets') + '/'
    sys.path.insert(0, datasets_dir)
else:
    root_dir = os.path.realpath('..\\Audio-Made-Easy')
    sys.path.insert(0, root_dir)
    #from Utils.Music import Music
    utils_dir = root_dir + '\\Utils\\'
    assets_dir = root_dir + '\\assets\\'
    datasets_dir = assets_dir + 'datasets\\'

features = utils_dir + 'Features.txt'
brain = datasets_dir + 'brain.csv'

class Media_Player: # Supports only mp3
    def __init__(self, audio_file=''):
        '''
        Play, Pause, Stop, Replay (stop + play), resume

        next, prev -- for playlist playing (for single audio ----- SAY: "That was the last song" <resume_playing>)
        '''
        self.__audio_file = audio_file
        self.__audio = MP3(audio_file)
        self.__audio_sample_rate = self.__audio.info.sample_rate
        self.__audio_channels = self.__audio.info.channels
        self.__audio_length = self.__audio.info.length
        self.__audio_sample_rate = self.__audio.info.sample_rate
        self.__song_name = audio_file.split()[0]

        self.__songtracks = os.listdir()
        self.__playlist = []
        for track in self.__songtracks:
            self.__playlist.append(track)
    
    def play(self):
        if pygame.mixer.get_init():
            pygame.mixer.quit() # quit it, to make sure it is reinitialized
        pygame.mixer.pre_init(frequency=self.__audio_sample_rate, size=-16, channels=self.__audio_channels, buffer=4096)
        pygame.mixer.init()
        pygame.mixer.music.load(self.__audio_file)
        pygame.mixer.music.play()
        print(self.__song_name + " ---- Playing")

    def pause(self):
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
        print("Playback Paused")

    def resume(self):
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.unpause()
        print(self.__song_name + " ---- Resumed")

    def stop(self):
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        print("Stopped")
    
    def replay(self):
        self.stop()
        self.play()
        print(self.__song_name + " ---- Replaying")
    
    def current_time(self):
        timer = 0
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            timer = pygame.mixer.music.get_pos()
            timer = int(timer//1000)
        return timer

    def __music(self):
        while pygame.mixer.music.get_busy():
            timer = pygame.mixer.music.get_pos()
            time.sleep(1)
            control = input()
            pygame.time.Clock().tick(10)
            if control == "pause":
                pygame.mixer.music.pause()
            elif control == "play" :
                pygame.mixer.music.unpause()
            elif control == "time":
                timer = pygame.mixer.music.get_pos()
                timer = timer/1000
                print (str(timer))
            elif int(timer) > 10:
                print ("True")
                pygame.mixer.music.stop()
                break
            else:
                continue

class Youtube_mp3:
    song_created = ''

    def __init__(self):
        '''
        Overview:
            Throw me a song query... I will play it for you!

        Description:
            That also with the help of YouTube. Now guess my library size. LOL!
        '''
        self.lst = []
        self.dict = {}
        self.dict_names = {}
        self.playlist = []
    
    def flush_media_files_created(self):
        if glob('song*') or glob('*mp3') or glob('*webm'):
            self.song_created = ''
            video_in_dir = glob('song.*')
            audio_in_dir = glob('*mp3')
            temp_in_dir = glob('*webm')
            if video_in_dir:
                try:
                    os.remove(video_in_dir[0])
                    self.song_created = ''
                except PermissionError: # say 'STOP' will be implemented after creating 'class Media_Player'
                    print('Silently quiting app!')
                    #print("Please Wait! The song is being played! Let it finish... say 'STOP' or quit external media player (temp) ")
            if audio_in_dir:
                try:
                    os.remove(audio_in_dir[0])
                    self.song_created = ''
                except PermissionError: # say 'STOP' will be implemented after creating 'class Media_Player'
                    print('Silently quiting app!')
                    #print("Please Wait! The song is being played! Let it finish... say 'STOP' or quit external media player (temp) ")
            if temp_in_dir:
                try:
                    os.remove(temp_in_dir[0])
                    self.song_created = ''
                except PermissionError: # say 'STOP' will be implemented after creating 'class Media_Player'
                    print('Silently quiting app!')
                    #print("Please Wait! The song is being played! Let it finish... say 'STOP' or quit external media player (temp) ")

    def url_search(self, search_string, max_search):
        self.dict = {} # Flushing the buffer for new song request
        self.dict_names = {}
        textToSearch = search_string
        query = urllib.parse.quote(textToSearch)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, 'lxml')
        i = 1
        for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
            if len(self.dict) < max_search:
                self.dict[i] = 'https://www.youtube.com' + vid['href']
                i += 1
            else:
                break
        return url

    def get_search_items(self, num):
        ### 'user' found in url; grab onther search result from self.url_search(string_search, num_of_user_found) and replace those in self.dict
        #if self.dict != {}:
        if self.dict:
            i = 1
            try:
                for url in self.dict.values():
                    info = pafy.new(url)
                    #self.dict_names[i] = info.title
                    self.dict_names[i] = (info.title, url)
                    if num == 0:
                        print("{0}. {1}".format(i, info.title))
                    i += 1

            except ValueError:
                pass

            except OSError:
                print('This video is unavailable') # Bheege Hont Tere; Dostana Hindi movie; desi boyz
                # Truncate last key from 'self.dict'
                del self.dict[list(self.dict.keys())[-1]]
                self.get_search_items(num)
            
            return (self.dict_names, self.dict)
        return None

    def play_media(self, num): # Returns 'Media_Player' object with loaded song
        global song_created
        url = self.dict[int(num)]
        video = pafy.new(url)
        video_title = video.title
        video_title = re.sub(r'\W+', '', video_title)
        print(f'video_title: {video_title}\n')
        song_title = video_title + '.mp3'
        bestaudio = video.getbestaudio()
        self.flush_media_files_created()
        song_created = video_title + bestaudio.extension
        print('Loading... Please Wait!')
        sleep(2)
        bestaudio.download(song_created, quiet=True)
        sleep(2)

        # Convert to '.mp3' format using 'ffmpeg'
        command = "ffmpeg -i " + str(song_created) + " -vn -ab 128k -ar 44100 -y " + str(song_title)
        subprocess.call(command, shell=True)

        # os.startfile(song_created) # for playing in device default media-player (VLC for me)

        self.player = Media_Player(audio_file=song_title)
        #self.player = Media_Player(audio_file='assets\\JG.mp3') # used for Cache testing purpose
        return self.player
                
    def download_media(self, num):
        url = self.dict[int(num)]
        info = pafy.new(url)
        audio = info.getbestaudio(preftype="m4a")
        song_name = self.dict_names[int(num)]
        print("Downloading: {0}.".format(self.dict_names[int(num)]))
        print(song_name)
        song_name = input("Filename (Enter if as it is): ")
        file_name = song_name + '.m4a'
        if song_name == '':
            audio.download(remux_audio=True)
        else:
            audio.download(filepath = file_name, remux_audio=True)

    def bulk_download(self, url, num):
        info = pafy.new(url)
        audio = info.getbestaudio(preftype="m4a")
        song_name = self.dict_names[int(num)]
        print("Downloading: {0}.".format(self.dict_names[int(num)]))
        print(song_name)
        song_name = input("Filename (Enter if as it is): ")
        file_name = song_name + '.m4a'
        if song_name == '':
            audio.download(remux_audio=True)
        else:
            audio.download(filepath = file_name, remux_audio=True)

    def add_playlist(self, search_query):
        url = self.url_search(search_query, max_search=1)
        self.playlist.append(url)

class _DataBase:
    SYNONYMS = {
        'END' : ['end', 'close', 'finish', 'stop', 'terminate', 'windup']
    }

class Voice_Assistant: ## NOTE: Play a beep when sub-queries are searched
    '''
    Overview:
        Perform any task just with your voice.
    
    Description:
        This Voice Assistant has a lots of Abilities (mentioned inside sub-class 'Abilities'). Basically when we ask 'AI' engine for any task. Then it asks its own 'Abilities' to perform some task based on input query. Then it takes the output and return it to us.
    '''
    search_terms = ['wikipedia', 'open youtube', 'open google', 'open stackoverflow', 'play song', 'time', 'open code', 'quit']

    def __init__(self):
        self.engine = pyttsx3.init('sapi5')
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[0].id)
        self.VA_NAME = 'Google'
        self.ytb = Youtube_mp3()
        self._DataBase = _DataBase()
        self._brain = brain
        self._song_name = ''

    def _speak(self, audio):
        self.engine.say(audio)
        self.engine.runAndWait()

    def __wish_me(self):
        hour = int(datetime.now().hour)
        if 0 <= hour < 12:
            self._speak('Good Morning!')
        elif 12 <= hour < 18:
            self._speak('Good Afternoon!')
        else:
            self._speak('Good Evening!')
        
        self._speak(f'Hello Sir or Madam. I am {self.VA_NAME} - Your personal voice assistant!')
        self._speak('How may I help You?')
    
    def _take_command(self): ## NOTE: Execution Stopped (hanged)
        '''
        NOTE: <To Solve HANG issue>
        Create 2 threads: for handling the mic voice commands
        1. if retries exceed a THRESHOLD_VALUE=5 ======= kill it
        2. it waits for thread 1 to be killed ======= then it will start
        <Cycle interchangely REPEATS>
        '''
        ## NOTE: Create 2 threads (one for handling the mic voice commands) && (amother will wait for its expire)
        r = sr.Recognizer()

        with sr.Microphone() as source:
            # r.adjust_for_ambient_noise(source) # Ambient Noise Cancellation; use only when in a noisy background
            '''
            Intended to calibrate the energy threshold with the ambient energy level. Should be used on periods of audio without speech - will stop early if any speech is detected.
            '''
            print('Listening...') # execute in seperate threads; if one gets hanged (overloaded) kill that; start new
            r.pause_threshold = 1
            audio = r.listen(source)
        
        try:
            print('Recognizing...')
            query = r.recognize_google(audio, language='en-in')
            print(f'User Said: {query}\n')
        except Exception:
            print('Say that again please...')
            return 'None'
        return query
    
    def _substr_in_list_of_strs(self, lst, substr):
        '''
        Objective: Check if a substring is present in a list of strings

        Source: https://www.geeksforgeeks.org/python-finding-strings-with-given-substring-in-list/
        '''
        res_lst_of_strs_with_substr = list(filter(lambda x: substr in x, lst))
        return (bool(res_lst_of_strs_with_substr), res_lst_of_strs_with_substr)
    
    def _stream_online(self, song_name, number=0): # number = song_number to play in the list of search results
        '''
        It calls 'play_media()' of 'Youtube_mp3';; which returns 'Media_Player' object with loaded song.
        Then, 'Abilities' will control the media-player options with voice
        '''
        max_search = 5
        main_list = False
        self._song_name = song_name

        def try_new_song(new=True):
            if new:
                self._speak('What song to search for?')
                while True:
                    search_term = self._take_command()
                    if search_term != 'None':
                        break
            else:
                search_term = song_name
            self._stream_online(search_term)
            
        if number == 0: # direct playing song
            ### Add support for 'search more'; (increase max_search value by let's say=5; show result from 6-10) [say 'refresh', 'more']
            self.ytb.url_search(song_name, max_search)
            search_titles = self.ytb.get_search_items(number) ## NOTE: Don't display the list again when 'retry_song_search_queries[]' called
            skip_song_search_queries = ['skip', 'abort']
            retry_song_search_queries = ['retry', 'search again', 'other', 'new', 'different', 'none of these', 'not these', 'not this'] ## NOTE: not able to handle wrong entry correctly; re-executing searched result
            if search_titles:
                if search_titles[1]:
                    self._speak('Which Number Song? (SAY for example, Number 1)')
                    while True:
                        song_number = self._take_command()
                        if self._substr_in_list_of_strs(skip_song_search_queries, song_number)[0]: # skip song search; go to main list
                            main_list = True
                            break
                        elif self._substr_in_list_of_strs(retry_song_search_queries, song_number)[0]:
                            main_list = False # try again for another song; not main list
                            break
                        elif song_number != 'None' and \
                            not self._substr_in_list_of_strs(skip_song_search_queries, song_number)[0] and \
                            not self._substr_in_list_of_strs(retry_song_search_queries, song_number)[0]:
                            if 'number' not in song_number:
                                self._speak('Was expecting a number! Retry...')
                                try_new_song(new=False)
                            break
                    if not main_list and not self._substr_in_list_of_strs(retry_song_search_queries, song_number)[0]:
                        if 'number' in song_number and 'user' in search_titles[0][int(song_number.strip().split()[-1])][0]:
                            self._speak('This is a channel name, not a song! Try again...')
                            ### implement this issue in 'Youtube_mp3.get_search_items()'
                        elif 'number' not in song_number or 'number' in song_number and len(song_number.strip().split()) == 1:
                            self._speak('Was expecting a number! Retry...')
                            try_new_song(new=False)
                        elif 'number' in song_number and song_number.strip().split()[-1].isdigit():
                            print(f'Song Title: {search_titles[0][int(song_number.strip().split()[-1])][0]}')
                            self.player = self.ytb.play_media(song_number.strip().split()[-1])
                            main_list = True # So that 'try_new_song()' will not execute after song successfully start playing
                        else: ## NOTE: 'number <non-digit>' is not handled properly
                            print('Say that again please...')
                            try_new_song(new=False)
                else: # for No Search results
                    main_list = False
                    self._speak(f'No song found with {song_name}! Try Again...') # try again for another song; not main list
            else:
                main_list = False
                self._speak(f'No song found with {song_name}! Try Again...') # try again for another song; not main list
            
            if not main_list:
                try_new_song()
        
        else: # play song from last 'webpage' valid song search
            ## NOTE: First search the song_name along with ('lyric', 'full', 'audio', 'official', '|'); if no result => display the list (allow more/refresh_list...)
            song_search_query = [song_name + ' ' + key for key in ('lyric', 'full', 'audio', 'official', '|')]
            print(f'song_search_query: {song_search_query}')
            results_found = False
            for query in song_search_query: # search for 'song_name' + ==> ('lyric', 'full', 'audio', 'official', '|')
                self.ytb.url_search(query, max_search)
                search_titles = self.ytb.get_search_items(number) # Return the result list for each 'query';; don't print the list (since, number != 0)
                if search_titles: # if atleast 1 song found
                    for num in search_titles[0].keys(): # traverse the list for the search query
                        if query.split()[-1] in search_titles[0][num][0]: # if any('lyric', 'full', 'audio', 'official', '|') in search_titles[0][num][0] <-- song_title
                            results_found = True
                            number = num
                            break
                if results_found:
                    break
            if results_found:
                self.player = self.ytb.play_media(number)
            else:
                self.ytb.url_search(song_name, max_search)
                search_titles = self.ytb.get_search_items(number)
                if search_titles[1]:
                    self._speak('Which Number Song? (SAY for example, Number 1)')
                    while True:
                        song_number = self._take_command()
                        if self._substr_in_list_of_strs(skip_song_search_queries, song_number)[0]: # skip song search; go to main list
                            main_list = True
                            break
                        elif self._substr_in_list_of_strs(retry_song_search_queries, song_number)[0]:
                            main_list = False # try again for another song; not main list
                            break
                        elif song_number != 'None' and \
                            not self._substr_in_list_of_strs(skip_song_search_queries, song_number)[0] and \
                            not self._substr_in_list_of_strs(retry_song_search_queries, song_number)[0]:
                            if 'number' not in song_number:
                                self._speak('Was expecting a number! Retry...')
                                try_new_song(new=False)
                            break
                    if not main_list and not self._substr_in_list_of_strs(retry_song_search_queries, song_number)[0]:
                        if 'number' in song_number and 'user' in search_titles[0][int(song_number.strip().split()[-1])][0]: # chk if search result is a valid song or not
                            self._speak('This is a channel name, not a song! Try again...')
                            ### implement this issue in 'Youtube_mp3.get_search_items()'
                        elif 'number' not in song_number or 'number' in song_number and len(song_number.strip().split()) == 1:
                            self._speak('Was expecting a number! Retry...')
                            try_new_song(new=False)
                        elif 'number' in song_number and song_number.strip().split()[-1].isdigit():
                            print(f'Song Title: {search_titles[0][int(song_number.strip().split()[-1])][0]}')
                            self.player = self.ytb.play_media(song_number.strip().split()[-1])
                            main_list = True # So that 'try_new_song()' will not execute after song successfully start playing
                        else: ## NOTE: 'number <non-digit>' is not handled properly
                            print('Say that again please...')
                            try_new_song(new=False)
                else: # for No Search results
                    main_list = False
                    self._speak(f'No song found with {song_name}! Try Again...') # try again for another song; not main list
                
                if not main_list:
                    try_new_song()
        
        return self.player

    class Abilities: ## NOTE: Handle any type of 'can you <>';; direct perform action rather than telling what to ask
        '''
        Overview:
            The 'Abilities' that I have to perform various tasks.

        Myself:
            My 'Abilities' are very limited.

        NOTE: A task for you... "Please train me with new 'Abilities' so that I can stand in the real world"
        '''
        __my_abilities_with_keywords = {
            'Search for information on wikipedia': ['info', 'information', 'wiki', 'wikipedia'],
            'Open Youtube and search for you': ['youtube', 'searching youtube', 'youtube search', 'open youtube', 'youtube opening', 'viewing youtube', 'youtube viewing', 'watching youtube', 'youtube watching'],
            'Open Google and search for you': ['google'],
            'Open stackoverflow and search for you': ['stackoverflow'],
            'Stream Song from youtube directly': ['Stream', 'Song'],
            'Tell you the current time': ['time', 'tell'],
            'Open VS Code for you': ['VS', 'Code'],
            'have general conversation with you': ['conversation', 'talk'],
            'saying Goodbye': ['Goodbye']
        } # {'Ability to speak out' : 'keyword/s'}
        __my_abilities_with_index = list(zip(list(range(0, len(__my_abilities_with_keywords))), __my_abilities_with_keywords.keys())) # zip ('index numbers', my_abilities)
        __queries_made = []
        __unknown_abilities = []

        def __init__(self):
            self.__va = Voice_Assistant()
            self.__random_2_numbers = list(np.random.permutation(np.arange(0, len(self.__my_abilities_with_keywords) - 1))[:2])
            self.__retries = 1

        def what_can_you_do(self, query): # Return 2 random abilities from 'self.my_abilities'[0:-1] and 'Bid Goodbye'
            if 'how can you help in ' in query or 'how can you help me ' in query:
                self.how_can_you(query)
            else:
                first = self.__my_abilities_with_index[self.__random_2_numbers[0]][1]
                second = self.__my_abilities_with_index[self.__random_2_numbers[1]][1]
                last = self.__my_abilities_with_index[-1][1]
                i_can_do = 'Out of many; I can ' + first + '; or even ' + second + ' for you. Or you can quit this application by ' + last
                self.__va._speak(i_can_do)
        
        def how_can_you(self, query): # Handles any type of 'How can you <task>'
            what_to_ask = ''
            print(f'query: {query}')
            if 'how can you help in' in query or 'how can you help me' in query:
                new_query = query.split()[5:]
            else:
                new_query = query.split()[3:]
            c = 0
            for v in self.__my_abilities_with_keywords.values():
                common_keyword = list(set(new_query) & set(v))
                if common_keyword:
                    if self.__va._substr_in_list_of_strs(v, common_keyword[0])[0]:
                        what_to_ask = self.__va.search_terms[c] #list(self.my_abilities_with_keywords.keys())[list(self.my_abilities_with_keywords.values()).index(common_keyword[0])]
                    break
                else:
                    c += 1
            
            print(f'what to ask: {what_to_ask}')
            if what_to_ask:
                self.__va._speak('Just say; ' + what_to_ask)
            else:
                self.__va._speak("I have never told that I can do this!")
                self.__unknown_abilities.append(' '.join(query.split()[3:]))
                self.__va._speak("Anyway I will learn this in future")

        def wikipedia(self, query): ## NOTE: Incomplete
            self.__queries_made.append(query)
            self.__va._speak('Searching Wikipedia...')
            query = query.replace('wikipedia', '') ## NOTE: If 'query' is only 'wikipedia' then this line will throw 'wikipedia.exceptions.WikipediaException'; deal with it
            try:
                results = wikipedia.summary(query, sentences=2)
                self.__va._speak('According to Wikipedia')
                print(results)
                self.__va._speak(results)
            except wikipedia.exceptions.PageError:
                self.__va._speak('Sorry! Page Not Found!')
            except wikipedia.exceptions.DisambiguationError as e: # "Bengali Movie Wikipedia"; "SK Wikipedia"
                queries = e.options
                sub_queries = {}
                self.__va._speak('Following are the options found, matching your query')
                for num, option in enumerate(queries):
                    print('{0}. {1}'.format(num + 1, option))
                    sub_queries[num] = option
                self.__va._speak('Which Number Page? (SAY for example, Number 1)') ## NOTE: Incomplete...
                while True:
                    page_num = self.__va._take_command()
                    if page_num != 'None':
                        break
                new_query = sub_queries[int(page_num.strip().split()[-1]) - 1]
            except wikipedia.exceptions.WikipediaException: ## NOTE: Incomplete...
                print('Say that again please...')
                self.__va._speak('search wikipedia')
                while True:
                    new_query = self.__va._take_command()
                    if new_query != 'None':
                        break
                results = wikipedia.summary(new_query, sentences=2)
                self.__va._speak('According to Wikipedia')
                print(results)
                self.__va._speak(results)

        def youtube(self, query):
            self.__queries_made.append(query)
            self.__va._speak('What to search for?')
            while True:
                search_term = self.__va._take_command()
                if search_term != 'None':
                    break
            query = urllib.parse.quote(search_term)
            url = "https://www.youtube.com/results?search_query=" + query
            webbrowser.open_new_tab(url)

        def google(self, query):
            self.__queries_made.append(query)
            self.__va._speak('What to search for?')
            while True:
                search_term = self.__va._take_command()
                if search_term != 'None':
                    break
            query = urllib.parse.quote(search_term)
            url = "https://www.google.com/search?q=" + query
            webbrowser.open_new_tab(url)

        def play_song_from_last_search(self, website): ## NOTE: Incomplete
            if website == 'wikipedia':
                search_sub = self.__va._substr_in_list_of_strs(self.__queries_made, 'wikipedia')
                if search_sub[0]: # if wikipedia searched
                    if len(search_sub[1]) >= 1:
                        last_searched_query = search_sub[1][-1]
                        song_name = last_searched_query.replace('wikipedia', '').strip()
                        wiki_res = wikipedia.summary(song_name, sentences=10) # check id query is a valid song or not
                        if 'music' in wiki_res or 'song' in wiki_res or 'film' in wiki_res:
                            self.__va._stream_online(song_name, 1)
                        else:
                            self.__va._speak('No song searched in wikipedia!')
                    else:
                        query = search_sub[1][-1]
                        song_name = query.replace('wikipedia', '').strip()
                        wiki_res = wikipedia.summary(song_name, sentences=10) # check id query is a valid song or not
                        if 'music' in wiki_res or 'song' in wiki_res or 'film' in wiki_res:
                            self.__va._stream_online(song_name, 1) ## Will not work now;; See LINE: 306
                        else:
                            self.__va._speak('No song searched in wikipedia!')
                    return True
            
            elif website == 'youtube':
                pass # self.__va._stream_online();; first result
                return True

            elif website == 'google':
                pass # self.__va._stream_online();; first result with a song name
                return True
            
            else:
                self.__va._speak('No song found in search queries! Instead ask to play song...')
                return False

        def play_song(self, query):
            self.__va._speak('What to search for?')
            while True:
                search_term = self.__va._take_command()
                if search_term != 'None':
                    break
            
            music_player = self.__va._stream_online(search_term)
            if music_player:
                music_player.play()

                while True:
                    call_VA = self.__va._take_command()
                    if self.__va.VA_NAME in call_VA:
                        music_player.pause()
                        control = self.__va._take_command()
                        if 'play' in control:  # start from beginning
                            music_player.play()
                        elif 'pause' in control: # pause
                            music_player.pause()
                        elif 'replay' in control: # start from beginning
                            ## NOTE: Make this functionality so that the song replays after it finishes
                            music_player.replay()
                        elif 'resume' in control: # start after pause
                            music_player.resume()
                        elif 'end' in control or any(self.__va._DataBase.SYNONYMS['END']) in control: # stop the song && closes the 'Media_Player' instance
                            music_player.stop()
                            print(f'Current Position: {music_player.current_time()}\n')
                            self.__va.ytb.flush_media_files_created()
                            break
                        else:
                            music_player.resume()
            else:
                for _ in range(self.__retries):
                    self.__va._speak(f'Sorry! unable to find {self.__va._song_name}...')
                    self.__va._speak('Trying again! Plaise Wait...')
                    self.__va._stream_online(self.__va._song_name)

        def stackoverflow(self, query):
            self.__va._speak('What to search for?')
            while True:
                search_term = self.__va._take_command()
                if search_term != 'None':
                    break
            query = urllib.parse.quote(search_term)
            url = "https://stackoverflow.com/search?q=" + query
            webbrowser.open_new_tab(url)

        def current_time(self, query):
            str_time = datetime.now().strftime("%H:%M:%S")
            self.__va._speak(f'Sir or Madam, The Time is {str_time}')

        def open_app(self, query):
            code_path = 'C:\\Users\\dgkii\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe'
            os.startfile(code_path)

        def quit_VA(self, query):
            hour = int(datetime.now().hour)
            if 0 <= hour <=18:
                self.__va._speak('Good Bye Sir or Madam, Thanks for your time! Have a nice day')
            else:
                if 'good night' in query:
                    self.__va._speak('Good Bye Sir or Madam, Thanks for your time! Good Night!')
                else:
                    self.__va._speak('Good Bye Sir or Madam, Thanks for your time!')
            self.__va.ytb.flush_media_files_created()

        def conversation(self): # This the brain of my VA. Read 'datasets/brain.csv'; create and train model to have conversation with user
            brain = pd.read_csv(self.__va._brain)
            self.stop = False

            ## Approximating QA system
            # Approximate string matching
            def getApproximateAnswer(q):
                max_score = 0
                answer = ""
                prediction = ""
                for _, row in brain.iterrows():
                    score = ratio(row["Question"], q)
                    if score >= 0.9: # I'm sure, stop here
                        return row["Answer"], score, row["Question"]
                    elif score > max_score: # I'm unsure, continue
                        max_score = score
                        answer = row["Answer"]
                        prediction = row["Question"]

                if max_score > 0.8:
                    return answer, max_score, prediction
                return "Sorry, I didn't get you.", max_score, prediction

            while not self.stop:
                def ask():
                    print('Waiting for you!')
                    while True:
                        question = self.__va._take_command()
                        if question != 'None':
                            break
                    reply(question)

                def reply(question):
                    answer, _, _ = getApproximateAnswer(question)
                    self.__va._speak(answer)

                    if 'bye' in answer:
                        if 'as you wish' in answer:
                            self.stop = True
                        else:
                            self.quit_VA(question)
                            self.stop = True
                
                ask()
            
            if self.stop:
                return False
            return True

        def read_out_news(self, query): # query: NEWS Category (region / topic / etc...)
            url = 'https://opensourcepyapi.herokuapp.com:443/news'
            r = requests.get(url)
            data = r.json()
            y = json.loads(data)
            sleep(1)
            c = 1

            NEWS_Headlines = list(y['Title'].values())
            random_10_numbers = list(np.random.permutation(np.arange(0, len(NEWS_Headlines) - 1))[:10])
            random_10_news_headlines = [NEWS_Headlines[i] for i in random_10_numbers]

            self.__va._speak('TOP 10 Headlines Today...')
            for news in random_10_news_headlines:
                print(f'Number {c}: {news}')
                self.__va._speak(f'Number {c}')
                self.__va._speak(news)
                Beep(1047, 300)
                sleep(1)
                c += 1
                if c > 10:
                    break
            self.__va._speak('Thank You!')

    def start_AI_engine(self): ### TODO: If valid query => calls respective functions in 'Abilities'; Else => calls 'Abilities.what_can_you_do()'
        self.__wish_me()
        self.__if_any_query_made = False
        self.__time_out_between_failed_queries = 1 # seconds
        self.__last_webpage_visited = '' # store the """webpage name from each""" queries_made
        self.__available_webpages = {
            'w' : 'wikipedia',
            'y' : 'youtube',
            'g' : 'google'}

        while True:
            self.__abilities = self.Abilities()
            query = self._take_command().lower()
            print(f'query: {query}')
            # Logic for executing tasks based on query
            ### if self._substr_in_list_of_strs('can do perform'.split(), query)[0]:
            if 'what can you do' in query or 'how can you help' in query:
                self.__if_any_query_made = False
                self.__abilities.what_can_you_do(query)
            
            elif 'how can you' in query:
                self.__if_any_query_made = True
                self.__abilities.how_can_you(query)
            
            elif 'wikipedia' in query:
                self.__if_any_query_made = True
                self.__last_webpage_visited = self.__available_webpages['w']
                self.__abilities.wikipedia(query)

            elif 'open youtube' in query:
                self.__if_any_query_made = True
                self.__last_webpage_visited = self.__available_webpages['w']
                self.__abilities.youtube(query)

            elif 'open google' in query:
                self.__if_any_query_made = True
                self.__last_webpage_visited = self.__available_webpages['w']
                self.__abilities.google(query)
            
            elif 'play the song' in query or 'play it' in query or 'play this song' in query or 'hear' in query or 'listen' in query:
                self.__if_any_query_made = True
                if 'wiki' in self.__last_webpage_visited:
                    if not self.__abilities.play_song_from_last_search(website=self.__available_webpages['w']):
                        self.__if_any_query_made = False
                elif 'youtube' in self.__last_webpage_visited:
                    if not self.__abilities.play_song_from_last_search(website=self.__available_webpages['y']):
                        self.__if_any_query_made = False
                elif 'google' in self.__last_webpage_visited:
                    if not self.__abilities.play_song_from_last_search(website=self.__available_webpages['g']):
                        self.__if_any_query_made = False

            elif 'play song' in query or 'play music' in query or 'play a song' in query:
                self.__if_any_query_made = True
                self.__abilities.play_song(query)

            elif 'open stackoverflow' in query:
                self.__if_any_query_made = True
                self.__abilities.stackoverflow(query)

            elif 'time' in query:
                self.__if_any_query_made = True
                self.__abilities.current_time(query)

            elif 'open vs code' in query: ## NOTE: don't use absolute path; instead search for its executable (.exe) file and then execute
                self.__if_any_query_made = True
                self.__abilities.open_app(query)

            elif 'bye' in query or 'quit' in query or 'stop' in query or 'exit' in query:
                self.__if_any_query_made = True
                self.__abilities.quit_VA(query)
                return False

            elif 'conversation' in query or 'talk' in query:
                self.__if_any_query_made = True
                self._speak('Sure Sir!')
                return(self.__abilities.conversation())

            elif query == 'none' and not self.__if_any_query_made: # Stop executing when not asked anything
                self.__abilities.what_can_you_do(query)
                sleep(self.__time_out_between_failed_queries)

            elif 'news' in query:
                self.__if_any_query_made = True
                self.__abilities.read_out_news(query)

        return True
