# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

###############################################################################################

import Tkinter as tk
import pydub.playback
import multiprocessing as mlt
import essentia.standard as essstd
from pylab import *
from Queue import Empty
import time

###############################################################################################


###############################################################################################

filename = "31 - Contradanse in C K587"

try:
    sound = pydub.AudioSegment.from_wav(filename + ".wav")

except IOError:
    sound = pydub.AudioSegment.from_mp3(filename + ".mp3")
    sound.export(filename + ".wav", format = "wav")


###############################################################################################

hopSize = 128.
frameSize = 2048.
sampleRate = 44100.
guessUnvoiced = True

###############################################################################################


###############################################################################################

pitchmelodia = essstd.PitchMelodia(binResolution = 1, filterIterations = 10, guessUnvoiced = True, minDuration = 1, timeContinuity = 10)
tonalextractor = essstd.TonalExtractor()

audio = essstd.MonoLoader(filename = filename + ".wav", sampleRate = sampleRate)()
audio = essstd.EqualLoudness()(audio)

pitch, pitchConfidence = pitchmelodia(audio)
timestamps = 8 * hopSize / sampleRate + np.arange(len(pitch)) * (hopSize / sampleRate)

fichier = open(filename + ".data", "w")

for _pitch, _time in zip(pitch, timestamps):
    fichier.write("{} {}".format(_pitch, _time) + "\n")
fichier.close()

fichier = open(filename + ".data", "r")

pitch = []
timestamps = []

for line in fichier:
    line = line.split()
    pitch.append(float(line[0]))
    timestamps.append(float(line[1]))

fichier.close()

pitch = np.array(pitch)
timestamps = np.array(timestamps)

###############################################################################################


###############################################################################################

r = pow(2, 1./12)
octave3 = [440*r**k for k in range(-9, 3)]
octaveK = [np.array(octave3) * np.power(2., k - 3.) for k in range(0, 10)]
notes = ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si", ""]
colors = ["Red", "violet", "DarkOrange", "Yellow", "Magenta", "Purple", "Lime", "Green", "Teal", "Cyan", "DarkBlue", "Maroon", "Black"]

###############################################################################################


###############################################################################################

class Project(object):

    def __init__(self, _q):
        self.window = tk.Tk()
        self.trame = tk.Canvas(self.window, width=2000, height=900)
        self.note = tk.Label(text = "")

        self.window.title('Project')
        self.trame.pack()
        self.note.pack()


        self.ChecksPerSec = 100

        self.window.after(1000/self.ChecksPerSec, self.onTimer, _q)

    def onTimer(self, _q):
        try:
            noteIndex = _q.get(0)
            self.note.config(text = notes[noteIndex] + " : " + colors[noteIndex])
            self.trame.config(bg = colors[noteIndex])
        except Empty:
            pass
        finally:
            GenerateData(_q)
            self.window.after(1000/self.ChecksPerSec, self.onTimer, _q)

def octave(frequence):
    v = np.abs(np.array(octaveK) - frequence)
    nearZero = np.abs(0 - frequence)

    if nearZero > v.min():
        index = np.where(v == v.min())
    else: return 12

    return int(index[1])

lastTime = -1

def GenerateData(_q):
    global lastTime
    newTime = time.time()
    if newTime > lastTime:
        lastTime = newTime
        trackTime = np.array(lastTime - beginTime)
        atTime = np.abs(trackTime - timestamps)
        nearTimeIndex = np.where(atTime == atTime.min())
        noteIndex = octave(pitch[nearTimeIndex])
        _q.put(noteIndex)

def play_sound():
    pydub.playback.play(sound)

###############################################################################################


###############################################################################################
if __name__ == '__main__':
# Queue which will be used for storing Data

    q = mlt.Queue()
    q.cancel_join_thread() # or else thread that puts data will not term

    project = Project(q)

    beginTime = time.time()
    t1 = mlt.Process(target = GenerateData, args = (q,)).start()
    t2 = mlt.Process(target = play_sound).start()

    project.window.mainloop()

###############################################################################################
