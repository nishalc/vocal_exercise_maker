from functions import *

#inputs
note_folder = 'Notes'
chord_folder = 'Chords'

#INPUTS IN THE CONTROL PANEL WHICH GET COMPACTED
start_note = 'G'
start_octave = 2
end_note = 'A'
end_octave = 4

click_track = True
reverse_bin = False #default = true
ascend_bin = True
chords_bin = True

duration_multiplier = 1
note_steps = 1

tempo = 110

pattern = '1358888531'

#pattern =   [1,1,2,3,3,4,5,5,6,7,6,7,8,9,9,8,7,7,6,5,5,4,3,2,1,0,1]
#durations = [2,1,1,2,1,1,2,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,2] # will default to 1's for the length of pattern
#durations = [i/2 for i in durations]
durations = [1,1,1,1,1,1,1,1,2,2,2]

scale_type = 'M'

filename = 'Goog'

bin_d = {'click_track':click_track, 'reverse_bin':reverse_bin, 'ascend_bin':ascend_bin, 'chords_bin':chords_bin,
         'note_steps':note_steps}
start_note_tup = (start_note, start_octave)
end_note_tup = (end_note, end_octave)

my_ex = VocalExercise(note_folder, chord_folder, start_note_tup, end_note_tup, tempo, pattern, durations, scale_type
                      , bin_d, filename, duration_multiplier)
my_ex.generate()
my_ex.export()
my_ex.play_track()