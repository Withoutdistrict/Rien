# import sys
#
# sys.path.append("/usr/local/lib/python3/dist-packages")
#
# import essentia
# import essentia.standard as ess
# from pylab import plot, show, figure, imshow, title
#
# audio = ess.MonoLoader(filename="accord.wav")()
# audio = ess.EqualLoudness()(audio)
#
# pitchmelodia = ess.PitchMelodia()
# pcs = ess.PitchContourSegmentation()
# pf = ess.PitchFilter()
#
# pitch, pitchConfidence = pitchmelodia(audio)
# onset, duration, MIDIPitch = pcs(pitch, audio)
# pf = pf(pitch, pitchConfidence)
#
# # Initialize algorithms we will use
# # loader = ess.MonoLoader(filename='accord.wav')
# # equalloudness = ess.EqualLoudness()
# # pitchmelodia = ess.PitchMelodia()
# #
# # # Use pool to store data
# # pool = essentia.Pool()
# #
# # # Connect streaming algorithms
# # loader.audio >> equalloudness.signal
# # equalloudness.signal >> pitchmelodia.signal
# #
# # pitchmelodia.pitch           >> (pool, "pitch")
# # pitchmelodia.pitchConfidence >> (pool, "pitchConfidence")
#
# # Run streaming network
# # essentia.run(loader)
#
# plot(pitch)
# show()
#

#!/usr/bin/env python3
"""Pass input directly to output.
See https://www.assembla.com/spaces/portaudio/subversion/source/HEAD/portaudio/trunk/test/patest_wire.c
"""
import argparse
import logging


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-i', '--input-device', type=int_or_str,
                    help='input device ID or substring')
parser.add_argument('-o', '--output-device', type=int_or_str,
                    help='output device ID or substring')
parser.add_argument('-c', '--channels', type=int, default=2,
                    help='number of channels')
parser.add_argument('-t', '--dtype', help='audio data type')
parser.add_argument('-s', '--samplerate', type=float, help='sampling rate')
parser.add_argument('-b', '--blocksize', type=int, help='block size')
parser.add_argument('-l', '--latency', type=float, help='latency in seconds')
args = parser.parse_args()

try:
    import sounddevice as sd

    def callback(indata, outdata, frames, time, status):
        if status:
            print(status)
        outdata[:] = indata

    with sd.Stream(device=(args.input_device, args.output_device),
                   samplerate=args.samplerate, blocksize=args.blocksize,
                   dtype=args.dtype, latency=args.latency,
                   channels=args.channels, callback=callback):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()
except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))