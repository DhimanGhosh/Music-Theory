import requests
import json
import pyttsx3
from time import sleep
from winsound import Beep
import numpy as np

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

url = 'https://opensourcepyapi.herokuapp.com:443/news'
r = requests.get(url)
data = r.json()

y = json.loads(data)
# print(y['Title']) ## NEWS: HEADLINES

sleep(1)
c = 1

NEWS_Headlines = list(y['Title'].values())
random_10_numbers = list(np.random.permutation(np.arange(0, len(NEWS_Headlines) - 1))[:10])
random_10_news_headlines = [NEWS_Headlines[i] for i in random_10_numbers]

speak('TOP 10 Headlines Today...')
for news in random_10_news_headlines:
    print(f'Number {c}: {news}')
    speak(f'Number {c}')
    speak(news)
    Beep(1047, 300)
    sleep(1)
    c += 1
    if c > 10:
        break
speak('Thank You!')