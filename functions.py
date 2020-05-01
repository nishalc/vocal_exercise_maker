import os
import pydub
from pydub.playback import play

# turns a note and number tuple into an index, assuming 0 = C2, 1 = D2 etc
def note_to_number(note):
    pitch = note[0]
    octave = note[1]
    add_on = (octave - 2) * 12
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return notes.index(pitch) + add_on  # returns the 0 indexed number!

# gives you the set of filepaths which are needed, based on required start and end notes
def note_chord_paths(note_folder, chord_folder, start_note, end_note):
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
    for root, directory, files in os.walk(note_folder):
        for file in files:
            notes.append(os.path.join(root, file))
    for root, directory, files in os.walk(chord_folder):
        for file in files:
            chords.append(os.path.join(root, file))
    notes = notes[start_index:end_index + 1]
    chords = chords[start_index:end_index + 1]
    return notes, chords


# take the total number of notes you have and a pattern and returns index values in list of lists.
# Each inner list is a sequence of notes
def pattern_to_lists(length, pattern, reverse_bin, ascend_bin, scale_type, note_steps):
    #translate number in a scale to number out of the 12 notes in each octave (including octave before and after)
    scale_dict = {'M': {-7: -14, -6: -12 ,-5: -10 ,-4: -8,-3: -7, -2: -5 , -1: -3, 0: -1, 1: 0, 2: 2, 3: 4, 4: 5, 5: 7,
                        6: 9, 7: 11, 8: 12, 9: 14, 10: 16, 11: 17, 12: 19, 13: 21, 14: 23, 15: 24},
                  'P': {1: 0, 2: 2, 3: 4, 4: 7, 5: 9}}
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
    def __init__(self, note_folder, chord_folder, start_note_tup, end_note_tup, tempo, pattern, durations, scale_type,
                 bin_d, filename, duration_multiplier):
        max_duration = 8000
        self.bin_d = bin_d

        # loading in the audio files needed
        note_paths, chord_paths = note_chord_paths(note_folder, chord_folder, start_note_tup, end_note_tup)
        self.notes = [pydub.AudioSegment.from_wav(i) for i in note_paths]
        self.chords = [pydub.AudioSegment.from_wav(j) for j in chord_paths]
        self.silence = pydub.AudioSegment.from_wav("silence.wav")
        self.click = pydub.AudioSegment.from_wav("click.wav")

        # check if durations string provided is sufficient, use default if not
        if len(durations) != len(pattern):
            durations = [1 for i in pattern]
        else:
            if duration_multiplier != 1:
                durations = [i * duration_multiplier for i in durations]

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
        self.name = filename + '_' + pattern_str + scale_type + '_' + start_str + '-' + end_str + '_' \
                    + str(tempo) + 'bpm.wav'

    def generate(self):
        exercise = self.click[:self.beat_duration] * 4  # start track with 4 clicks
        cbin = self.bin_d['chords_bin']
        x = 0
        for i, sequence in zip(self.chord_ints, self.patterns):
            exercise += (self.chords[i][:self.beat_duration] * cbin)
            if x == 0: # so that no weird pause for tracks without chords
                exercise += (self.silence[:self.beat_duration] * cbin)
            else:
                exercise += (self.silence[:self.beat_duration])

            for j, duration in zip(sequence, self.durations_ms):
                exercise += self.notes[j][:duration]
            if i != (len(self.chord_ints) - 1):  # if this isn't the last iteration
                exercise += (self.chords[i][:self.beat_duration] * cbin)
            x+=1
        if self.bin_d['click_track']:
            exercise = exercise.overlay(self.click[:self.beat_duration], loop=True)

        self.exercise = exercise
        print('Exercise generated!')

    def export(self):
        self.exercise.export(self.name, format='wav')

    def play_track(self):
        play(self.exercise)
