import os
import pydub
import winsound
import math

#####################           VOCAL EXERCISE CLASS FUNCTIONS                ########################################
#######################################################################################################################

# turns a note and number tuple into an index, assuming 0 = C2, 1 = D2 etc
def note_to_number(note):
    pitch = note[0]
    octave = note[1]
    add_on = (int(octave) - 2) * 12
    notes = ['C', 'C# / Db', 'D', 'D# / Eb', 'E', 'F', 'F# / Gb', 'G', 'G# / Ab', 'A', 'A# / Bb', 'B']
    return notes.index(pitch) + add_on  # returns the 0 indexed number!

# gives you the set of filepaths which are needed, based on required start and end notes
def note_chord_paths(start_note, end_note):
    start_index = note_to_number(start_note)
    end_index = note_to_number(end_note)
    if end_index <= start_index:
        print('Selected end note which is before start note, fool!')
        return 0
    elif start_note[1] < 2:
        print('Start note too low!')
        return 0
    elif (end_note[0] != 'C' and end_note[1] > 5):
        print('End note too high!')
        return 0
    notes = []
    chords = []
    for root, directory, files in os.walk("resources/Notes"):
        for file in files:
            notes.append(os.path.join(root, file))
    for root, directory, files in os.walk("resources/Chords"):
        for file in files:
            chords.append(os.path.join(root, file))
    notes.sort()
    chords.sort()
    notes = notes[start_index:end_index + 1]
    chords = chords[start_index:end_index + 1]
    return notes, chords

# take the total number of notes you have and a pattern and returns index values in list of lists.
# Each inner list is a sequence of notes
def pattern_to_lists(length, pattern, reverse_bin, ascend_bin, scale_type, note_steps):
    #translate number in a scale to semitone number
    scale_dict = {
        'Major': {-7: -14, -6: -12 ,-5: -10 ,-4: -8,-3: -7, -2: -5 , -1: -3, 0: -1, 1: 0, 2: 2, 3: 4, 4: 5, 5: 7,
                6: 9, 7: 11, 8: 12, 9: 14, 10: 16, 11: 17, 12: 19, 13: 21, 14: 23, 15: 24, 16:26, 17:28, 18:29,
                19:31, 20:33, 21:35, 22:36},
        'minor': {-6: -12, -5: -10, -4: -7, -3: -7, -2: -5, -1: -4, 0: -2, 1: 0, 2: 2, 3: 3, 4: 5,
                5: 7, 6: 8, 7: 10, 8: 12, 9: 14, 10: 15, 11: 17, 12: 19, 13: 20, 14: 22, 15: 24,
                16:26, 17:27, 18:29, 19:31, 20:32, 21:34, 22:36},
        'Major Pentatonic': {-5:-14, -4:-12 ,-3:-10, -2:-8 ,-1:-5 ,0: -3,1: 0, 2: 2, 3: 4, 4: 7, 5: 9, 6: 12,
                                 7:14, 8:16, 9:19, 10:21, 11:24},
       'minor Pentatonic': {
            -5: -14, -4: -12, -3: -9, -2: -7, -1: -5, 0: -2, 
            1: 0, 2: 3, 3: 5, 4: 7, 5: 10, 6: 12, 
            7: 15, 8: 17, 9: 19, 10: 22, 11: 24
        }
        }
    pattern = [scale_dict[scale_type][int(i)] for i in pattern] #

    chord_ints =  [j for j in range(length)][::note_steps]
    while True in [i < 0 for i in pattern]: #if notes in previous octave selected, then first chord needs to change
        pattern = [i+1 for i in pattern]
        chord_ints = [m + 1 for m in chord_ints]

    max_note = max(int(i) + 1 for i in pattern)  # for stop condition
    instructions = []
    for i in range(length)[::note_steps]:
        if i > length - max_note: # reached highest note requested
            chord_ints = chord_ints[:len(instructions)]  # needed incase you are descending only
            if ascend_bin == False:
                instructions = instructions[::-1]
                chord_ints = chord_ints[::-1]
            if reverse_bin == True:
                instructions = instructions + instructions[::-1]
                chord_ints = chord_ints + chord_ints[::-1]
                break
            else:
                break
        else:
            instructions.append([k + i for k in pattern])
    return instructions, chord_ints


# %%
class VocalExercise():
    def __init__(self, start_note_tup, end_note_tup, tempo, pattern, durations, scale_type,
                 bin_d, filename, duration_multiplier):
        max_duration = 8000
        self.bin_d = bin_d

        # loading in the audio files needed
        note_paths, chord_paths = note_chord_paths(start_note_tup, end_note_tup)
        self.notes = [pydub.AudioSegment.from_wav(i) for i in note_paths]
        self.chords = [pydub.AudioSegment.from_wav(j) for j in chord_paths]
        self.silence = pydub.AudioSegment.from_wav("resources/silence.wav")
        self.click = pydub.AudioSegment.from_wav("resources/click.wav")


        # check if durations string provided is sufficient, use default if not
        if len(durations) != len(pattern):
            durations = [1 * duration_multiplier for i in pattern]
        else:
            if duration_multiplier != 1:
                durations = [float(i) * duration_multiplier for i in durations]

        self.total_pattern_duration = sum(float(i) for i in durations)

        # check maximum note duration in selected durations
        self.beat_duration = ((60 / tempo) * 1000)
        max_note = float(max(durations)) * self.beat_duration
        if (self.beat_duration > max_duration) or (max_note > max_duration):
            print(f'you have exceed the max note duration of {max_duration}ms')
        self.durations_ms = [self.beat_duration * float(i) for i in durations]

        # generate the patterns, which select notes by index, and chord ints, which select chords by index
        self.patterns, self.chord_ints = pattern_to_lists(len(self.notes), pattern, self.bin_d['reverse_bin']
                                                          , self.bin_d['ascend_bin'], scale_type,
                                                          self.bin_d['note_steps'])

        # assigning a name to the final track
        start_str = start_note_tup[0] + str(start_note_tup[1])
        end_str = end_note_tup[0] + str(end_note_tup[1])
        pattern_str = ''.join([str(i) for i in pattern])
        if filename == "":
            filename_ = ""
        else:
            filename_ = filename + "_" 
        if self.bin_d["ascend_bin"]:
            self.name = filename_ + pattern_str + "_" + scale_type + '_' + start_str + '-' + end_str + '_' \
                        + str(tempo) + 'bpm.wav'
        else:
            self.name = filename_ + pattern_str + "_" + scale_type + '_' + end_str + '-' + start_str + '_' \
                        + str(tempo) + 'bpm.wav'


    def generate(self):
        exercise = self.click[:self.beat_duration] * 4  # start track with 4 clicks
        cbin = self.bin_d['chords_bin']
        x = 0
        for i, sequence in zip(self.chord_ints, self.patterns):
            exercise += (self.chords[i][:self.beat_duration] * cbin)
            if x == 0: # so that no weird pause for tracks without chords on the first pass only
                exercise += (self.silence[:self.beat_duration] * cbin)
            else:
                exercise += (self.silence[:self.beat_duration] * cbin)
                if cbin == 0:
                    exercise += (self.silence[:self.beat_duration] * self.bin_d['pause_bin'])

            for j, duration in zip(sequence, self.durations_ms):
                exercise += self.notes[j][:duration]
            
            # extra silence to match up beats
            beat_gap = math.ceil(self.total_pattern_duration) - self.total_pattern_duration 
            if beat_gap != 0:
                exercise += (self.silence[:self.beat_duration * beat_gap])
        
            if i != (len(self.chord_ints) - 1):  # if this isn't the last iteration
                exercise += (self.chords[i][:self.beat_duration] * cbin)
            x+=1

        if self.bin_d['click_track']:
            exercise = exercise.overlay(self.click[:self.beat_duration], loop=True)

        self.exercise = exercise
        print('Exercise generated!')

    def export(self, folder):
        self.exercise.export(folder+self.name, format='wav')

    def play_track(self):
        self.exercise.export('temp_to_play.wav', format='wav')
        winsound.PlaySound('temp_to_play.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)

    def stop_track(self):
        winsound.PlaySound(None, winsound.SND_PURGE)
