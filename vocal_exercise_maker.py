import PySimpleGUI as sg
import json
import os
import pydub
import simpleaudio as sa

#####################           VOCAL EXERCISE CLASS FUNCTIONS                ########################################
#######################################################################################################################

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
    #translate number in a scale to semitone number
    scale_dict = {'Major': {-7: -14, -6: -12 ,-5: -10 ,-4: -8,-3: -7, -2: -5 , -1: -3, 0: -1, 1: 0, 2: 2, 3: 4, 4: 5, 5: 7,
                        6: 9, 7: 11, 8: 12, 9: 14, 10: 16, 11: 17, 12: 19, 13: 21, 14: 23, 15: 24, 16:26, 17:28, 18:29,
                            19:31, 20:33, 21:35, 22:36},
                  'minor': {-6: -12, -5: -10, -4: -7, -3: -7, -2: -5, -1: -4, 0: -2, 1: 0, 2: 2, 3: 3, 4: 5,
                            5: 7, 6: 8, 7: 10, 8: 12, 9: 14, 10: 15, 11: 17, 12: 19, 13: 20, 14: 22, 15: 24,
                            16:26, 17:27, 18:29, 19:31, 20:32, 21:34, 22:36},
                  'Pentatonic': {-5:-14, -4:-12 ,-3:-10, -2:-8 ,-1:-5 ,0: -3,1: 0, 2: 2, 3: 4, 4: 7, 5: 9, 6: 12,
                                 7:14, 8:16, 9:19, 10:21, 11:24}}
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
            durations = [1 * duration_multiplier for i in pattern]
        else:
            if duration_multiplier != 1:
                durations = [float(i) * duration_multiplier for i in durations]

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
            if x == 0: # so that no weird pause for tracks without chords on the first pass only
                exercise += (self.silence[:self.beat_duration] * cbin)
            else:
                exercise += (self.silence[:self.beat_duration] * cbin)
                if cbin == 0:
                    exercise += (self.silence[:self.beat_duration] * self.bin_d['pause_bin'])

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
        self.exercise.export(self.name, format='wav')
        wav_obj = sa.WaveObject.from_wave_file(self.name)
        play_obj = wav_obj.play()
        self.play_obj = play_obj
        #play_obj.wait_done()

    def stop_track(self):
        self.play_obj.stop()


   #######################           FUNCTIONS FOR UI         #####################################
#######################################################################################################################

def intialize_exercise(values):
    bin_d = {'click_track': values['click_track'], 'reverse_bin': values['reverse_bin'],
             'ascend_bin': values['ascend_bin'], 'chords_bin': values['chords_bin'],
             'note_steps': int(values['note_steps']), 'pause_bin':values['pause_bin']}
    start_note_tup = (values['start_note'], values['start_octave'])
    end_note_tup = (values['end_note'], values['end_octave'])
    tempo = int(values['tempo'])
    if values['preset_pat_bin'] == True:
        pattern = values['preset_pat'].split(',')
    else:
        pattern = values['custom_pat'].split(',')
    durations = values['durations'].split(',')
    scale_type = values['scale_type']
    filename = values['filename']
    duration_multiplier = float(values['duration_multiplier'])
    my_ex = VocalExercise('Notes', 'Chords', start_note_tup, end_note_tup, tempo, pattern, durations, scale_type,
                          bin_d, filename, duration_multiplier)
    my_ex.generate()
    return my_ex, my_ex.name.split('.')[0]

def update_window(window, values):
    window['start_note'].update(values['start_note'])
    window['start_octave'].update(values['start_octave'])
    window['scale_type'].update(values['scale_type'])
    window['end_note'].update(values['end_note'])
    window['end_octave'].update(values['end_octave'])
    window['tempo'].update(values['tempo'])
    window['filename'].update(values['filename'])
    window['preset_pat'].update(values['preset_pat'])
    window['preset_pat_bin'].update(values['preset_pat_bin'])
    window['custom_pat_bin'].update(values['custom_pat_bin'])
    window['custom_pat'].update(values['custom_pat'])
    window['click_track'].update(values['click_track'])
    window['chords_bin'].update(values['chords_bin'])
    window['reverse_bin'].update(values['reverse_bin'])
    window['pause_bin'].update(values['pause_bin'])
    window['note_steps'].update(values['note_steps'])
    window['ascend_bin'].update(values['ascend_bin'])
    window['durations'].update(values['durations'])
    window['duration_multiplier'].update(values['duration_multiplier'])

#Inputs for dropdown menus etc
sg.theme('DarkBlue1')
scales = ('Major', 'Pentatonic', 'minor')
notes = ('A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#')
octaves = (2,3,4,5)
scale_pats = ('1,2,3,2,1', '1,2,3,4,5,4,3,2,1', '5,4,3,2,1', '1,3,5,8,5,3,1', '1,2,3,4,5,6,7,8,9,8,7,6,5,4,3,2,1')

#Rows within the layout
lowest = [sg.Text('Lowest note: '), sg.Drop(notes, default_value='C', size=(3,12),  key='start_note'),
          sg.Text('Octave:'), sg.Drop(octaves, size=(3,5), key='start_octave', default_value=3),
          sg.Text('Scale: '),
          sg.Drop(scales, size=(12,12), key='scale_type', default_value='Major')]
highest = [sg.Text('Highest note:'), sg.Drop(notes, default_value='C', size=(3,12),  key='end_note'),
          sg.Text('Octave:'), sg.Drop(octaves, size=(3,5), key='end_octave', default_value=4)]
tempo = [sg.Text('Tempo (bpm):  '), sg.Input(70, size=(5,5), key='tempo')
    , sg.Text(' '*8+'Filename:'), sg.Input('', size=(20,5), key='filename')]
pattern = [sg.Text('Scale pattern:  '), sg.Radio('Preset  ','radio1', default=True, key='preset_pat_bin'),
           sg.Drop(scale_pats, size=(37,12), key='preset_pat', default_value='1,2,3,2,1'),
            ]
pattern2 = [ sg.Text(' '*22), sg.Radio('Custom', 'radio1', key='custom_pat_bin'),
             sg.InputText(size=(39,20), key='custom_pat'),
            ]

durations = [sg.Text('Note durations:'), sg.InputText('1,1,1' ,size=(34,12), key='durations'),
             sg.Text('Mulitplier:'), sg.Input('1', key='duration_multiplier', size=(4,3))]

extras = [sg.Checkbox('Click track', default=True, key='click_track'), sg.Checkbox('Chords',
                                                                                   key='chords_bin', default=True)
    , sg.Checkbox('Repeat and reverse', key='reverse_bin'), sg.Checkbox('Pause between', key='pause_bin')]
extras2 =  [sg.Text('Note increment:'), sg.Input(1, size=(3,3), key='note_steps'), sg.Text(' '*6+'Note Order:')
    ,sg.Radio('Ascending', 'radio2', key='ascend_bin', default=True)
    , sg.Radio('Descending', 'radio2')]

controls = [[sg.Input(visible =False, enable_events = True, key = 'import'),
             sg.FileBrowse('Import\n.json', size=(6,3), key='import_path'), sg.Button('Export\n.json', size=(6,3))],
            [sg.Button('Export .wav\n& .json', size=(6,3)), sg.Button('Play', size=(6,3), key='play_stop')]]

# Title texts
tit_main = [sg.Text('1. Main input                                                       '
                    '', font=('Helvetica', 16, 'bold', 'underline'), text_color='darkgrey')]
tit_extra = [sg.Text('2. Extra Options                                                 '
                     '', font=('Helvetica', 16, 'bold', 'underline'), text_color='darkgrey')]
tit_controls = [sg.Text('3. Controls                                                          '
                        '', font=('Helvetica', 16, 'bold', 'underline'), text_color='darkgrey')]


def main():
    # Main layout
    column1 = sg.Col([tit_main, lowest, highest, pattern, pattern2, durations, tempo,
                      [sg.Text('', font=('Helvetica', 6))],
                      tit_extra, extras2, extras, [sg.Text('', font=('Helvetica', 6))], tit_controls,
                      [sg.Column(controls)
                          , sg.Column([[sg.Output(size=(42, 7))]])], ])

    form = sg.FlexForm('My first GUI', auto_size_text=True)
    layout = [[column1]]
    window = sg.Window('Vocal Exercise Maker v1.0', layout)

    playing = 0
    while True:
        event, values = window.read()

        if event == 'import':
            filename = values['import_path']
            with open(filename, 'r') as f:
               nvalues = json.load(f)
            update_window(window, nvalues)
            print('Import successful')
        elif event == 'Export\n.json':
            my_ex, filename = intialize_exercise(values)
            with open(filename+'.json', 'w') as fp:
                json.dump(values, fp)
            print('Exported ' + filename + '.json')
        elif event == 'Export .wav\n& .json':
            my_ex, filename = intialize_exercise(values)
            my_ex.export()
            with open(filename+'.json', 'w') as fp:
                json.dump(values, fp)
            print('Exported ' + filename + '.json and .wav')
        elif event == 'play_stop':
            if playing == 0:
                my_ex, filename = intialize_exercise(values)
                my_ex.play_track()
                playing = 1
                window['play_stop'].update('Stop')
            else:
                if playing == 1:
                    my_ex.stop_track()
                    window['play_stop'].update('Play')
                    playing = 0
                else:
                    print('No file is playing m8')
        elif event in (None, 'Close'):
            break

    window.close()

main()

