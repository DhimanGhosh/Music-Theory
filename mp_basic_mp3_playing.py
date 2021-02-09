import pygame


def pmusic(file):
    pygame.init()
    pygame.mixer.init()
    clock = pygame.time.Clock()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        print("Playing...")
        clock.tick(1000)


def stopmusic():
    pygame.mixer.music.stop()


def getmixerargs():
    pygame.mixer.init()
    freq, size, chan = pygame.mixer.get_init()
    return freq, size, chan


def initMixer():
    BUFFER = 3072  # audio buffer size, number of samples since pygame 1.8.
    FREQ, SIZE, CHAN = getmixerargs()
    pygame.mixer.init(FREQ, SIZE, CHAN, BUFFER)


try:
    initMixer()
    file = 'assets\\cache\\bheegey-hont-tere.mp3'
    pmusic(file)
except KeyboardInterrupt:  # to stop playing, press "ctrl-c"
    stopmusic()
    print("\nPlay Stopped by user")
except Exception:
    print("unknown error")
