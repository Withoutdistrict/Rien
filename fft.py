import wave
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
from scipy.fftpack import fft, rfft
from scipy.io import wavfile # get the api
from scipy.signal import blackmanharris
from scipy import signal
import pyaudio
import sounddevice as sd
from numpy import pi, cos, cosh, arccosh, arccos, sum, exp
from scipy.signal import argrelextrema, argrelmax

def fft_wav():
    """ Calcule la transformée de Fourier du fichier 'output.wav'
        créé par record() précédemment.
        
        Inspiré de https://stackoverflow.com/questions/23377665/
    """

    # On lit le fichier (fréquence d'échantillonage, données)
    fs, data = wavfile.read('261-329-392.wav')
    N = 2500
    w = blackmanharris(N)
    data = np.concatenate((data[0:N].T, data[N:N*2].T))


    # data = np.concatenate((data,)*50)
    l = len(data)
    # On prend seulement le premier channel
    # Calcule la transformée de Fourier (amplitudes)
    amp = abs(fft(data))
    
    # Niveau de bruit (arbitraire)
    noise = 50*amp.mean()
    
    # On a seulement besoin de la première moitiée (symétrie des fonctions réelles)
    d = len(amp)//2
    amp = amp[:d]
    
    # Pour l'axe x en Hz
    k = np.arange(l//2)
    T = l/fs
    frq = k/T
    # sd.play(data, samplerate=fs)
    time = np.arange(l) * T / 100000
    plt.plot(time, data)
    # plt.show()
    
    # On sélectionne les pics significatifs
    # ... si le point est plus grand que ceux avant et après
    detections = (amp > np.roll(amp, 1)) & (amp > np.roll(amp, -1))
    # ... et si l'amplitude est plus grande que le bruit
    detections = detections & (amp > noise)

    # On garde dans deux arrays
    frq_pic = frq[detections]
    amp_pic = amp[detections]
    print(frq_pic)
    print("[261.0 329.0 392.0]")

    # Graphique
    fig, ax = plt.subplots()
    
    # bruit
    ax.axhline(noise, c='r', ls=':')
    
    # Pour chaque pic détecté, on indique sa fréquence sur le graphique
    for f, a in zip(frq_pic, amp_pic):
        xy = np.array([f, a])
        ax.annotate('{:.0f} Hz'.format(f),  # indique la fréquence
                    xy = xy,                # position de l'annotation
                    xytext = 1.01*xy,       # position du texte
                    clip_on = True)
    
    # Axes et labels
    ax.minorticks_on()
    ax.plot(frq, amp)
    ax.set_xlabel('Fréquence (Hz)')
    ax.set_xlim(0, 2000)
    ax.set_ylabel('Amplitude')
    ax.set_title('Transformée de Fourier')
    #fig.savefig('fft.png')
    plt.show(fig)
    plt.close(fig)
    
if __name__ == '__main__':
    fft_wav()
