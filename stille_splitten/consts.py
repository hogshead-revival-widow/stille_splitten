# status der zurückgegebenen sequenz
SUCCESS = 100
NO_RESULT = -1
UNWEIGHTED_RESULTS = 1

# programm
VERSION = '0.0.7'
NAME = 'stille' # Name des zu generierenden Konsolenskripts

""" Wenn `FFMPEG_FILE` None ist, wird `ffmpeg` im Pfad erwartet.
Andernfalls kann hier die systemspezifische ffmpeg-binary in bin/ abgelegt werden,
dann muss (systemunabhängig) angegeben werden: 'bin/<ffmpeg-datei>'. Wird von `SETTINGS` dann als 
package ressource abgerufen."""
FFMPEG_FILE = None

PYINSTALL_PLANNED = False
