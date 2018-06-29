# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import sys
import argparse
import queue
import numpy as np

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import sounddevice as sd
from scipy.fftpack import fft
from scipy.signal import blackmanharris, find_peaks_cwt, argrelmax

import essentia


r = pow(2, 1./12)
f3 = np.array([440*r**k for k in range(-9, 3)])
fn = np.array([np.array(f3) * np.power(2., k - 3.) for k in range(0, 10)])
notes = np.array(["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si", ""])
colors = np.array(["Red", "violet", "DarkOrange", "Yellow", "Magenta", "Purple", "Lime", "Green", "Teal", "Cyan", "DarkBlue", "Maroon", "White"])
# colors = [(255,0,0),(255,135,0),(255,255,0),(160,255,0),(0,255,0),(105,255,0),(0,255,255),(0,165,255),(0,85,255),(0,0,255),(130,0,255),(255,0,255), (255,255,255)]
colorsName = np.array(["Rouge", "Violet", "Orange", "Jaune", "Magenta", "Mauve", "Lime", "Vert", "Teal", "Cyan", "Bleu", "Marron", "Blanc"])

def frq_note(frequence):
    listHeightIndex = []
    listPitchIndex = []

    for freq in frequence:
        delta = np.abs(np.array(fn) - freq)

        if freq > delta.min():
            HeightIndex = np.where(delta == delta.min())[0][0]
            PitchIndex = np.where(delta == delta.min())[1][0]
        else:
            HeightIndex = 0
            PitchIndex = 12

        listHeightIndex.append(HeightIndex)
        listPitchIndex.append(PitchIndex)

    return [listHeightIndex, listPitchIndex]

SAMPLERATE = 44100
BLOCKSIZE = 2224
FACTOR = 4
MNOISE = 50

sd.default.blocksize = BLOCKSIZE
sd.default.samplerate = SAMPLERATE

q = queue.Queue()

def gen_data():
    global amp
    global data
    global pic
    while True:
        try:
            queuedata = q.get_nowait()
        except queue.Empty:
            break
        queuedata = np.sum(queuedata.T, axis=0)
        LENQUEUEDATA = len(queuedata)

        data = np.roll(data, -LENQUEUEDATA)
        data[-LENQUEUEDATA:] = queuedata
        LENDATA = len(data)

        amp = np.abs(fft(data))
        LENAMP = len(amp)
        noise = MNOISE * amp.mean()
        amp = amp[:LENAMP // 2]
        k = np.arange(LENDATA // 2)
        T = LENDATA / SAMPLERATE
        frq = k / T

        detections = (amp > np.roll(amp, 1)) & (amp > np.roll(amp, -1))
        detections = detections & (amp > noise)
        # detections = argrelmax(amp[detections])

        frq_pic = frq[detections]
        amp_pic = amp[detections]
        LENPIC = len(frq_pic)

        pic = np.zeros([2, LENPIC])
        pic[0, :], pic[1, :] = frq_pic, amp_pic

def update_plot(frame):
    global pic
    global data
    global amp
    gen_data()
    lines.set_ydata(amp[:])
    hline.set_ydata(np.mean(amp)*MNOISE)
    frq_pic = []
    try:
        frq_pic = pic[0]
        amp_pic = pic[1]
        IsEmpty = frq_pic[0]
    except:
        frq_pic = np.zeros([1])
        amp_pic = np.zeros([1])

    return lines, hline

def init1():
    for Circle in listAnims:
        Circle.set_animated(True)
        ax1.add_patch(Circle)
    return listAnims

def update_plot1(i):
    gen_data()

    frq_pic, amp_pic = pic[0, :], pic[1, :]

    try:
        amp_max_pic = np.max(amp_pic)
        frq_pic, amp_pic = pic[0], pic[1]
        amp_pic = amp_pic / amp_max_pic

        # indexQ = np.where(amp_pic > 0.5)
        # frq_pic = frq_pic[indexQ]
        # amp_pic = amp_pic[indexQ]
    except:
        amp_max_pic = 0
        frq_pic, amp_pic = np.zeros([1]), np.zeros([1])

    HeightsIndex = frq_note(frq_pic)[0]
    PitchsIndex = frq_note(frq_pic)[1]

    for Circle in listAnims:
        Circle.set_facecolor("white")
        Circle.set_visible(False)

    k = 0
    for i, j in zip(HeightsIndex, PitchsIndex):
        x = i * 5
        y = j * 2 + 2
        listAnims[k].center = (x, y)
        # listAnims[k].set_facecolor('#%02x%02x%02x' % colors[PitchsIndex[k]])
        listAnims[k].set_facecolor(colors[PitchsIndex[k]])
        listAnims[k].set_radius(amp_pic[k])
        listAnims[k].set_visible(True)
        k+=1

    return listAnims


def callback(indata, frames, time, status):
    q.put(indata[:])

data = np.zeros([BLOCKSIZE*FACTOR])
amp = np.zeros([int(BLOCKSIZE/2)*FACTOR])
pic = np.zeros([1])

LENDATA = BLOCKSIZE*FACTOR
fig, ax = plt.subplots()
k = np.arange(LENDATA // 2)
T = LENDATA / SAMPLERATE
frq = k / T

lines, = ax.plot(frq, amp)
hline = ax.axhline(0, color = "red")
for i in range(8):
    for fr in fn[i,:]:
        if fr < 5000:
            ax.axvline(fr, color = "red")

ax.set_ylim(-3, 900)
ax.set_xlim(0, 5000)

print(sd.query_devices())

ani = FuncAnimation(fig, update_plot, interval = 0, blit = True)

fig1, ax1 = plt.subplots()

listAnims = []
for i in range(8):
    for j in range(12):
        x = i*5
        y = j*2 + 2
        listAnims.append(plt.Circle((x,y), radius = 1, fill = True))
listAnims = tuple(listAnims)

ax1.set_xlim(-2, 38)
ax1.set_ylim(-2, 26)
ax1.set_aspect("equal")
ax1.set_axis_off()

ani1 = FuncAnimation(fig1, update_plot1, init_func = init1, interval = 0, blit = True)

stream = sd.InputStream(channels = 2, blocksize = BLOCKSIZE, samplerate = SAMPLERATE, callback = callback)

with stream:
     plt.show()