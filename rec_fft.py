import wave
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.io import wavfile # get the api

try:
    import pyaudio
    
except ModuleNotFoundError:
    # Au cas où le package n'est pas installé, demande à l'utilisateur de le faire
    print('Veuillez installer le package \'pyaudio\':')
    print('> python -m pip install pyaudio\n')
    raise


def record(RECORD_SECONDS = 2):
    """ Records sound from the microphone for RECORD_SECONDS
        and saves to output.wav. 
        From http://people.csail.mit.edu/hubert/pyaudio/
    """
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "output.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print('* recording for {} s'.format(RECORD_SECONDS))

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    
def fft_wav():
    """ Calcule la transformée de Fourier du fichier 'output.wav'
        créé par record() précédemment.
        
        Inspiré de https://stackoverflow.com/questions/23377665/
    """

    # On lit le fichier (fréquence d'échantillonage, données)
    fs, data = wavfile.read('accord.wav')
    
    # On prend seulement le premier channel
    a = data.T
    
    # Calcule la transformée de Fourier (amplitudes)
    print('* calcul de la transformée de Fourier')
    amp = np.abs(fft(a))
    
    # Niveau de bruit (arbitraire)
    noise = 70*amp.mean()
    
    # On a seulement besoin de la première moitiée (symétrie des fonctions réelles)
    d = len(amp)//2  
    amp = amp[:d]
    
    # Pour l'axe x en Hz
    k = np.arange(len(data)//2)
    T = len(data)/fs
    frq = k/T
    plt.plot(np.arange(len(a))*T/100000, a)
 #   plt.show()
    
    # On sélectionne les pics significatifs
    # ... si le point est plus grand que ceux avant et après
    detections = (amp > np.roll(amp, 1)) & (amp > np.roll(amp, -1))
    # ... et si l'amplitude est plus grande que le bruit
    detections = detections & (amp > noise)
    
    # On garde dans deux arrays
    frq_pic = frq[detections]
    amp_pic = amp[detections]
    
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
    print('* fin')
    
    
if __name__ == '__main__':
    fft_wav()
