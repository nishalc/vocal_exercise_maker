import PyInstaller.__main__
import shutil

PyInstaller.__main__.run([
   'main.py',
   '--onefile',
   '--name=%s' % 'vocal_exercise_maker',
   '--windowed'
])

source = 'dist/vocal_exercise_maker.exe'
destination = 'vocal_exercise_maker.exe'

dest = shutil.move(source, destination)
