#!/usr/bin/env python3

# Logic for each choice of menu
import platform
from time import sleep

if platform.system() == 'Linux':
    from Music import Music
else:
    from Utils.Music import Music

class Menu:
    def __init__(self):
        #self.__va = Voice_Assistant()
        print(f'''
        ###########################################
        ###    Welcome to Music Theory Guide    ###
        ###########################################

            1. Major Scale
            2. Major Chord
            3. Chords in Major Scale
            4. Note in Major Scales
            5. Note shift with capo position (Guitar)
            6. Scale shift with capo position (Guitar)
            7. Minor Scale
            8. Minor Chord
            9. Chords in Minor Scale
            10. Relative Minor/Major
            11. Play Tone Based on Note
            12. Play Tone in Sequence (Scale / Note Sequence)
            13. Scale from Chords
            14. Scale from Notes
            15. Detect Notes in a Audio (wav) file
            16. Play Audio from a file (wav)
            17. Record and Playback
            18. Record and Save
            19. Play MP3 Audio
            20. AI Voice Assistant 'GOOGLE'
            21. Best Capo position for easy play (Feature coming soon)
            22. Quit
        ''')
        self.__talk('Welcome to Music Theory Guide')
    
    def __talk(self, text):
        if platform.system() == 'Linux':
            music = Music()
            music.linux_speech(text)
        # else:
        #     va = Voice_Assistant()
        #     va._speak(text)

    def __valid_input(self, input_text): # Control empty user input
        while True:
            self.__talk('Enter {}'.format(input_text))
            data = input("{}: ".format(input_text))
            if data is '':
                self.__talk('Invalid {} Entered'.format(input_text))
                continue
            else:
                break
        self.__talk('You entered {}'.format(data))
        return data

    def major_scale(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Major Scale')
        note = self.__valid_input('Note')
        music = Music(note)
        if music.valid_note(note)[1]:
            if music != None:
                result = music.major_scale()
                print("Notes for {} Major Scale: ".format(note) + ' '.join(result))
            else:
                self.Study_Music_Theory()
        else:
            self.Study_Music()

    def major_chord(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Minor Chord')
        note = self.__valid_input('Note')
        music = Music(note)
        if music.valid_note(note)[1]:
            if music != None:
                result = music.major_chord()
                print("Major Chord Progression for {} Major Scale: ".format(note) + ' '.join(result))
            else:
                self.Study_Music_Theory()
        else:
            self.Study_Music()

    def chords_in_major_scale(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Notes in Major Scale')
        note = self.__valid_input('Note')
        music = Music(note)
        if music.valid_note(note)[1]:
            if music != None:
                result = music.chords_in_major_scale()
                print("Notes in {} Major Scale: ".format(note) + ' '.join(result))
            else:
                self.Study_Music_Theory()
        else:
            self.Study_Music()

    def note_in_major_scales(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Note in Major Scales')
        note = self.__valid_input('Note')
        music = Music(note)
        if music.valid_note(note)[1]:
            if music != None:
                result = music.note_in_major_scales()
                print("{} Major Note is present in Scales: {}".format(note, ' '.join(result)))
            else:
                self.Study_Music_Theory()
        else:
            self.Study_Music()

    def note_shift_with_capo_position(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Note in Major Scales')
        note = self.__valid_input('Note')
        music = Music(note)
        if music.valid_note(note)[1]:
            if music != None:
                capo_position = int(self.__valid_input('Capo on Fret Number'))
                result = music.capo_pos_note_shift(capo_position)
                print("Result Note for {} with Capo at {}: {}".format(note, capo_position, result))
            else:
                self.Study_Music_Theory()
        else:
            self.Study_Music()

    def scale_shift_with_capo_position(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Scale shift with capo position')
        note = self.__valid_input('Original Scale')
        music = Music(note)
        if music.valid_note(note)[1]:
            if music != None:
                capo_position = int(self.__valid_input('Capo on Fret Number'))
                new_note = music.capo_pos_note_shift(capo_position)
                result = music.capo_pos_scale_shift(capo_position)
                print("Result Scale for {} with Capo at {}: {}".format(note, capo_position, new_note))
                print("Notes: " + ' '.join(result))
            else:
                self.Study_Music_Theory()
        else:
            self.Study_Music()

    def minor_scale(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Minor Scale')
        note = self.__valid_input('Note')
        music = Music(note)
        if music.valid_note(note)[1]:
            if music != None:
                result = music.minor_scale()
                print("Notes for {} Minor Scale: ".format(note) + ' '.join(result))
            else:
                self.Study_Music_Theory()
        else:
            self.Study_Music()

    def minor_chord(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Minor Chord')
        note = self.__valid_input('Note')
        music = Music(note)
        if music.valid_note(note)[1]:
            if music != None:
                result = music.minor_chord()
                print("{} Minor Chord Progression: ".format(note) + ' '.join(result))
            else:
                self.Study_Music_Theory()
        else:
            self.Study_Music()

    def chords_in_minor_scale(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Notes in Minor Scale')
        note = self.__valid_input('Note')
        music = Music(note)
        if music.valid_note(note)[1]:
            if music != None:
                result = music.chords_in_minor_scale()
                print("Notes in {} Minor Scale: ".format(note) + ' '.join(result))
            else:
                self.Study_Music_Theory()
        else:
            self.Study_Music()
    
    def relative_minor_major(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Relative Minor / Major')
        scl = input('1. Relative Major\n2. Relative Minor\nChoice: ')
        if int(scl) == 1:
            note = self.__valid_input('Minor Note')
            music = Music(note)
            if music.valid_note(note)[1]:
                if music != None:
                    result = music.relative_major(note)
                    print("Relative Major of {}m is: {}".format(note, result))
                else:
                    self.Study_Music_Theory()
            else:
                self.Study_Music()
        elif int(scl) == 2:
            note = self.__valid_input('Minor Note')
            music = Music(note)
            if music.valid_note(note)[1]:
                if music != None:
                    result = music.relative_minor(note)
                    print("Relative Minor of {} is: {}".format(note, result))
                else:
                    self.Study_Music_Theory()
            else:
                self.Study_Music()
    
    def play_tone(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Play Tone Based on Note')
        note = self.__valid_input('Note')
        music = Music(note)
        if music.valid_note(note)[1]:
            if music != None:
                music.note_beep(note)
            else:
                self.Study_Music_Theory()
        else:
            self.Study_Music()
    
    def play_tone_in_seq(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Play Tone in Sequence')
        ch = input('1. Play Notes in a Scale\n2. Play Note Sequence\nChoice: ')
        if int(ch) == 1:
            min_maj = input("1. Minor Scale\n2. Major Scale\nChoice: ")
            if int(min_maj) == 1:
                scale = self.__valid_input('Scale')
                music = Music(scale)
                if music.valid_note(scale)[1]:
                    if music != None:
                        music.note_beep_scale('m', scale)
                    else:
                        self.Study_Music_Theory()
                else:
                    self.Study_Music()
            elif int(min_maj) == 2:
                scale = self.__valid_input('Scale')
                music = Music(scale)
                if music.valid_note(scale)[1]:
                    if music != None:
                        music.note_beep_scale('M', scale)
                    else:
                        self.Study_Music_Theory()
                else:
                    self.Study_Music()
        elif int(ch) == 2:
            notes = self.__valid_input('Notes')
            music = Music()
            music.note_beep_seq(notes.split())
    
    def scale_from_chords(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Scale from Chords')
        # Find Scale from chords and use in best_capo_position() for up-shifting / down-shifting
        chords = self.__valid_input('Chords: ')
        music = Music()
        common_scale = music.common_scale_from_chords(chords.split())
        result = common_scale[0]
        if common_scale[1] is '' or common_scale[1] == 'NR':
            if len(result) > 0:
                print("'{}' Chords are present in '{}' Scale".format(chords, result))
            else:
                print("'{}' Chords does not share common scale... Please Check the chords Once...".format(chords))
        else:
            print("'{}' Chords are present in '{}' Scale or '{}' Scale".format(chords, result[0], result[1]))
    
    def scale_from_notes(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Scale from Notes')
        # Find Scale from notes and use in best_capo_position() for up-shifting / down-shifting
        notes = self.__valid_input('Notes: ')
        music = Music()
        common_scale = music.common_scale_from_notes(notes.split())
        result = common_scale[0]
        if len(result) > 0:
            if common_scale[1] is '' or common_scale[1] == 'NR':
                print("'{}' Notes are present in '{}' & '{}' Scales".format(notes, result[0], result[1]))
            elif common_scale[1] == 'R':
                print("'{}' Notes are present in '{}' Scale or '{}' Scale".format(notes, result[0], result[1]))
        else:
            print("'{}' Notes does not share common scale... Please Check the Notes Once...".format(notes))
    
    def best_capo_position(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('Best Capo position for easy play')
        self.__talk('Sorry Feature Coming soon')
        print('Sorry Feature Coming soon...')

    def wrong_entry(self, wob):
        wob.set_wrong_flag(True)
        print('Wrong Entry!\nTry Again...\n')

    def Study_Music_Theory(self):
        self.__talk('Go and study basic music theory first')
        print('Go and study basic music theory first!!!')
        exit()
    
    def Study_Music(self):
        self.__talk('Invalid Music Notation!')
        print('Invalid Music Notation!\nI am not here to teach you MUSIC but Guide!')
 
    def notes_in_audio(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Detect Notes in a Audio file')
        audio_file = input('Enter the path for audio file: ')
        music = Music()
        print('Notes in your audio file: {}'.format(music.audio_note_detect(audio_file)))
    
    def play_audio(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Play Audio from a file')
        audio_file = input('Enter the path for audio file: ')
        music = Music()
        print('Playing Audio...')
        music.play_audio_file(audio_file)
    
    def record_play(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Record and Playback')
        music = Music()
        duration = int(input('Enter the duration of recording (in sec): '))
        print('Record your audio after this beep...')
        sleep(2)
        music.freq_beep(1047)
        sleep(.3)
        print('Listening...')
        music.record_and_playback(duration=duration)
        print('Playing Audio...')
    
    def record_save(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Record and Save')
        music = Music()
        duration = int(input('Enter the duration of recording (in sec): '))
        output_file = input('Enter Output File Name: ') # recordedFile
        output_file = 'assets\\' + output_file + '.wav'
        print('Record your audio after this beep...')
        sleep(2)
        music.freq_beep(1047)
        sleep(.3)
        print('Listening...')
        music.record_and_save(duration=duration, output_file=output_file)
        print('{} file saved successfully...'.format(output_file))

    def play_mp3(self, wob):
        wob.set_wrong_flag(False)
        self.__talk('You chose Play MP3 Audio')
        audio_dir = input('Enter the path for mp3 audio file: ') + '\\'
        mp3_audio_file = input('Enter the name of mp3 audio file: ') + '.mp3'
        music = Music()
        print('Playing Audio...')
        music.play_mp3(audio_dir, mp3_audio_file)

    def va(self, wob):
        wob.set_wrong_flag(False)
        music = Music()
        return music.voice_assist()
