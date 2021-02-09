#!/usr/bin/env python3

from time import sleep

# ----- MINGUS ----- #
# mingus.core
import mingus.core.notes as M_notes
import mingus.core.chords as M_chords
import mingus.core.intervals as M_intervals
import mingus.core.chords as M_chords
import mingus.core.scales as M_scales
import mingus.core.value as M_value
import mingus.core.meter as M_meter
import mingus.core.keys as M_keys
import mingus.core.progressions as M_progressions

# mingus.containers
from mingus.containers import Note as M_Note, NoteContainer as M_NoteContainer, Bar as M_Bar, Composition as M_Composition, Suite as M_Suite
from mingus.containers.instrument import Instrument as M_Instrument, Piano as M_Piano, Guitar as M_Guitar, MidiInstrument as M_MidiInstrument, MidiPercussionInstrument as M_MidiPercussionInstrument
from mingus.containers.track import Track as M_Track

# mingus.midi
# from mingus.midi import fluidsynth
from mingus.midi import midi_events as M_midi_events, midi_file_in as M_midi_file_in, midi_file_out as M_midi_file_out, midi_track as M_midi_track, Sequencer as M_Sequencer, SequencerObserver as M_SequencerObserver
from mingus.midi.sequencer import Sequencer as M_Sequencer

# mingus.extra
import mingus.extra.lilypond as M_lilypond
import mingus.extra.tunings as M_tunings
import mingus.extra.tablature as M_tablature
import mingus.extra.fft as M_fft
# ----- MINGUS ----- #

import os
import sys
import platform
if platform.system() == 'Linux':
    from Note_Tone import Note_Tone
    from Audio_Processing import Audio_Process 
    from Voice_Assistant import Voice_Assistant
elif platform.system() == 'Windows':
    root_dir = os.path.realpath('')
    root_dir = '\\'.join(root_dir.split('\\')[:-1])
    sys.path.insert(0, root_dir)
    import winsound
    from Utils.Note_Tone import Note_Tone
    from Utils.Audio_Processing import Audio_Process
    from Utils.Voice_Assistant import Voice_Assistant


class _Mingus_Helper:
    def __original_notation_intact(self, note):
        if len(note) > 1:
            return note[1]
        return note

    def note_validity_chk_redundancy_remover(self, note):
        '''
        Objective: Check if note is valid or not; if so remove any redundancy from the note
        '''
        if M_notes.is_valid_note(note):
            note1 = M_notes.reduce_accidentals(M_notes.remove_redundant_accidentals(note))
            if self.__original_notation_intact(note) not in note1:
                return (note, True)
            else:
                return (note1, True)
        return (note, False)


class Music:
    def __init__(self, note='C', audio_file=''):
        '''
        Objective: Contructor for Music Class

        Description:
            1. Create object of Mingus_Helper class
            2. Create all possible Notes
            3. Open position chords (Guitar)
            4. Set note as non-redundat valid note
            5. Set formulas for different progressions
        '''
        self.__mh = _Mingus_Helper()
        self.__notesS = ['A','A#','B','C','C#','D','D#','E','F','F#','G','G#']
        self.notesS = self.__notesS
        self.__notesb = ['A','Bb','Cb','C','Db','D','Eb','Fb','F','Gb','G','Ab']
        self.notesb = self.__notesb
        self.__open_pos_chords = ['0_A','0_Am','0_B','0_Bm','0_C','0_D','0_Dm','0_E','0_Em','0_F','0_Fm','0_G']

        self.__is_valid_note = self.valid_note(note)
        if self.__is_valid_note[1]:
            self.__note = self.__is_valid_note[0]
        
        self.__tone = 2
        self.__semi_tone = 1
        self.__major = ''
        self.__minor = 'm'
        self.__diminished = 'dim'
        self.__maj_scale_formula = [self.__tone,self.__tone,self.__semi_tone,self.__tone,self.__tone,self.__tone,self.__semi_tone]
        self.__chord_prog_in_maj_scale_formula = [self.__major,self.__minor,self.__minor,self.__major,self.__major,self.__minor,self.__diminished]
        self.__min_scale_formula = [self.__tone,self.__semi_tone,self.__tone,self.__tone,self.__semi_tone,self.__tone,self.__tone]
        self.__chord_prog_in_min_scale_formula = [self.__minor,self.__minor,self.__major,self.__major+'/'+self.__minor,self.__major+'/'+self.__minor,self.__major,self.__major]
        
        self.__audio_file = audio_file
        self.__ap = Audio_Process(self.__audio_file)

        self.__voice_assist = Voice_Assistant()

        self.__tone = Note_Tone()
        self.__octave4 = self.__tone.notes(4)
        self.__octave5 = self.__tone.notes(5)

        self.__octaves = self.__octave4 + self.__octave5

        # Notes Frequency, Octave 4
        self.__C4  = self.__octave4[0]
        self.__Cs4 = self.__octave4[1]
        self.__D4  = self.__octave4[2]
        self.__Ds4 = self.__octave4[3]
        self.__E4  = self.__octave4[4]
        self.__F4  = self.__octave4[5]
        self.__Fs4 = self.__octave4[6]
        self.__G4  = self.__octave4[7]
        self.__Gs4 = self.__octave4[8]
        self.__A4  = self.__octave4[9]
        self.__As4 = self.__octave4[10]
        self.__B4  = self.__octave4[11]
    
    def linux_speech(self, text):
        '''
        Objective: Text-to-speech (LINIX)

        Description: call "spd-say '<TEXT>' "
        '''
        os.system('spd-say "{}"'.format(text))
        sleep(len(text)/10) # Wait for the speech to end; Else next speech will play before ending; if given one after another

    def __b2s(self, note):
        '''
        Objective: Convert Flat'b' note to Sharp'#' note
        '''
        return self.__notesS[self.__note_position_in_list(note)]

    def __s2b(self, note):
        '''
        Objective: Convert Sharp'#' note to Flat'b' note
        '''
        return self.__notesb[self.__note_position_in_list(note)]

    def __note_position_in_list(self, note):
        '''
        Objective: Find the position of a note in a valid_list

        Description:
            1. Check if note is valid or not
            2. if so check for list in which the valid note will fall ('#' / 'b' / '0')
            3. Find the position of the note in that list
        '''
        valid_list = self.__valid_list(note)
        return valid_list.index(note)
    
    def valid_note(self, note):
        '''
        Objective: Check if a note is valid or not using _Mingus_Helper
        '''
        is_valid_note = self.__mh.note_validity_chk_redundancy_remover(note)
        if not is_valid_note[1]:
            return (note, False)
        note = is_valid_note[0]
        return (note, True)
    
    def substr_in_list_of_strs(self, lst, substr):
        '''
        Objective: Check if a substring is present in a list of strings

        Source: https://www.geeksforgeeks.org/python-finding-strings-with-given-substring-in-list/
        '''
        res_lst_of_strs_with_substr = list(filter(lambda x: substr in x, lst))
        return bool(res_lst_of_strs_with_substr)

    def __valid_list(self, note):
        '''
        Objective: Return a valid list w.r.t a valid note

        Description:
            1. Check if note is valid or not
            2. if so check for list in which the valid note will fall ('#' / 'b' / '0')
        '''
        is_valid_note = self.valid_note(note)
        if is_valid_note[1]:
            note = is_valid_note[0]
        if note in self.__notesS:
            return self.__notesS
        elif note in self.__notesb:
            return self.__notesb
        elif self.substr_in_list_of_strs(self.__open_pos_chords, '0_' + note): # Used for 'best_capo_position()'
            return self.__open_pos_chords

    def major_scale(self):
        '''
        Objective: Return the major notes in a scale

        Description: Use major_scale_formula to retrieve the notes
        '''
        valid_list = self.__valid_list(self.__note)
        position = self.__note_position_in_list(self.__note)

        notes_in_scale = [valid_list[position]]

        for i in range(6):
            position = position + self.__maj_scale_formula[i]
            if position >= len(valid_list):
                position = position % len(valid_list)
            notes_in_scale.append(valid_list[position])

        return notes_in_scale

    def __major_scale(self, note):
        '''
        Objective: Return the major notes in a scale for a passed note

        Description: Use major_scale_formula to retrieve the notes
        '''
        valid_list = self.__valid_list(note)
        position = self.__note_position_in_list(note)

        notes_in_scale = [valid_list[position]]
        
        for i in range(6):
            position = position + self.__maj_scale_formula[i]
            if position >= len(valid_list):
                position = position % len(valid_list)
            notes_in_scale.append(valid_list[position])

        return notes_in_scale

    def major_chord(self):
        '''
        Objective: Return the major chord in a scale

        Description: Use major_scale() to retrieve the notes; return 0, 2, 4 position notes
        '''
        scale = self.major_scale()
        return [scale[0], scale[2], scale[4]]

    def chords_in_major_scale(self):
        '''
        Objective: Return the chords in major scale

        Description: Use major_scale() to retrieve the notes; and attach the respective chord notation w.r.t chord_prog_in_maj_scale formula
        '''
        notes = self.major_scale()
        for i in range(len(notes)):
            notes[i] = notes[i] + self.__chord_prog_in_maj_scale_formula[i]
        return notes

    def __chords_in_major_scale(self, scale):
        '''
        Objective: Return the chords in passed major scale

        Description: Use major_scale() to retrieve the notes; and attach the respective chord notation w.r.t chord_prog_in_maj_scale formula
        '''
        notes = self.__major_scale(scale)
        for i in range(len(notes)):
            notes[i] = notes[i] + self.__chord_prog_in_maj_scale_formula[i]
        return notes

    def note_in_major_scales(self):
        '''
        Objective: Return the major scales where the note is present
        '''
        valid_list = self.__valid_list(self.__note)
        notes_scales = []
        scales = []
        for i in range(len(valid_list)):
            notes_scales.append(self.__major_scale(valid_list[i]))
        
        for i in range(len(notes_scales)):
            for j in range(len(notes_scales[0])):
                if self.__note == notes_scales[i][j]:
                    scales.append(notes_scales[i][0])
        return scales
    
    def __note_in_major_scales(self, note):
        '''
        Objective: Return the major scales where the note is present
        '''
        valid_list = self.__valid_list(note)
        notes_scales = []
        scales = []
        for i in range(len(valid_list)):
            notes_scales.append(self.__major_scale(valid_list[i]))
        
        for i in range(len(notes_scales)):
            for j in range(len(notes_scales[0])):
                if note == notes_scales[i][j]:
                    scales.append(notes_scales[i][0])
        return scales

    def minor_scale(self):
        '''
        Objective: Return the minor notes in a scale

        Description: Use minor_scale_formula to retrieve the notes
        '''
        valid_list = self.__valid_list(self.__note)
        position = self.__note_position_in_list(self.__note)

        notes_in_scale = [valid_list[position]]
        
        for i in range(6):
            position = position + self.__min_scale_formula[i]
            if position >= len(valid_list):
                position = position % len(valid_list)
            notes_in_scale.append(valid_list[position])

        return notes_in_scale

    def __minor_scale(self, note):
        '''
        Objective: Return the minor notes in a scale for a passed note

        Description: Use minor_scale_formula to retrieve the notes
        '''
        valid_list = self.__valid_list(note)
        position = self.__note_position_in_list(note)

        notes_in_scale = [valid_list[position]]
        
        for i in range(6):
            position = position + self.__min_scale_formula[i]
            if position >= len(valid_list):
                position = position % len(valid_list)
            notes_in_scale.append(valid_list[position])

        return notes_in_scale

    def minor_chord(self):
        '''
        Objective: Return the minor chord in a scale

        Description: Use minor_scale() to retrieve the notes; return 0, 2, 4 position notes
        '''
        scale = self.minor_scale()
        return [scale[0], scale[2], scale[4]]

    def chords_in_minor_scale(self):
        '''
        Objective: Return the chords in minor scale

        Description: Use minor_scale() to retrieve the notes; and attach the respective chord notation w.r.t chord_prog_in_min_scale formula
        '''
        notes = self.minor_scale()
        for i in range(len(notes)):
            if '/' in self.__chord_prog_in_min_scale_formula[i]:
                join_formula = '/' + notes[i]
                notes[i] = notes[i] + self.__chord_prog_in_min_scale_formula[i]
                parts = notes[i].split('/')
                notes[i] = join_formula.join(parts)+' '
            else:
                notes[i] = notes[i] + self.__chord_prog_in_min_scale_formula[i]
        return notes

    def __chords_in_minor_scale(self, scale):
        '''
        Objective: Return the chords in passed minor scale

        Description: Use minor_scale() to retrieve the notes; and attach the respective chord notation w.r.t chord_prog_in_min_scale formula
        '''
        notes = self.__minor_scale(scale)
        for i in range(len(notes)):
            if '/' in self.__chord_prog_in_min_scale_formula[i]:
                join_formula = '/' + notes[i]
                notes[i] = notes[i] + self.__chord_prog_in_min_scale_formula[i]
                parts = notes[i].split('/')
                notes[i] = join_formula.join(parts)+' '
            else:
                notes[i] = notes[i] + self.__chord_prog_in_min_scale_formula[i]
        return notes

    def capo_pos_note_shift(self, capo_pos = 0):
        '''
        Objective: Find new note with change in position of Capo (Guitar)
        '''
        valid_list = self.__valid_list(self.__note)
        position = 0
        for i in range(len(valid_list)):
            if valid_list[i] == self.__note:
                position = i

        new_note = valid_list[position - capo_pos]
        return new_note

    def capo_pos_scale_shift(self, capo_pos = 0):
        '''
        Objective: Find new scale with change in position of Capo (Guitar)
        '''
        new_note = self.capo_pos_note_shift(capo_pos)
        new_scale = self.__chords_in_major_scale(new_note)
        return new_scale

    '''def best_capo_position(self, chords):
        for chord in chords:
            pass'''

    def relative_minor(self, major_scale):
        '''
        Objective: Find Relative Minor Scale of given Scale
        '''
        return self.__valid_list(major_scale)[self.__note_position_in_list(major_scale) - 3] + 'm'

    def relative_major(self, minor_scale):
        '''
        Objective: Find Relative Major Scale of given Scale
        '''
        list1 = self.__valid_list(minor_scale)
        return list1[(self.__note_position_in_list(minor_scale) + 3) % len(list1)]

    def __note_freq_detection(self, note):
        '''
        Objective: Return the frequency of note in 4th Octave
        '''
        note = self.__b2s(note)
        if note == 'C':
            return self.__C4
        elif note == 'C#':
            return self.__Cs4
        elif note == 'D':
            return self.__D4
        elif note == 'D#':
            return self.__Ds4
        elif note == 'E':
            return self.__E4
        elif note == 'F':
            return self.__F4
        elif note == 'F#':
            return self.__Fs4
        elif note == 'G':
            return self.__G4
        elif note == 'G#':
            return self.__Gs4
        elif note == 'A':
            return self.__A4
        elif note == 'A#':
            return self.__As4
        elif note == 'B':
            return self.__B4

    def freq_beep(self, freq, dur=300):
        '''
        Objective: Create beep tone based on OS w.r.t passed frequency and duration
        '''
        if platform.system() == 'Windows':
            winsound.Beep(freq, dur)
        elif platform.system() == 'Linux':
            os.system('play -nq -t alsa synth {} sine {}'.format(dur/1000, freq))
    
    def note_beep(self, note, dur=300):
        '''
        Objective: Create beep tone based on OS w.r.t passed note
        '''
        freq = self.__note_freq_detection(note)
        self.freq_beep(freq, dur)
    
    def note_beep_seq(self, notes):
        '''
        Objective: Create beep tone based on OS w.r.t passed note sequence
        '''
        # Play notes from same octave(4)
        for note in notes:
            self.note_beep(note)
            sleep(0.5)

    def note_beep_scale(self, scale_mode, scale):
        '''
        Objective: Create beep tone based on OS w.r.t (major / minor) notes of passed Scale
        '''
        # Play notes using 2 octaves(4, 5)
        if scale_mode == 'm':
            notes = self.__minor_scale(self.__s2b(scale))
        elif scale_mode == 'M':
            notes = self.__major_scale(self.__b2s(scale))

        note_octave_pos = self.__octaves.index(self.__note_freq_detection(notes[0]))
        scale_freq_range = self.__octaves[note_octave_pos : note_octave_pos + 13]

        position = 0
        scale_freq = [scale_freq_range[position]]
    
        for i in range(6):
            position = position + self.__maj_scale_formula[i]
            scale_freq.append(scale_freq_range[position])
        
        scale_freq.append(scale_freq_range[position + 1]) # Adding 8th Note from Next Octave for that Scale
        
        for freq in scale_freq:
            self.freq_beep(freq)
            sleep(0.5)

    def __chord_in_scales(self, chord):
        '''
        Objective: Find Major / Minor Scale(s) with given Chord
        '''
        # Major and Minor Scales containing Chords
        if 'm' in chord and 'dim' not in chord:
            note = chord[:-1]
        else:
            note = chord
        
        valid_list = self.__valid_list(note)
        
        # Major Scales with this chord
        notes_scales = dict()
        major_scales_with_chord = []
        for i in range(len(valid_list)):
            notes_scales[valid_list[i]] = self.__chords_in_major_scale(valid_list[i])

        for k,v in notes_scales.items():
            if chord in v:
                major_scales_with_chord.append(k)
        
        # Minor Scales with this chord
        notes_scales = dict()
        minor_scales_with_chord = []
        for i in range(len(valid_list)):
            min_scale1 = min_scale = self.__chords_in_minor_scale(valid_list[i])
            for scale in min_scale:
                if '/' in scale:
                    min_scale1.remove(scale)
                    min_scale1.extend(scale.split('/'))
            notes_scales[valid_list[i] + 'm'] = min_scale1
        
        for k,v in notes_scales.items():
            if chord in v:
                minor_scales_with_chord.append(k)
        
        scales = major_scales_with_chord + minor_scales_with_chord
        return scales
    
    def common_scale_from_chords(self, chords):
        '''
        Objective: Find Major / Minor Scale(s) with the given Chords
        '''
        scales_from_chords = []
        for chord in chords:
            scales_from_chords.append(self.__chord_in_scales(chord))
        list_of_sets = []
        for scale in scales_from_chords:
            list_of_sets.append(set(scale))
        result = list_of_sets[0]
        if len(list_of_sets) > 2:
            for i in range(1, len(list_of_sets)):
                result = result.intersection(list_of_sets[i])
        result = list(result)
        if len(result) == 2:
            minor_note_in_result = [item for item in result if 'm' in item][0]
            minor_note_index = result.index(minor_note_in_result)
            major_note_index = minor_note_index - 1
            if self.relative_minor(result[major_note_index]) == result[minor_note_index] and self.relative_major(result[minor_note_index][:-1]) == result[major_note_index]:
                return (result, 'R')
            else:
                return (result, 'NR')
        else:
            return (result, '')
        
    def common_scale_from_notes(self, notes):
        '''
        Objective: Find Major / Minor Scale(s) with the given Notes
        '''
        scales_from_notes = []
        for note in notes:
            scales_from_notes.append(self.__note_in_major_scales(note))
        list_of_sets = []
        for scale in scales_from_notes:
            list_of_sets.append(set(scale))
        result = list_of_sets[0]
        if len(list_of_sets) > 2:
            for i in range(1, len(list_of_sets)):
                result = result.intersection(list_of_sets[i])
        result = list(result)
        if len(result) == 2:
            print(result)
            minor_note_in_result = [item for item in result if 'm' in item]
            if minor_note_in_result:
                minor_note_in_result = minor_note_in_result[0]
                minor_note_index = result.index(minor_note_in_result)
                major_note_index = minor_note_index - 1
                if self.relative_minor(result[major_note_index]) == result[minor_note_index] and self.relative_major(result[minor_note_index][:-1]) == result[major_note_index]:
                    return (result, 'R')
                else:
                    return (result, 'NR')
        return (result, '')

    def audio_note_detect(self, audio_file):
        if audio_file:
            self.__audio_file = audio_file
        notes_from_audio = self.__ap.detect_notes_from_audio(self.__audio_file)
        return notes_from_audio

    def play_audio_file(self, audio_file):
        if audio_file:
            self.__audio_file = audio_file
        self.__ap.play_audio(audio_file=self.__audio_file)
    
    def record_and_playback(self, duration=3):
        my_recording = self.__ap.record(duration=duration)
        self.__ap.play_audio(my_recording)
    
    def record_and_save(self, duration=3, output_file=''):
        self.__ap.record_and_save_to_file(duration, output_file)

    def play_mp3(self, music_dir, mp3_audio_file):
        if mp3_audio_file:
            self.__audio_file = mp3_audio_file
        self.__ap.play_mp3(music_dir, self.__audio_file)

    def voice_assist(self):
        '''
        Start Voice Assistant
        '''
        return self.__voice_assist.start_AI_engine()
