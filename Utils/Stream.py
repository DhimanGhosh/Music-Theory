import os, random
from time import sleep
from lxml import html  ## to get the data of '<div> ... </div>'
# https://stackoverflow.com/questions/38174490/how-can-i-collect-this-data-from-a-div-using-selenium-and-python

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Music:  ## NOTE: Open Chrome Headless
    def __init__(self):
        self.driver = webdriver.Chrome('D:\\PYTHON\\Codes\\Audio-Made-Easy\\assets\\chromedriver.exe')
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=0x0')


class Google(Music):  # "((//div[@class='BFJZOc']//div)[1])//a" ## Song Link
    def __init__(self, song_search):
        super(Google, self).__init__()
        self.driver.get('https://google.com/')
        self.song_search = song_search
        self.timeout = 3

    def __page_load_wait(self, driver, timeout, xpath):
        try:
            element_present = EC.presence_of_element_located((By.XPATH, xpath))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
        finally:
            print("Page loaded")

    def __find_song(self):
        song_name = self.driver.find_element(By.XPATH, "(//div[@class='search_song']//input)")  # Search song
        song_name.send_keys(self.song_search)
        search_button = self.driver.find_element(By.XPATH, "(//div[@class='search_song']//a)")  # Click on search
        hover = ActionChains(self.driver).move_to_element(search_button)
        hover.click().perform()
        self.__page_load_wait(self.driver, self.timeout,
                              "(//li[@class='list loaded']//a[@title])[1]")  # Get link of all songs
        song = self.driver.find_element(By.XPATH,
                                        "(//li[@class='list loaded']//a[@title])[1]")  # "Aur Tanha Song · Love Aaj Kal"
        song_info = self.driver.find_element(By.XPATH,
                                             "(//li[@class='list loaded']//a[@title]//span)[1]")  # "Song · Love Aaj Kal"
        song_url = song.get_attribute("href")  # https://gaana.com/song/aur-tanha
        song_title = song.get_attribute("title")  # "Aur Tanha Song · Love Aaj Kal"
        album_name = song_info.text  # "Song · Love Aaj Kal"
        return song_url, song_title, album_name, song

    def __get_duration_of_song_in_sec(self, duration):
        dur = duration.split(':')  # H : M : S
        if len(dur) == 3:
            d = 3600 * int(dur[0]) + 60 * int(dur[1]) + int(dur[2])
        elif len(dur) == 2:
            d = 60 * int(dur[0]) + int(dur[1])
        else:
            d = int(dur[0])
        return d

    def play_song(self):  ## BUG: Unable to find the duration 'text' correctly
        song = self.__find_song()
        song_url = song[0]
        song_title = song[1]
        album = song[2].split('·')[-1].strip()
        print('Song URL: {}\nSong Info: {}\nAlbum Name: {}'.format(song_url, song_title, album))
        hover = ActionChains(self.driver).move_to_element(song[3])
        hover.click().perform()
        # self.__page_load_wait(self.driver, self.timeout, "//li[@class='s_duration']//a[@data-type='playSong']") # song duration (somrtime error: 'mithe alo')
        self.__page_load_wait(self.driver, self.timeout, "//div[@class='timer-wrap']//div[2]")
        song_duration = self.driver.find_element(By.XPATH, "//div[@class='timer-wrap']//div[2]")  # Get duration of song
        duration = song_duration.get_attribute("text")
        get_lyrics = ''
        print(f'Duration: {duration}')
        dur = self.__get_duration_of_song_in_sec(duration)
        sleep(dur)
        self.__quit()  # for stop playing any more songs

    def __quit(self):
        self.driver.quit()


class Gaana(Music):
    def __init__(self, song_search):
        super(Gaana, self).__init__()
        self.driver.get('https://gaana.com/')
        self.song_search = song_search
        self.timeout = 3

    def __page_load_wait(self, driver, timeout, xpath):
        try:
            element_present = EC.presence_of_element_located((By.XPATH, xpath))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
        finally:
            print("Page loaded")

    def __find_song(self, song_search):
        song_name = self.driver.find_element(By.XPATH, "(//div[@class='search_song']//input)")  # Search song
        song_name.send_keys(song_search)
        search_button = self.driver.find_element(By.XPATH, "(//div[@class='search_song']//a)")
        hover = ActionChains(self.driver).move_to_element(search_button)  # Click on search
        hover.click().perform()
        self.__page_load_wait(self.driver, self.timeout,
                              "(//li[@class='list loaded']//a[@title])[1]")  # Get link of all songs
        song_obj = self.driver.find_element(By.XPATH,
                                            "(//li[@class='list loaded']//a[@title])[1]")  # "Aur Tanha Song · Love Aaj Kal"
        song_info = self.driver.find_element(By.XPATH,
                                             "(//li[@class='list loaded']//a[@title]//span)[1]")  # "Song · Love Aaj Kal"
        song_url = song_obj.get_attribute("href")  # https://gaana.com/song/aur-tanha
        song_title = song_obj.get_attribute("title")  # "Aur Tanha Song · Love Aaj Kal"
        album_name = song_info.text.split('·')[-1].strip()  # "Song · Love Aaj Kal" ## "Love Aaj Kal"
        return (song_url, song_title, album_name, song_obj)

    def __find_song_in_album(self, song_search, album_search):
        album_name = self.driver.find_element(By.XPATH, "(//div[@class='search_song']//input)")  # Search album
        album_name.send_keys(album_search)
        search_button = self.driver.find_element(By.XPATH, "(//div[@class='search_song']//a)")
        hover = ActionChains(self.driver).move_to_element(search_button)  # Click on search
        hover.click().perform()
        self.__page_load_wait(self.driver, self.timeout,
                              "(//li[@class='list loaded']//a[@title])[1]")  # Get link of album
        album_obj = self.driver.find_element(By.XPATH,
                                             "(//li[@class='list loaded']//a[@title])[1]")  # "Borbaad Album · 2014"
        album_info = self.driver.find_element(By.XPATH,
                                              "(//li[@class='list loaded']//a[@title]//span)[1]")  # "Album · 2014"
        album_url = album_obj.get_attribute("href")  # https://gaana.com/album/borbaad
        album_title = album_obj.get_attribute("title")  # "Borbaad"
        album_year = album_info.text.split('·')[-1].strip()  # "2014"
        hover = ActionChains(self.driver).move_to_element(album_obj)  # Click on Album Name
        hover.click().perform()

        # Return 'first song' with the 'first word' of 'song_search'
        tot_songs = 8
        song_obj = None
        self.__page_load_wait(self.driver, self.timeout,
                              "(((//div[@class='s_c']//li[@draggable='true'])[1])//a[@data-type='playSong'])[2]")  # Songs List

        album_tot_duration = self.driver.find_element(By.XPATH,
                                                      ("(//li[@class='s_duration']/a[1])[2]"))  # album duration
        print(f"album_tot_duration: {album_tot_duration.get_attribute('text')}")

        for i in range(1, tot_songs + 1):
            song_obj = self.driver.find_element(By.XPATH,
                                                f"((//div[@class='s_c']//li[@class='draggable'])[{i}])//a[@class='sng_c']")
            song_title = song_obj.get_attribute('text')
            print(f"Song Name: {song_obj.get_attribute('text')}")
            duration = self.driver.find_element(By.XPATH,
                                                f"((//div[@class='s_c']//li[@draggable='true'])[{i}])//li[@class='s_duration']")
            print(f"Duration: : {duration.get_attribute('text')}")

        song_url = ''
        album_name = ''
        return (song_url, song_title, album_name, song_obj)

    def __get_duration_of_song_in_sec(self, duration):
        dur = duration.split(':')  # H : M : S
        if len(dur) == 3:
            d = 3600 * int(dur[0]) + 60 * int(dur[1]) + int(dur[2])
        elif len(dur) == 2:
            d = 60 * int(dur[0]) + int(dur[1])
        else:
            d = int(dur[0])
        return d

    def play_song(self):  ## BUG: Unable to find the duration 'text' correctly
        '''if 'from' in self.song_search: # song search from album
            album_search = self.song_search.split('from')[-1].strip()
            song = self.__find_song_in_album(self.song_search.split('from')[0].strip(), album_search)
        else:
            song = self.__find_song(self.song_search)'''
        song = self.__find_song(self.song_search)
        song_url = song[0]
        song_title = song[1]
        album = song[2]
        print('Song URL: {}\nSong Info: {}\nAlbum Name: {}'.format(song_url, song_title, album))
        hover = ActionChains(self.driver).move_to_element(song[3])
        hover.click().perform()
        # self.__page_load_wait(self.driver, self.timeout, "//li[@class='s_duration']//a[@data-type='playSong']") # song duration (somrtime error: 'mithe alo')
        self.__page_load_wait(self.driver, self.timeout, "//div[@class='timer-wrap']//div[2]")
        song_duration = self.driver.find_element(By.XPATH, "//div[@class='timer-wrap']//div[2]")  # Get duration of song
        duration = song_duration.get_attribute("text")
        get_lyrics = ''
        print(f'Duration: {duration}')
        dur = self.__get_duration_of_song_in_sec(duration)
        sleep(dur)
        self.__quit()  # for stop playing any more songs

    def __quit(self):
        self.driver.quit()


class Webmusic(Music):
    def __init__(self, song_search):
        super(Webmusic, self).__init__()
        self.driver.get('http://webmusic.live/')


class DjMaza(Music):  # will work on this later due to ad page
    def __init__(self, song_search):
        super(DjMaza, self).__init__()
        self.driver.get('https://www.djmazak.com/')
        self.song_search = song_search
        self.timeout = 3

    def page_load_wait(self, driver, timeout, xpath):
        try:
            element_present = EC.presence_of_element_located((By.XPATH, xpath))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
        finally:
            print("Page loaded")

    def close_last_tab(self):
        if (len(self.driver.window_handles) == 2):
            self.driver.switch_to.window(window_name=self.driver.window_handles[-1])
            self.driver.close()
            self.driver.switch_to.window(window_name=self.driver.window_handles[0])
            print('ad page deleted')

    def find_song(self):
        try:
            self.page_load_wait(self.driver, self.timeout, "(//a[@0id='lke98'])")
            ad = self.driver.find_element(By.XPATH, "(//a[@0id='lke98'])")  # Click on initial ad
            hover = ActionChains(self.driver).move_to_element(ad)
            hover.click().perform()
            self.close_last_tab()
            # self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
        except NoSuchElementException:
            print('No Ad')

        try:
            self.page_load_wait(self.driver, self.timeout, "(//div[@class='mc-closeModal'])")
            self.page_load_wait(self.driver, self.timeout, "(//div[@class='input-group']//input)")
            modal = self.driver.find_element(By.XPATH, "(//div[@class='mc-closeModal'])")  # close modal
            hover = ActionChains(self.driver).move_to_element(modal)
            hover.click().perform()
        except NoSuchElementException:
            print('No Modal')

        elem = self.driver.find_element(By.XPATH, "(//div[@class='input-group']//input)")  # Search song
        elem.send_keys(self.song_search)
        elem = self.driver.find_element(By.XPATH, "(//div[@class='input-group']//span//i)")  # Click on search
        hover = ActionChains(self.driver).move_to_element(elem)
        hover.click().perform()

    def quit(self):
        sleep(2)
        self.driver.quit()

# if __name__ == "__main__":
#     album = 'parbona ami charte toke' # full 'album' play
#     song = 'parbona'
#     song_from_album = 'parbona ami charte toke from borbaad' # 'borbaad' movie song
#     music = Gaana(song)
#     music.play_song()
