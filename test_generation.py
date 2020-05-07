from vocal_exercise_maker import *
#This file is used for debugging and general experimentation (without the gui getting in the way

note_folder = 'Notes'
chord_folder = 'Chords'

start_note = 'C'
start_octave = 2
end_note = 'C'
end_octave = 4

click_track = True
reverse_bin = False
ascend_bin = True
chords_bin = True
pause_bin = False

duration_multiplier = 1
note_steps = 1
tempo = 60
scale_type = 'Pentatonic'
filename = 'Goog'

#pattern = [1,0, -1, -2, -3, -4, -5, -6, -7]
#pattern = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
pattern = [-4,-3,-2,-1,0,1,2,3,4,5]
durations = [1,1,1,1,1,1,1,1,2,2,2]

bin_d = {'click_track':click_track, 'reverse_bin':reverse_bin, 'ascend_bin':ascend_bin, 'chords_bin':chords_bin,
         'note_steps':note_steps, 'pause_bin':pause_bin}
start_note_tup = (start_note, start_octave)
end_note_tup = (end_note, end_octave)

my_ex = VocalExercise(note_folder, chord_folder, start_note_tup, end_note_tup, tempo, pattern, durations, scale_type
                      , bin_d, filename, duration_multiplier)
my_ex.generate()
my_ex.export()
