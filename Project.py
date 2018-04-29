# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import sys

# sys.path.append("/usr/local/lib/python3/dist-packages")

import argparse
import queue
import numpy as np

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
# import essentia
# import essentia.standard as ess
import matplotlib.patches as patches
import soundfile as sf



# wasapi_exclusive = sd.WasapiSettings(exclusive=True)
# sd.default.extra_settings = wasapi_exclusive

r = pow(2, 1./12)
octave3 = [440*r**k for k in range(-9, 3)]
octaveK = [np.array(octave3) * np.power(2., k - 3.) for k in range(0, 10)]
notes = ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si", ""]
colors = ["Red", "violet", "DarkOrange", "Yellow", "Magenta", "Purple", "Lime", "Green", "Teal", "Cyan", "DarkBlue", "Maroon", "White"]
colorsName = ["Rouge", "Violet", "Orange", "Jaune", "Magenta", "Mauve", "Lime", "Vert", "Teal", "Cyan", "Bleu", "Marron", "Blanc"]

# import pycuda as cuda


# def fft_data(data, fs):
#     a = data.T
#     amp = np.abs(fft(a))
#     noise = 60 * amp.mean()    # Niveau de bruit (arbitraire)
#     d = len(amp) // 2
#     amp = amp[:d]
#     k = np.arange(len(data) // 2)
#     T = len(data) / fs
#     frq = k / T
#     detections = (amp > np.roll(amp, 1)) & (amp > np.roll(amp, -1))    # On sélectionne les pics significatifs    # ... si le point est plus grand que ceux avant et après
#     detections = detections & (amp > noise)    # ... et si l'amplitude est plus grande que le bruit
#     frq_pic = frq[detections]    # On garde dans deux arrays
#     amp_pic = amp[detections]
#
#     return frq_pic, amp_pic


def octave(frequence):
    TabIndex = []

    for freq in frequence:
        v = np.abs(np.array(octaveK) - freq)
        nearZero = np.abs(0 - freq)

        if nearZero > v.min():
            index = np.where(v == v.min())
        else:
            index = 12
        TabIndex.append(index)

    return TabIndex

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

SAMPLERATE = 48000
BLOCKSIZE = 5000

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-l', '--list-devices', action='store_true',help='show list of audio devices and exit')
parser.add_argument('-i', '--interval', type=float, default=1, help='minimum time between plot updates (default: %(default)s ms)')
parser.add_argument('-n', '--downsample', type=int, default=1000, metavar='N', help='display every Nth sample (default: %(default)s)')
parser.add_argument('channels', type=int, default=[1], nargs='*', metavar='CHANNEL', help='input channels to plot (default: the first)')
parser.add_argument('-g', '--gain', type=float, default=1, help='initial gain factor (default %(default)s)')
parser.add_argument('-w', '--window', type=float, default=1000, metavar='DURATION', help='visible time slot (default: %(default)s ms)')

sd.default.blocksize = BLOCKSIZE
sd.default.samplerate = SAMPLERATE

# wasapi_exclusive = sd.WasapiSettings(exclusive=True)
# sd.default.extra_settings = wasapi_exclusive

args = parser.parse_args()

if any(c < 1 for c in args.channels):
    parser.error('argument CHANNEL: must be >= 1')
mapping = [c - 1 for c in args.channels]  # Channel numbers start with 1
q = queue.Queue()

from collections import Counter

# def update_plot(frame):
#     try:
#         data = q.get_nowait()
#         try:
#             Counts = Counter(data)
#             Freq = (Counts.most_common())[0][0]
#             Index = int(octave(data))
#
#             rectangle.set_facecolor(colors[Index])
#             if Index != 12:
#                 text.set_text(colorsName[Index])
#                 NoteText.set_text(notes[Index])
#                 NoteText.set_position((Index*2, 0))
#             else:
#                 text.set_text("")
#                 NoteText.set_text("")
#         except Exception as e:
#             print(type(e).__name__ + ': ' + str(e))
#             rectangle.set_facecolor(colors[12])
#             text.set_text("")
#             NoteText.set_text("")
#     except queue.Empty:
#         None
#
#     rectangle.set_visible(True)
#     text.set_visible(True)
#     NoteText.set_visible(True)
#     return rectangle, text, NoteText,


def update_plot(frame):
    """This is called by matplotlib for each plot update.
    Typically, audio callbacks happen more frequently than plot updates,
    therefore the queue tends to contain multiple blocks of audio data.
    """
    global plotdata
    global data
    while True:
        try:
            queuedata = q.get_nowait()
        except queue.Empty:
            break
        queuedata = queuedata.T[0] + queuedata.T[1]
        LENQUEUEDATA = len(queuedata)
        LENDATA = len(data)
        data = np.roll(data, -LENQUEUEDATA)
        data[-LENQUEUEDATA:] = queuedata

        plotdata = np.abs(fft(data))
        LENPLOTDATA = len(plotdata)
        noise = 40 * plotdata.mean()

        plotdata = plotdata[:LENDATA // 2]
        k = np.arange(LENDATA // 2)
        T = LENDATA / SAMPLERATE
        frq = k / T

        detections = (plotdata > np.roll(plotdata, 1)) & (plotdata > np.roll(plotdata, -1))
        detections = detections & (plotdata > noise)
        frq_pic = frq[detections]
        amp_pic = plotdata[detections]

        lines.set_ydata(plotdata[:])

        try:
            frq_pic[0]
        except:
            frq_pic = np.zeros([1])
            amp_pic = np.zeros([1])

        i = 0
        max = len(frq_pic)
        if i < max:
            text1.set_text(str(frq_pic[i]))
            text1.set_position((frq_pic[i], amp_pic[i]))
            i += 1
        else:
            text1.set_text("")
            text1.set_position((0, 0))

        if i < max:
            text2.set_text(str(frq_pic[i]))
            text2.set_position((frq_pic[i], amp_pic[i]))
            i += 1
        else:
            text2.set_text("")
            text2.set_position((0, 0))

        if i < max:
            text3.set_text(str(frq_pic[i]))
            text3.set_position((frq_pic[i], amp_pic[i]))
            i += 1
        else:
            text3.set_text("")
            text3.set_position((0, 0))

        if i < max:
            text4.set_text(str(frq_pic[i]))
            text4.set_position((frq_pic[i], amp_pic[i]))
            i += 1
        else:
            text4.set_text("")
            text4.set_position((0, 0))

        if i < max:
            text5.set_text(str(frq_pic[i]))
            text5.set_position((frq_pic[i], amp_pic[i]))
            i += 1
        else:
            text5.set_text("")
            text5.set_position((0, 0))

    return lines, text1, text2, text3, text4, text5,

# import vamp
from scipy.fftpack import fft

if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)

# length = int(args.window * SAMPLERATE / (1000 * args.downsample))
# plotdata = np.zeros(length)

# pitchZeros = np.zeros(41)
#
# def callback(indata, frames, time, status):#Fonctionne
#     ppm = ess.PitchMelodia(minDuration = 1, sampleRate = SAMPLERATE, frameSize=frames) #filterIterations = 10, binResolution = 10,
#     el = ess.EqualLoudness(sampleRate = SAMPLERATE)
#     pf = ess.PitchFilter()
#     try:
#         indataEL = el(indata[:, 0])
#         pitch, pitchConfidence = ppm(indataEL)
#         IndexPitchConfidence = np.where(pitchConfidence < 1e-4)
#         pitch[IndexPitchConfidence] = 0
#         pitchF = pf(pitch, pitchConfidence)
#         q.put(pitchF)
#     except Exception:
#         q.put(pitchZeros)

def callback(indata, frames, time, status):
    q.put(indata[:])


# def callback(indata, frames, time, status):
#     # el = ess.EqualLoudness(sampleRate = SAMPLERATE)
#     try:
#         indataEL = (indata[:, 0]).T
#         # sd.play(indataEL, samplerate=SAMPLERATE)
#         amp = np.abs(fft(indataEL))
#         noise = 60 * amp.mean()  # Niveau de bruit (arbitraire)
#         d = len(amp) // 2
#         amp = amp[:d]
#         k = np.arange(len(indataEL) // 2)
#         T = len(indataEL) / SAMPLERATE
#         frq = k / T
#         detections = []
#         c1 = np.any((amp > np.roll(amp, 1)) & (amp > np.roll(amp,-1)))
#         if c1:
#             detections = (amp > np.roll(amp, 1)) & (amp > np.roll(amp,-1))
#             c2 = np.any(detections & (amp > noise))
#             if c2:
#                 detections = detections & (amp > noise)
#
#         frq_pic, amp_pic= frq[detections], amp[detections]
#         print(frq_pic)
#         # frq_pic, amp_pic = fft_data(indataEL, SAMPLERATE)
#         q.put(frq_pic)
#     except Exception as e:
#         print(type(e).__name__ + ': ' + str(e))
#         q.put([])

# fig, ax = plt.subplots()

# lines = ax.plot(plotdata, ls="", marker=".")
# rectangle = plt.Rectangle((0, 0), 28, 28, fill=True)
# text = plt.text(14, 14, "", fontsize=15, color='black')
# NoteText = plt.text(0, 0, "", fontsize=15, color='black')
# ax.add_patch(rectangle)
#
# ax.axis((0, 28, 0, 28))
#
# ax.set_yticks([0])
# ax.yaxis.grid(True)
# ax.tick_params(bottom='off', top='off', labelbottom='off', right='off', left='off', labelleft='off')
# fig.tight_layout(pad=0)


length = int(args.window * SAMPLERATE / (1000 * args.downsample))
data = np.zeros([BLOCKSIZE*4])
plotdata = np.zeros([int(BLOCKSIZE/2)*4])
LENDATA = len(data)

fig, ax = plt.subplots()
k = np.arange(LENDATA // 2)
T = LENDATA / SAMPLERATE
frq = k / T

lines, = ax.plot(frq, plotdata)
text1 = ax.text(0,0, s="")
text2 = ax.text(0,0, s="")
text3 = ax.text(0,0, s="")
text4 = ax.text(0,0, s="")
text5 = ax.text(0,0, s="")

ax.set_ylim(-3, 100)
ax.set_xlim(0, 2000)
stream = sd.InputStream(device = 1, channels = 2, blocksize = BLOCKSIZE, samplerate = SAMPLERATE, callback = callback)
ani = FuncAnimation(fig, update_plot, interval = args.interval, blit = True)

with stream:
     plt.show()

# except Exception as e:
#     parser.exit(type(e).__name__ + ': ' + str(e))
