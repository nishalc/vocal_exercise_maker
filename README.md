# vocal_exercise_generator
python program to generate vocal exercises

I made this program for myself but hope it is useful to anyone looking to make vocal exericses. Drop me a line on reddit (u/nnnishal) or youtube if you have any queries. 

Please checkout the video at .... for a walkthrough and demo.

STEP BY STEP INSTRUCTIONS
1. Select your note range, these will the highest and lowest notes that appear in the track - not necessarily the starting and end notes
2. Pick a scale and pattern, there are a bunch of presets, or you can select your own - just make sure to check 'custom' 
3. Choose durations, here 1 means 1 beat at your selected tempo. By default the program chooses 1 for the whole pattern, make sure your durations match the number of notes in the pattern.
4. Select extra options. 
- Repeat and reverse means upon reaching the last note it will return back to the first in the opposite order.
- Pause between is adding an extra pause between each pattern, useful if you have disabled the chords in track. 
5. Controls : you can export the parameters using Export .json, this can then be read by the program to preselect all your parameters. Use play to test your exercise and make sure you are happy! Export .wav and .json will produce both the audio file and a parameter file. 

THINGS TO NOTE
1. The notes are limited to 8 seconds, so any single note within a pattern cannot be longer than this (just repeat it if you really want it).
2. You can go BACKWARDS and into the next octave on a scale pattern. Eg 0 will be a step down from 1, 9 is the 2nd on the octave above.

