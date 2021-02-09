import numpy as np
import pandas as pd
import pyttsx3
import playsound
import speech_recognition as sr
from gtts import gTTS
import wikipedia
import webbrowser
import requests
import json
import string
import os
import sys
import shutil
import platform
import subprocess
import re
import pygame
import time
import urllib.request as request
from urllib.request import urlopen
from urllib.parse import quote
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from random import randint
from datetime import datetime
from glob import glob
from time import sleep
from mutagen.mp3 import MP3
from winsound import Beep
from Levenshtein import ratio
from difflib import SequenceMatcher
from youtube_search import YoutubeSearch
# from pytube import YouTube

from pdb import set_trace as debug

utils_dir = assets_dir = datasets_dir = cache_dir = tmp_dir = ''
# ----- Access Other Directories on Particular Platform ----- #
if platform.system() == 'Linux':
    utils_dir = os.path.realpath('../Utils') + os.sep
    sys.path.insert(0, utils_dir)
    from Stream import Gaana

    assets_dir = os.path.realpath('../assets') + os.sep
    sys.path.insert(0, assets_dir)
    datasets_dir = os.path.realpath('../assets/datasets') + os.sep
    sys.path.insert(0, datasets_dir)
    cache_dir = os.path.realpath('../assets/cache') + os.sep
    sys.path.insert(0, cache_dir)
    tmp_dir = os.path.realpath('../assets/cache/tmp_dir') + os.sep
    sys.path.insert(0, tmp_dir)
elif platform.system() == 'Windows':
    root_dir = os.path.realpath('')
    if root_dir.split('\\')[-1].strip() == '' and root_dir.split('\\')[-2].strip() != 'Audio-Made-Easy':
        root_dir = '\\'.join(root_dir.split('\\')[:-1])
    elif root_dir.split('\\')[-1].strip() != 'Audio-Made-Easy':
        root_dir = '\\'.join(root_dir.split('\\')[:-1])
    sys.path.insert(0, root_dir)
    from Utils.Stream import Gaana

    utils_dir = root_dir + os.sep + 'Utils' + os.sep
    assets_dir = root_dir + os.sep + 'assets' + os.sep
    datasets_dir = assets_dir + 'datasets' + os.sep
    cache_dir = assets_dir + 'cache' + os.sep
    tmp_dir = cache_dir + 'tmp_dir' + os.sep

features = utils_dir + 'Features.txt'
brain = datasets_dir + 'brain.csv'
jokes = datasets_dir + 'shortjokes.csv'
songs_mapping_file = cache_dir + 'song_map.json'
songs_mapping = dict()


class _Song_Search_and_Stream:  # Implemented in 'Stream.py'
    '''
    Using bs4: (Web scraping)

    >> For example <<
    ---SEARCHING---
    1. query: 'mithe alo'
    2. go to https://www.google.com/search?q=mithe+alo
    3. grep for 'Movie / Album' : <Cockpit>
    4. open the link to get its information; lets say 'wikipedia'
    5. grep for 'mithe alo' in the page using 'wikipedia' API -OR- there itself (will help to get the length of this song)
    6. get the length from there

    ---DOWNLOADING---
    1. 
    '''
    pass


class _Media_Player:  # Supports only mp3
    '''
    TODO:
        1. Cross playing multiple songs in playlist (total time of prev song -5 before end FADE OUT; total time of next song -5 before start FADE IN)
        2. Show live timer
        3. seek bar
        4. Stop playing music / in Music player control mode after song ends
    '''
    REPLAY = False

    def __init__(self,
                 audio_file=assets_dir + 'welcome.mp3'):  # If nothing is found; for the time being; just play the initialised value
        '''
        Play, Pause, Stop, Resume, Restart(Stop + Play), Replay <A MODE to restart the song once it finishes>

        forward (+10 seconds), backward (-10 seconds) ---- 'pygame.mixer.music.get_pos' && 'pygame.mixer.music.set_pos'

        volume-up (), volume-down () ---- 'pygame.mixer.music.get_volume()' && 'pygame.mixer.music.set_volume()'

        next, prev -- for playlist playing (for single audio ---- SAY: "That was the last song" <resume_playing>)
        '''
        self.__audio_file = audio_file
        self.__audio = MP3(self.__audio_file)
        self.__audio_sample_rate = self.__audio.info.sample_rate
        self.__audio_channels = self.__audio.info.channels
        self.__audio_length = self.__audio.info.length
        self.__song_name = audio_file.split('\\')[-1]
        self.__volume = 0.5
        self.__songtracks = os.listdir()
        self.__playlist = []
        for track in self.__songtracks:
            self.__playlist.append(track)

    def play(self):
        if pygame.mixer.get_init():
            pygame.mixer.quit()  # quit it, to make sure it is reinitialized
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
            # pygame.mixer.music.fadeout(5)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        print("Stopped")

    def replay(self):
        self.REPLAY = not self.REPLAY
        if self.REPLAY:
            print(f'{self.__audio_file} ---- is set to REPLAY')
        else:
            print(f'{self.__audio_file} ---- is set NOT to REPLAY')
        return self.REPLAY

    def restart(self):
        self.stop()
        self.play()
        print(self.__song_name + " ---- Restarting")

    def volume(self, mode):
        if mode == 'up':
            self.__volume += 0.1
        elif mode == 'down':
            self.__volume -= 0.1
        elif mode == 'max':
            self.__volume = 1.0
        elif mode == 'min':
            self.__volume = 0.1
        elif mode == 'mute':
            self.__volume = 0.0
        pygame.mixer.music.set_volume(self.__volume)

    def current_time(self):
        timer = 0
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            timer = pygame.mixer.music.get_pos()
            timer = int(timer // 1000)
        return timer

    def __un_used_functions(self):
        pygame.mixer.music.rewind()  # restart music
        pygame.mixer.music.queue  # queue a sound file to follow the current


class _Youtube_mp3:  # Download songs from youtube and create a mp3 file of that
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
        try:
            os.mkdir(cache_dir)
            print('Cache folder created')
        except FileExistsError:
            print('Cache folder already present')
        try:
            os.mkdir(tmp_dir)
            print('tmp folder created')
        except FileExistsError:
            print('tmp folder already present')
        try:
            for f in glob(assets_dir + '*.exe'):
                print(f'Copying "{f}" to {tmp_dir}')
                shutil.copy(f, tmp_dir)
        except Exception:
            print(f'EXE already copied to {tmp_dir}')

    def url_search(self, search_string, max_search):  # search youtube and returns list of 5 links
        dict = {}
        results = YoutubeSearch(search_string + ' full audio lyrics', max_results=max_search).to_dict()
        for i in range(len(results)):
            dict[i] = 'https://www.youtube.com' + results[i]['url_suffix']
        return dict

    def clean_file_name(self, name):  # TODO: match the song search name from the downloaded name ; pass song search term for matching
        name = name.title()
        name = name.replace(' ', '-')
        name = name.replace('_', '-')
        name = name.replace('(', '-')
        name = name.replace('\'', '-')
        name = name.replace('\"', '-')
        name = name.split('--')[0] + '.' + name.split('.')[-1]
        if name[-1] == '-':
            name = name[:-1]
        if name[0] == '-':
            name = name[1:]
        ## ---- Unable to handle non english characters ---- ## (Search for song 'Sudhu Tui from Bengali movie Villain')
        # getVals = list([val for val in name if val.isalpha() or val.isnumeric() or val=='-'])
        '''pattern = re.compile("[A-Za-z0-9 -]+")
        name = pattern.fullmatch(name)'''
        # name = "".join(getVals)
        if len(name.split('-')) >= 3:
            if name.endswith(name.split('.')[-1]):
                ext = name.split('.')[-1]
                name = name.split('.')[0]
                name = '-'.join(name.split('-')[:3]) + '.' + ext
            else:
                name = '-'.join(name.split('-')[:3]) + '.mp3'
        else:
            if name.endswith(name.split('.')[-1]):
                ext = name.split('.')[-1]
                name = name.split('.')[0] + '.' + ext
            else:
                name = name.split('.')[0] + '.mp3'

        return name

    def adjust_file_name(self, text):
        text = ''.join([word for word in text if word not in string.punctuation])
        text = text.lower()
        # text = ' '.join([word for word in text.split('-') if word not in stopwords])
        text = text.replace('oo', 'u')
        text = text.replace('nn', 'n')
        text = text.replace('aa', 'a')
        return text

    def test_url(self, song_name1, url):  # (in folder 'assets\cache')
        # TODO:
        #  1. While storing in cache maintain dictionary to map search term with the file name stored ; eg: "Back-In-Black" stored as "Ac-Dc.mp3"
        #  2. Restrict Cache storage total size ; replace the oldest (first) saved file with the latest search if cache full ; FIFO (queue)
        global songs_mapping
        os.chdir(tmp_dir)
        try:
            # command = 'youtube-dl -f bestaudio ' + url + ' --exec "ffmpeg -i {}  -codec:a libmp3lame -qscale:a 0 {}.mp3 && del {} " '
            # command = ['youtube-dl','-cit','--skip-unavailable-fragments','--embed-thumbnail','--no-warnings','--no-playlist','--extract-audio','--audio-quality', '0','--audio-format', 'mp3', url]
            # print(f'Download Command: {command}')
            # subprocess.call(command)
            subprocess.call(f'python -m youtube_dl --restrict-filenames --ignore-errors -x --audio-format mp3 {url}')
            sleep(2)
            if glob('*.mp3') or glob('*.webm') or glob('*.m4a'):  # song found
                new_name = song_name = ''
                print(f"media files:\n{glob('*.*')}")
                if glob('*.webm'):
                    song_name = glob('*.webm')[0]
                    print(
                        f"song_name webm: {song_name}\ncleaned_song_name webm: {self.clean_file_name(song_name)}")# + '.' + song_name.split('.')[-1]}")
                    os.rename(song_name, self.clean_file_name(song_name))# + '.' + song_name.split('.')[-1])
                    song_name = glob('*.webm')[0]
                    new_name = song_name.split('.')[0] + '.mp3'
                    command = f"ffmpeg -i {song_name} -vn -ar 44100 -ac 2 -b:a 192k -y {new_name}"
                    subprocess.call(command)
                    print(f'\n\n\nNAME of FILE to PLAY: {new_name}\n\n')
                elif glob('*.m4a'):
                    song_name = glob('*.m4a')[0]
                    print(
                        f"song_name m4a: {song_name}\ncleaned_song_name m4a: {self.clean_file_name(song_name)}")# + '.' + song_name.split('.')[-1]}")
                    os.rename(song_name, self.clean_file_name(song_name))# + '.' + song_name.split('.')[-1])
                    song_name = glob('*.m4a')[0]
                    new_name = song_name.split('.')[0] + '.mp3'
                    command = f'ffmpeg -i {song_name} -codec:v copy -codec:a libmp3lame -q:a 2 -y {new_name}'
                    subprocess.call(command)
                    print(f'\n\n\nNAME of FILE to PLAY: {new_name}\n\n')
                elif glob('*.mp3'):
                    song_name = glob('*.mp3')[0]
                    print(
                        f"song_name mp3: {song_name}\ncleaned_song_name mp3: {self.clean_file_name(song_name)}")# + '.' + song_name.split('.')[-1]}")
                    os.rename(song_name, self.clean_file_name(song_name))# + '.' + song_name.split('.')[-1])
                    new_name = glob('*.mp3')[0]
                    shutil.copy(new_name, cache_dir)
                    os.chdir(cache_dir)
                    print(f'\n\n\nNAME of FILE to PLAY: {new_name}\n\n')
                print(f'Song name just before copying: {new_name}')
                # shutil.copy(new_name.lower(), cache_dir)
                print(f'Song name just after copying: {new_name}')
                songs_mapping[song_name1] = new_name
                with open(songs_mapping_file, 'w') as f:
                    json.dump(songs_mapping, f)
                os.chdir(tmp_dir)
                # new_name = glob('*.mp3')[0]
                print(f'Song name just after copying re-created: {new_name}')
                return new_name
            else:
                return None
        except Exception:  # (HTTPError) # url is not a song
            return None

    def play_media(self,
                   song_name):  # Play media based on url; since .mp3 will already be downloaded in 'test_url()'; no need to download it again; ---- Just Returns '_Media_Player' object with loaded song----
        os.chdir(cache_dir)
        self.player = _Media_Player(audio_file=cache_dir + song_name)
        return self.player

    def play_media_from_cache(self, query):  # String Similarity using SequenceMatcher
        '''
        For Cache storing:
        1. Check if the name of the song is there in cache folder or not.
        2. If it is there play from cache or download it and play
        ('store' them && 'encrypt' them --------- 'decrypt' while using)
        '''  ## ---- {'q': query, 'c': cache} ---- ##

        def set_sort_join_string(s1):
            if '.mp3' in s1:
                s1 = s1.split('.mp3')[0]
            s1 = self.clean_file_name(s1)
            s1 = self.adjust_file_name(s1)
            s1 = ''.join(s1.split('-'))
            s2 = list(set([x for x in s1]))
            s2.sort()
            s1 = ''.join(s2)
            return s1

        def sentence_matcher(q, c):  # q: ['suna', 'man', 'ka']; c: ['soona', 'mann', 'ka', 'aangan']
            q1 = [set_sort_join_string(x) for x in q]
            print(f'Query after cleaning: {q1}')
            c1 = [set_sort_join_string(x) for x in c]
            print(f'Cache after cleaning: {c1}')

            print(f'First word of query: {q1[0]}')
            print(f'First word of cache: {c1[0]}')

            if len(q1[0]) != len(c1[0]):
                min_str = min([q1[0], c1[0]], key=len)
                print(f'min_str: {min_str}')
                max_str = max([q1[0], c1[0]], key=len)
                print(f'max_str: {max_str}')
            else:
                min_str = q1[0]
                max_str = c1[0]

            match = True
            p = 0
            for i in range(len(min_str)):
                p = i
                if max_str[i] != min_str[i]:
                    match = False
                    break

            if match:
                print('Matched!')
                return True
            elif p >= len(max_str) // 2:
                m = SequenceMatcher(None, max_str, min_str)
                if m.ratio() > 0.95:
                    print('Matched with Matcher!')
                    return True
                else:
                    print('No Match!')
                    return False

        # 'Format' string and match with 'first word' of 'list' with first word of 'query'; then go to 'second word'; so on...
        os.chdir(cache_dir)
        q = query.split(' ')
        for c in glob('*.mp3'):
            k = c
            c = c.lower()
            c1 = c.split('.mp3')[0]
            c1 = c1.replace('-', ' ').strip().split(' ')
            print(f'Song Found: {k}')
            if sentence_matcher(q, c1):
                return k

        return None

    def add_playlist(self, search_query):
        url = self.url_search(search_query, max_search=1)
        self.playlist.append(url)


class _Vocabulary:  # Reads data from datasets; Store personalised data
    ## ---- SYNONYMS ---- ##
    SYNONYMS = {
        'PLAY': ['play', 'begin'],  # This will act as 'Replay' (when called while playing a song)
        'PAUSE': ['pause', 'hold', 'break', 'suspend', 'interrupt'],
        'RESUME': ['resume'],
        'REPLAY': ['replay', 'repeat', 'reply'],
        # 'reply' is added since 'speech_recognition' sometimes hear 'reply' when I say 'replay'... LOL!
        'RESTART': ['restart', 'beginning', 'starting', 'start from ', 'play from '],
        'STOP': ['stop', 'close', 'finish', 'end', 'terminate', 'wind up', 'windup'],
        'VOLUME UP': ['up', 'volume up', 'increase volume', 'increase'],
        'VOLUME DOWN': ['down', 'volume down', 'decrease volume', 'decrease'],
        'MAX VOLUME': ['max', 'max volume', 'full volume', 'loud volume'],
        'MIN VOLUME': ['min', 'min volume', 'low volume', 'whisper'],
        'MUTE': ['mute', 'no volume', 'no sound', 'silent']
    }

    ## ---- JOKES ---- ##
    df = pd.read_csv(jokes)
    joke = df['Joke']
    random_joke_id = np.random.permutation(np.arange(0, len(joke) - 1))[:1]
    JOKES = {
        'joke': str(joke[random_joke_id[0]])
    }

    ## ---- Conversation ---- ##
    BRAIN = pd.read_csv(brain)

    ## ---- Song Search Abort ---- ##
    skip_song_search_queries = ['skip', 'abort']
    retry_song_search_queries = ['retry', 'search again', 'other', 'new', 'different', 'none of these', 'not these',
                                 'not this']  ## NOTE: not able to handle wrong entry correctly; re-executing searched result

    ## ---- ABILITIES ---- ##
    ABILITIES = ['wikipedia', 'open youtube', 'open google', 'open stackoverflow', 'play song', 'time', 'open code',
                 'quit', 'news']
    my_abilities_with_keywords = {
        'Search for information on wikipedia': ['info', 'information', 'wiki', 'wikipedia'],
        'Open Youtube and search for you': ['youtube', 'searching youtube', 'youtube search', 'open youtube',
                                            'youtube opening', 'viewing youtube', 'youtube viewing', 'watching youtube',
                                            'youtube watching'],
        'Open Google and search for you': ['google'],
        'Open stackoverflow and search for you': ['stackoverflow'],
        'Stream Song from youtube directly for you': ['stream', 'song', 'streaming', 'music'],
        'Tell you the current time': ['time', 'tell'],
        'Open VS Code for you': ['VS', 'Code'],
        'have general conversation with you': ['conversation', 'talk'],
        'Read out live news for you': ['news', 'break', 'hot'],
        'saying Goodbye': ['Goodbye'],
    }  # {'Ability to speak out' : 'keyword/s'}


class Voice_Assistant:  ## NOTE: Play a beep when sub-queries are searched
    '''
    Overview:
        Perform any task just with your voice.

    Description:
        This Voice Assistant has a lots of Abilities (mentioned inside sub-class 'Abilities'). Basically when we ask 'AI' engine for any task. Then it asks its own 'Abilities' to perform some task based on input query. Then it takes the output and return it to us.
    '''

    '''
    How to improve its speech recognision:

    Create a list[...] to keep track of words asked as query to VA.
    So as to improve day-by-day its speech recognition; using ''cosine-similarity'' (or any sort of text matching algorithm) between 'new query asked and old queries made'.
    If better result is observed; replace the old one with the new one.
    '''

    def __init__(self):
        # self.engine = pyttsx3.init('sapi5')
        # self.voices = self.engine.getProperty('voices')
        # self.engine.setProperty('voice', self.voices[0].id)
        self.VA_NAME = 'Jarvis'
        self._Vocabulary = _Vocabulary()
        self.ytb = _Youtube_mp3()
        self.search_terms = self._Vocabulary.ABILITIES
        self._song_name = ''
        self.player = _Media_Player()
        self.__retry_list = 1  # if the first 5 searches doesn't contain any media file; then go for next 5 searches
        # self.stream = _Song_Search_and_Stream()

    def _speak(self, text):
        tts = gTTS(text=text, lang='en')  # NOTE: Taking too much time saving to a file and reading out
        filename = 'voice.mp3'
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)

        # self.engine.say(text)  # NOTE: But this process worked previously but not now
        # self.engine.runAndWait()

    def __wish_me(self):
        hour = int(datetime.now().hour)
        if 0 <= hour < 12:
            self._speak('Good Morning!')
        elif 12 <= hour < 18:
            self._speak('Good Afternoon!')
        else:
            self._speak('Good Evening!')

        # self._speak(f'Hello Sir. I am {self.VA_NAME} - Your personal voice assistant!')
        self._speak('How may I help You?')

    def _take_command(self, waiting_for_query=''):  ## NOTE: Execution Stopped (hanged)
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
            ## NOTE: Add what the mic is waiting to hear from you
            print(
                f'Waiting for: {waiting_for_query}\nListening...')  # execute in seperate threads; if one gets hanged (overloaded) kill that; start new ['DEBUGGING' purpose only] <--> comment it when 'using'
            r.pause_threshold = 1  # let it be as '1'
            r.energy_threshold = 100  # Default: 300 (now less energy reqd. while speaking)
            audio = r.listen(source)

        try:
            print('Recognizing...')
            query = r.recognize_google(audio, language='en-in')
            print(f'User Said: {query}\n')
        except Exception:
            print('Say that again please...')
            return 'none'
        return query.lower()

    def _substr_in_list_of_strs(self, lst, substr):
        '''
        Objective: Check if a substring is present in a list of strings

        Source: https://www.geeksforgeeks.org/python-finding-strings-with-given-substring-in-list/
        '''
        res_lst_of_strs_with_substr = list(filter(lambda x: substr in x, lst))
        return bool(res_lst_of_strs_with_substr), res_lst_of_strs_with_substr

    def _stream_online(self, song_name, number=0):  # number = song_number to play in the list of search results
        max_search = 1
        valid_song = False
        song_name_recv = ''

        if number == 0:  # direct play; doesn't involve user
            self._speak('Searching Song...')
            cache_search = self.ytb.play_media_from_cache(song_name)
            if not cache_search:
                songs_list = self.ytb.url_search(song_name,
                                                 max_search)  ##NOTE: add 'search_more' parameter in 'url_search()' that will hold an integer of 'self.__retry_list'
                print(f'songs_list: {songs_list}')
                if songs_list:
                    for sl_no, url in songs_list.items():
                        print(sl_no, url)
                        os.chdir(tmp_dir)
                        song_name_recv = self.ytb.test_url(song_name,
                                                           url)  # TODO: {song_name: saved_name} ; need to store this dict as json file for cache search
                        os.chdir(cache_dir)
                        # print(f'song name recv in _stream_online: {song_name_recv}')
                        print(f"\n\nsong_name_recv tmp: {song_name_recv}")
                        if song_name_recv and [
                            self.ytb.play_media_from_cache(song_name_recv.split('.')[0])]:  # valid song found
                            valid_song = True
                            break
                        else:
                            continue
                    if valid_song:
                        shutil.rmtree(tmp_dir, ignore_errors=True)
                        self.player = self.ytb.play_media(song_name_recv)
                    else:  # list of 5 searches exhausted
                        pass  # self.__retry_list += 1 (----if the first 5 searches doesn't contain any media file; then go for next 5 searches----)
                else:
                    self.player = None
                    pass  # Say Again
            else:  # Play from cache
                self._speak('Playing from your cache')
                shutil.rmtree(tmp_dir, ignore_errors=True)
                self.player = self.ytb.play_media(cache_search)

        '''else: # Not implemented yet
            song_search_query = [song_name + ' ' + key for key in ('lyric', 'full', 'audio', 'official', '|')]
            print(f'song_search_query: {song_search_query}')
            results_found = False
            for query in song_search_query: # search for 'song_name' + ==> ('lyric', 'full', 'audio', 'official', '|')
                self.ytb.url_search(query, max_search)
                #search_titles = self.ytb.get_search_items(number) # Return the result list for each 'query';; don't print the list (since, number != 0)
                if search_titles: # if atleast 1 song found
                    for num in search_titles[0].keys(): # traverse the list for the search query
                        if query.split()[-1] in search_titles[0][num][0]: # if any('lyric', 'full', 'audio', 'official', '|') in search_titles[0][num][0] <-- song_title
                            results_found = True
                            number = num
                            break
                if results_found:
                    break
            if results_found:
                print(f'\n\nsong in wiki search ---- results_found:\n{results_found}\n\n')
                self.player = self.ytb.play_media(number)
            else: # If direct song play did not work for 'play_song_from_last_search()' then call 'self._stream_online(song_name, number=0); since here 'number=1'
                self._stream_online(song_name, number=0)'''

        return self.player

    class Abilities:  ## NOTE: Handle any type of 'can you <>';; direct perform action rather than telling what to ask
        '''
        Overview:
            The 'Abilities' that I have to perform various tasks.

        Myself:
            My 'Abilities' are very limited.

        NOTE: A task for you... "Please train me with new 'Abilities' so that I can stand in the real world"
        '''

        '''
        NOTE: Add support for wikipedia extract for information like ('Bollywood movies releasing next month')
        '''

        '''
        NOTE: If 'another / again' joke is asked; SAY it;; or else pass this 'query' to main 'Thread' so that ita can execute any of its tasks
            {Don't use this approach;; or else it has to be implemented on every sub-tasks}

        Instead:
            1. Go back to main thread
            2. If 'another / again' is asked
            3. It will check what was the last thing asked <stored in a list[]>
            4. Based on that; it will call the respective function

        NOTE: It can conflict with the feature 'Abilities.play_song_from_last_search(<webpage>)'. Make the commands unique [SMARTer recognision]
        '''

        def __init__(self):
            self.__va = Voice_Assistant()
            self.__my_abilities_with_keywords = self.__va._Vocabulary.my_abilities_with_keywords
            self.__my_abilities_with_index = list(zip(list(range(0, len(self.__my_abilities_with_keywords))),
                                                      self.__my_abilities_with_keywords.keys()))  # zip ('index numbers', my_abilities)
            self.__random_2_numbers = list(
                np.random.permutation(np.arange(0, len(self.__my_abilities_with_keywords) - 1))[:2])
            self.__call_VA_timout = 1
            self.__queries_made = []
            self.__unknown_abilities = []

        def what_can_you_do(self, query):  # Return 2 random abilities from 'self.my_abilities'[0:-1] and 'Bid Goodbye'
            if 'how can you help in ' in query or 'how can you help me ' in query:
                self.how_can_you(query)
            else:
                first = self.__my_abilities_with_index[self.__random_2_numbers[0]][1]
                second = self.__my_abilities_with_index[self.__random_2_numbers[1]][1]
                last = self.__my_abilities_with_index[-1][1]
                i_can_do = 'Out of many; I can ' + first + '; or even ' + second + ' . Or you can quit this application by ' + last
                self.__va._speak(i_can_do)

        def how_can_you(self, query):  # Handles any type of 'How can you <task>'
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
                        what_to_ask = self.__va.search_terms[
                            c]  # list(self.my_abilities_with_keywords.keys())[list(self.my_abilities_with_keywords.values()).index(common_keyword[0])]
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

        def wikipedia(self, query):  ## NOTE: Incomplete
            self.__queries_made.append(query)
            self.__va._speak('Searching Wikipedia...')
            query = query.replace('wikipedia',
                                  '')  ## NOTE: If 'query' is only 'wikipedia' then this line will throw 'wikipedia.exceptions.WikipediaException'; deal with it
            try:
                results = wikipedia.summary(query, sentences=2)
                self.__va._speak('According to Wikipedia')
                print(results)
                self.__va._speak(results)
            except wikipedia.exceptions.PageError:
                self.__va._speak('Sorry! Page Not Found!')
            except wikipedia.exceptions.DisambiguationError as e:  # "Bengali Movie Wikipedia"; "SK Wikipedia"
                queries = e.options
                sub_queries = {}
                self.__va._speak('Following are the options found, matching your query')
                for num, option in enumerate(queries):
                    print('{0}. {1}'.format(num + 1, option))
                    sub_queries[num] = option
                self.__va._speak('Which Number Page? (SAY for example, Number 1)')  ## NOTE: Incomplete...
                while True:
                    page_num = self.__va._take_command('Which Number Wikipedia Page? (SAY for example, Number 1)')
                    if page_num != 'none':
                        break
                new_query = sub_queries[int(page_num.strip().split()[-1]) - 1]
            except wikipedia.exceptions.WikipediaException:  ## NOTE: Incomplete...
                print('Say that again please...')
                self.__va._speak('search wikipedia')
                while True:
                    new_query = self.__va._take_command('what to search in wikipedia')
                    if new_query != 'none':
                        break
                results = wikipedia.summary(new_query, sentences=2)
                self.__va._speak('According to Wikipedia')
                print(results)
                self.__va._speak(results)

        def youtube(self, query):
            self.__queries_made.append(query)
            self.__va._speak('What to search for?')
            while True:
                search_term = self.__va._take_command('What to search in youtube?')
                if search_term != 'none':
                    break
            query = quote(search_term)
            url = "https://www.youtube.com/results?search_query=" + query
            webbrowser.open_new_tab(url)

        def google(self, query):
            self.__queries_made.append(query)
            self.__va._speak('What to search for?')
            while True:
                search_term = self.__va._take_command('What to search in google?')
                if search_term != 'none':
                    break
            query = quote(search_term)
            url = "https://www.google.com/search?q=" + query
            webbrowser.open_new_tab(url)

        def play_song_from_last_search(self, website):  ## NOTE: Incomplete
            if website == 'wikipedia':
                search_sub = self.__va._substr_in_list_of_strs(self.__queries_made, 'wikipedia')
                if search_sub[0]:  # if wikipedia searched
                    if len(search_sub[1]) >= 1:
                        last_searched_query = search_sub[1][-1]
                        song_name = last_searched_query.replace('wikipedia', '').strip()
                        wiki_res = wikipedia.summary(song_name, sentences=10)  # check id query is a valid song or not
                        if 'music' in wiki_res or 'song' in wiki_res or 'film' in wiki_res:
                            self.__va._stream_online(song_name, 1)
                        else:
                            self.__va._speak('No song searched in wikipedia!')
                    else:
                        query = search_sub[1][-1]
                        song_name = query.replace('wikipedia', '').strip()
                        wiki_res = wikipedia.summary(song_name, sentences=10)  # check id query is a valid song or not
                        if 'music' in wiki_res or 'song' in wiki_res or 'film' in wiki_res:
                            self.__va._stream_online(song_name, 1)  ## Will not work now;; See LINE: 306
                        else:
                            self.__va._speak('No song searched in wikipedia!')
                    return True

            elif website == 'youtube':
                pass  # self.__va._stream_online();; first result
                return True

            elif website == 'google':
                pass  # self.__va._stream_online();; first result with a song name
                return True

            else:
                self.__va._speak('No song found in search queries! Instead ask to play song...')
                return False

        def stream_song(self, query):  # Selenium in 'gaana.com'
            '''
            Use 2 threads:
            1. 'main thread' to handle the selenium webdriver for song playing (or else not be able to use device or interrupt --- only possible till song ends)
            2. to handle all the controls
            '''  # 'STOP' --> 'self.driver.quit()'
            ## Add support for play songs from the movie / album (sleep for total duration of all songs; and support for play next / prev; stop any)
            ## For controls actions use selenium itself for; next, prev, pause, play, replay, album play
            search_term = ' '.join(query.split()[1:])
            gaana = Gaana(search_term)
            gaana.play_song()

        def play_song(self, query):  # Use multi-threading for 'song playing' and 'media-player controls' (2 threads)
            def any_keyword_match_with_Vocabulary(keyword, list_to_search_in):
                for key in list_to_search_in:
                    if keyword.lower() in key.lower() or key.lower() in keyword.lower():  # Simplest 'text matching algorithm'
                        return True
                return False

            paused = False
            replay_song = False
            search_term = ' '.join(query.split()[1:])
            music_player = self.__va._stream_online(search_term)
            if music_player:
                music_player.play()
            else:
                self.__va._speak('Sorry Sir! Did not get you!')
                while True:
                    self.__va._speak('Please say that again!')
                    retry = self.__va._take_command('Waiting for Search Song Again')
                    if not retry:
                        continue
                    self.play_song(retry)

            control = ''  # To detect 'STOP'
            while True:
                call_VA = self.__va._take_command('Waiting for (OK JARVIS)')
                if self.__va.VA_NAME.lower() in call_VA:  # If VA is called
                    music_player.pause()
                    wait = 1
                    control = ''
                    while not control or wait <= self.__call_VA_timout:
                        control = self.__va._take_command('Waiting for Music Control Actions')
                        if control:  # TODO: if anything other than player controls asked ; stop music and continue to serve the new command
                            if any_keyword_match_with_Vocabulary(control, self.__va._Vocabulary.SYNONYMS[
                                'PLAY']):  # start from beginning
                                music_player.resume()  # Eliminated everything from (_Vocabulary.SYNONYMS['PLAY'])
                            elif any_keyword_match_with_Vocabulary(control,
                                                                   self.__va._Vocabulary.SYNONYMS['PAUSE']):  # pause
                                music_player.pause()
                                paused = not paused  # To stop replaying when in paused; when VA is called and no query passed
                            elif any_keyword_match_with_Vocabulary(control, self.__va._Vocabulary.SYNONYMS[
                                'REPLAY']):  # A MODE to restart the song once it finishes
                                replay_song = music_player.replay()
                                music_player.resume()
                            elif any_keyword_match_with_Vocabulary(control, self.__va._Vocabulary.SYNONYMS[
                                'RESTART']):  # pause
                                music_player.restart()
                            elif any_keyword_match_with_Vocabulary(control, self.__va._Vocabulary.SYNONYMS[
                                'RESUME']):  # start after pause
                                music_player.resume()
                            elif any_keyword_match_with_Vocabulary(control, self.__va._Vocabulary.SYNONYMS[
                                'VOLUME UP']):  # Volume Up
                                music_player.volume(mode='up')
                            elif any_keyword_match_with_Vocabulary(control, self.__va._Vocabulary.SYNONYMS[
                                'VOLUME DOWN']):  # Volume Down
                                music_player.volume(mode='down')
                            elif any_keyword_match_with_Vocabulary(control, self.__va._Vocabulary.SYNONYMS[
                                'MAX VOLUME']):  # Volume Down
                                music_player.volume(mode='max')
                            elif any_keyword_match_with_Vocabulary(control, self.__va._Vocabulary.SYNONYMS[
                                'MIN VOLUME']):  # Volume Down
                                music_player.volume(mode='min')
                            elif any_keyword_match_with_Vocabulary(control, self.__va._Vocabulary.SYNONYMS[
                                'MUTE']):  # Volume Down
                                music_player.volume(mode='mute')
                            elif any_keyword_match_with_Vocabulary(control, self.__va._Vocabulary.SYNONYMS[
                                'STOP']):  # stop the song && closes the '_Media_Player' instance
                                music_player.stop()
                                print(f'Current Position: {music_player.current_time()}\n')
                                break
                        wait += 1
                        print(f'waiting for control command... timeout[{wait}]')
                    if any_keyword_match_with_Vocabulary(control, self.__va._Vocabulary.SYNONYMS[
                        'STOP']):  # exit from 'play_song()'
                        break
                    elif wait >= self.__call_VA_timout:
                        if not paused:
                            music_player.resume()  # If nothing is said after calling VA
                            print('TIMEOUT Happened.... and Playback RESUMED....')
                elif 'none' in call_VA or '' in call_VA:  # If some text from unwanted voice is detected; it will skip and 'restart()' will be called
                    continue
                elif replay_song and not 'when_song_ends()':  # To avoid this just using 'not when_song_ends()' (Means, song will never end) [A . False = False]
                    music_player.restart()

        def stackoverflow(self, query):
            self.__va._speak('What to search for?')
            while True:
                search_term = self.__va._take_command('What to search in stackoverflow?')
                if search_term != 'none':
                    break
            query = quote(search_term)
            url = "https://stackoverflow.com/search?q=" + query
            webbrowser.open_new_tab(url)

        def current_time(self, query):
            str_time = datetime.now().strftime("%H:%M:%S")
            self.__va._speak(f'Sir, The Time is {str_time}')

        def open_app(self, query):
            code_path = 'C:\\Users\\dgkii\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe'
            os.startfile(code_path)

        def quit_VA(self, query):
            os.chdir(cache_dir)
            shutil.rmtree(tmp_dir, cache_dir)
            hour = int(datetime.now().hour)
            if 0 <= hour <= 18:
                self.__va._speak('Good Bye Sir, Thanks for your time! Have a nice day')
            else:
                if 'good night' in query:
                    self.__va._speak('Good Bye Sir, Thanks for your time! Good Night!')
                else:
                    self.__va._speak('Good Bye Sir, Thanks for your time!')

        def conversation(self):  # This the brain of my VA. Read 'datasets/brain.csv'; create and train model to have conversation with user
            brain = self.__va._Vocabulary.BRAIN
            self.stop = False

            ## Approximating QA system
            # Approximate string matching
            def getApproximateAnswer(q):
                max_score = 0
                answer = ""
                prediction = ""
                for _, row in brain.iterrows():
                    score = ratio(row["Question"], q)
                    if score >= 0.9:  # I'm sure, stop here
                        return row["Answer"], score, row["Question"]
                    elif score > max_score:  # I'm unsure, continue
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
                        question = self.__va._take_command('Waiting for you to have coversation...')
                        if question != 'none':
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

        def read_out_news(self, query):  # query: NEWS Category (region / topic / etc...)
            url = 'https://opensourcepyapi.herokuapp.com:443/news'  # World News
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
                c += 1
                Beep(1047, 300)
                sleep(1)
            self.__va._speak('Thank You!')

        '''def read_out_news(self, query): # query: NEWS Category (region / topic / etc...) NOTE: [NEW Function ;; Not working]
            url = 'http://newsapi.org/v2/top-headlines?country=in&apiKey=e1cbf7941ba44b37bcf9e51cf289b804' # INDIA NEWS

            data = dict()
            with urlopen(url) as response:
                source = response.read()
                data = json.loads(source)

            sleep(1)
            print(data['articles'][0].keys())

            NEWS = data['articles']
            NEWS_Source = NEWS[0]['source']['name']
            NEWS_Headlines = NEWS[0]['title']
            NEWS_Description = NEWS[0]['description']
            NEWS_Link = NEWS[0]['url']

            print(f'{NEWS_Source}\n{NEWS_Headlines}\n{NEWS_Description}\n{NEWS_Link}\n')

            random_10_numbers = list(np.random.permutation(np.arange(0, len(NEWS_Headlines) - 1))[:10])
            random_10_news = [NEWS[i] for i in random_10_numbers]

            self.__va._speak('TOP 10 Headlines Today...')
            for i in range(len(random_10_news)): ## ERROR (check data-structure)
                news_headlines = random_10_news[i]['title']
                print(f"Number {i+1}: {news_headlines}")
                self.__va._speak(f'Number {i+1}')
                self.__va._speak(news_headlines)
                Beep(1047, 300)
                sleep(1)
            self.__va._speak('Thank You!')'''

        def tell_joke(self):
            jokes = self.__va._Vocabulary.JOKES
            self.__va._speak(jokes['joke'])

            ## ---- another / again ---- ## {check before 'Abilities.__init__()'}

    def start_AI_engine(self):  ### TODO: If valid query => calls respective functions in 'Abilities'; Else => calls 'Abilities.what_can_you_do()'
        self.__wish_me()
        self.__if_any_query_made = False
        self.__time_out_between_failed_queries = 1  # seconds
        self.__last_webpage_visited = ''  # store the """webpage name from each""" queries_made
        self.__available_webpages = {
            'w': 'wikipedia',
            'y': 'youtube',
            'g': 'google'}

        while True:
            self.__abilities = self.Abilities()
            query = self._take_command('Waiting for commands in main thread').lower()
            print(f'query: {query}')
            # Logic for executing tasks based on query
            ### if self._substr_in_list_of_strs('can do perform'.split(), query)[0]:
            '''
            NOTE: Make all the following 'if conditions' to come from '_Vocabulary'. So that they can be re-usable (if 'another' / 'again' asked)
            '''
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

            elif 'play ' in query:  # Before starting to play; just say the name of the song and its info
                self.__if_any_query_made = True
                self.__abilities.play_song(query)
                # self.__abilities.stream_song(query)

            elif 'stream ' in query or 'cream ' in query:
                self.__if_any_query_made = True
                self.__abilities.stream_song(query)

            elif 'open stackoverflow' in query:
                self.__if_any_query_made = True
                self.__abilities.stackoverflow(query)

            elif 'time' in query:
                self.__if_any_query_made = True
                self.__abilities.current_time(query)

            elif 'open vs code' in query:  ## NOTE: don't use absolute path; instead search for its executable (.exe) file and then execute
                self.__if_any_query_made = True
                self.__abilities.open_app(query)

            elif 'bye' in query or 'quit' in query or 'stop' in query or 'exit' in query:
                self.__if_any_query_made = True
                self.__abilities.quit_VA(query)
                return False

            elif 'conversation' in query or 'talk' in query:
                self.__if_any_query_made = True
                self._speak('Sure Sir!')
                return self.__abilities.conversation()

            elif query == 'none' and not self.__if_any_query_made:  # Stop executing when not asked anything
                self.__abilities.what_can_you_do(query)
                sleep(self.__time_out_between_failed_queries)

            elif 'news' in query:
                self.__if_any_query_made = True
                self.__abilities.read_out_news(query)

            elif 'joke' in query:
                self.__if_any_query_made = True
                self.__abilities.tell_joke()

            elif 'another' in query or 'again' in query:
                pass
                # last_thing_asked = self.__get_last_thing_asked()
        return True
