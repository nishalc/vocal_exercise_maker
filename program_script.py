import FreeSimpleGUI as sg
import json
from vocal_exercise import *

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
    my_ex = VocalExercise(start_note_tup, end_note_tup, tempo, pattern,
                          durations, scale_type, bin_d, filename, duration_multiplier)
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
scales = ('Major', 'minor', 'Major Pentatonic', "minor Pentatonic")
notes = ('C', 'C# / Db', 'D', 'D# / Eb', 'E', 'F', 'F# / Gb', 'G', 'G# / Ab', 'A', 'A# / Bb', 'B')
octaves = (2,3,4,5,6)
scale_pats = ('1,2,3,4,5,4,3,2,1', '1,2,3,2,1', '1,3,5,3,1', '1,5,1', '1,8,1',
              '1,3,5,8,5,3,1', '1,3,5,8,8,8,8,5,3,1', 
              '5,4,3,2,1', '8,5,3,1', 
              '1,3,5,8,10,12,11,9,7,5,4,2,1', 
              '1,2,3,4,5,6,7,8,7,6,5,4,3,2,1', 
              '1,2,3,4,5,6,7,8,9,8,7,6,5,4,3,2,1')

#Rows within the layout
lowest = [sg.Text('Lowest note: '), sg.Drop(notes, default_value='C', size=(6,12),  key='start_note'),
          sg.Text('Octave:'), sg.Drop(octaves, size=(3,5), key='start_octave', default_value=2),
          sg.Text('Scale: '),
          sg.Drop(scales, size=(12,12), key='scale_type', default_value='Major')]
highest = [sg.Text('Highest note:'), sg.Drop(notes, default_value='C', size=(6,12),  key='end_note'),
          sg.Text('Octave:'), sg.Drop(octaves, size=(3,5), key='end_octave', default_value=4)]
tempo = [sg.Text('Tempo (bpm):  '), sg.Input(70, size=(5,5), key='tempo')
    , sg.Text(' '*8+'Filename:'), sg.Input('', size=(20,5), key='filename')]
pattern = [sg.Text('Scale pattern:  '), sg.Radio('Preset  ','radio1', default=True, key='preset_pat_bin'),
           sg.Drop(scale_pats, size=(37,12), key='preset_pat', default_value='1,2,3,4,5,4,3,2,1'),
            ]
pattern2 = [ sg.Text(' '*22), sg.Radio('Custom', 'radio1', key='custom_pat_bin'),
             sg.InputText(size=(39,20), key='custom_pat'),
            ]

durations = [sg.Text('Note durations:'), sg.InputText('' ,size=(34,12), key='durations'),
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
    column1 = sg.Col([tit_main, lowest, highest, pattern, pattern2, durations, tempo,
                      [sg.Text('', font=('Helvetica', 6))],
                      tit_extra, extras2, extras, [sg.Text('', font=('Helvetica', 6))], tit_controls,
                      [sg.Column(controls)
                          , sg.Column([[sg.Output(size=(42, 7))]])], ])

    layout = [[column1]]
    window = sg.Window('Vocal Exercise Maker v1.0', layout)

    playing = 0
    while True:
        event, values = window.read()
        if event == 'import':
            filename = values['import_path']
            if filename != '':
                with open(filename, 'r') as f:
                   nvalues = json.load(f)
                update_window(window, nvalues)
                print('Import successful')
                values['import_path'] = ''
            else:
                print('Import aborted')
        elif event == 'Export\n.json':
            my_ex, filename = intialize_exercise(values) # not ideal to have to initializee everytime but no other way
            with open('OUTPUT/' + filename + '.json', 'w') as fp:
                json.dump(values, fp)
            print('Exported ' + filename + '.json')
        elif event == 'Export .wav\n& .json':
            my_ex, filename = intialize_exercise(values)
            my_ex.export('OUTPUT/')
            with open('OUTPUT/' + filename+'.json', 'w') as fp:
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

#main()

