# vocal_exercise_generator
This is a Python program which allows you to generate and customize vocal training exercises. If you have any questions, queries or bugs please let me know!

LICENSE INFO: Currently I've not set a license on this code, you're free to use the code of course :)

Please checkout the video at https://www.youtube.com/watch?v=tT5YHAJirp0 for a walkthrough and demo.

![ui](https://user-images.githubusercontent.com/48350767/84436026-b09e7500-ac2a-11ea-9de4-04bc854f7114.png)

You can run the program using the vocal_exercise_maker.exe or the script 'main.py' if you have Python installed (in which case you need the modules: 'Pydub', 'simpleaudio' and 'pysimplegui')

## Step by Step instructions
1. Select your note range, these will the highest and lowest notes that appear in the track - not necessarily the starting and end notes
2. Pick a scale and pattern, there are a bunch of presets, or you can select your own - just make sure to check 'custom'. The numbers represent the position in the scale, 1 3 5 is the 1st, 3rd, and 5th (presuming you have the major scale selected). 
3. Choose durations, here 1 means 1 quarter note at your selected tempo. By default the program chooses 1 for the whole pattern, make sure your durations match the number of notes in the pattern if you want to use varying durations. If you want to have every note the same duration, feel free to leave this as default and use the multiplier. The multiplier multiplies all note durations by it´s designated number, e.g 0.5 will make all notes eight beats.  
4. Select extra options:
- Repeat and reverse means upon reaching the last note it will return back to the first in reverse.
- Pause between is adding an extra pause between each pattern, useful if you have disabled the chords in track. 
5. Controls : you can export the parameters using Export .json, this can then be read by the program to preselect all your parameters. Use play to test your exercise and make sure you are happy! Export .wav and .json will produce both the audio file and a parameter file in the OUTPUT folder. 

## What each button does

* Play: will play the current settings for you to hear before you export, creates a temporary file to play
* Import .json: you can export the "recipe" for a vocal exercise as a .json, this import function lets you read in the parameters from a prior .json
* Export .json, export the current settings selected on the program to a .json, the name is automatically generated
* Export .wav and .json, will produce the current settings as a .wav and .json with the same name - use when you are happy with your file

## Notes / Fun Facts
1. The notes are limited to 8 seconds, so any single note within a pattern cannot be longer than this (just repeat it if you really want it).
2. You can go BACKWARDS into the previous octave and forward into the next octave on a scale pattern. Eg 0 will be a step down from 1, 9 is the 2nd on the octave above. 

## Future ideas / thoughts
1. Currently files are quite big as I need to use .wav files, in the future it may be possible to use .mp3, but only if the program is made on a different platform perhaps
2. Eventually, if there is interest I would like to make this into a webpage, but this is a far away idea. 

