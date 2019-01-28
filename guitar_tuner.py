import soundcard as sc
import numpy as np
import matplotlib.pyplot as plt

import sys,os
import curses

import thinkdsp
from constants import KEY_FREQUENCY_MAP_PIANO, FREQUENCY_KEY_MAP_PIANO

FRAMERATE = 44100    


class PitchDetector:

    def __init__(self, stdscr):
        # get a list of all speakers:
        speakers = sc.all_speakers()
        # get the current default speaker on your system:
        self.default_speaker = sc.default_speaker()
        # get a list of all microphones:
        mics = sc.all_microphones()
        # get the current default microphone on your system:
        self.default_mic = self.__get_build_in_mic(mics)
        self.stdscr = stdscr

        self.__load_canvas(stdscr)


    def __get_build_in_mic(self, mics):
        for m in mics:
            if m.name == 'Built-in Microphone':
                return m
        else:
            raise BuiltInMicrophoneNotFoundError

    def __load_canvas(self, stdscr):
        # Clear and refresh the screen for a blank canvas
        self.stdscr.clear()
        self.stdscr.refresh()

        # Start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        # self.__update_canvas()


    def update_canvas(self, pitch='-----'):
        # Initialization
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Declaration of strings
        title = "Pitch Perfect"[:width-1]
        subtitle = "Written by Seyoung & Jonathan"[:width-1]

        # Centering calculations
        start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
        start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        start_x_pitch = int((width // 2) - (len(pitch) // 2) - len(pitch) % 2)
        start_y = int((height // 2) - 2)

        # Rendering some text
        whstr = "Width: {}, Height: {}".format(width, height)
        self.stdscr.addstr(0, 0, whstr, curses.color_pair(1))

        # Render status bar
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.attroff(curses.color_pair(3))

        # Turning on attributes for title
        self.stdscr.attron(curses.color_pair(2))
        self.stdscr.attron(curses.A_BOLD)

        # Rendering title
        self.stdscr.addstr(start_y, start_x_title, title)

        # Turning off attributes for title
        self.stdscr.attroff(curses.color_pair(2))
        self.stdscr.attroff(curses.A_BOLD)

        # Print rest of text
        self.stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
        self.stdscr.addstr(start_y + 3, start_x_pitch, pitch)

        self.stdscr.addstr(height - 1, width -1, '')
        # Refresh the screen
        self.stdscr.refresh()

        # k = self.stdscr.getch()


def make_spectrum(ys, full=False, framerate=FRAMERATE):
    """Computes the spectrum using FFT.

    returns: Spectrum
    """
    n = len(ys)
    d = 1 / framerate

    if full:
        hs = np.fft.fft(ys)
        fs = np.fft.fftfreq(n, d)
    else:
        hs = np.fft.rfft(ys)
        fs = np.fft.rfftfreq(n, d)

    return thinkdsp.Spectrum(hs, fs, framerate, full)

def freq2key(frequency_float, freq2key_map, frequency_array):
    return freq2key_map[
        frequency_array[
            np.argmin(
                np.abs(frequency_array - frequency_float)
                )
            ]
        ]

class PianoPitchDetector(PitchDetector):

    def __init__(self, stdscr):
        super(PianoPitchDetector, self).__init__(stdscr)
        self.update_canvas()
        self.frequencies = np.array(list(KEY_FREQUENCY_MAP_PIANO.values()))
        self.listen()

    def listen(self):
        with self.default_mic.recorder(samplerate=FRAMERATE, channels=1) as mic:
            while True:
                ys = mic.record(numframes=FRAMERATE//5)
                spectrum = make_spectrum(ys)
                frequency_fundamental = spectrum.fs[spectrum.amps.argmax()]
                key = freq2key(frequency_fundamental, FREQUENCY_KEY_MAP_PIANO, self.frequencies)
                sentence = f'{key}: {frequency_fundamental:.2f}HZ'
                self.update_canvas(sentence)

                

    
class BuiltInMicrophoneNotFoundError(Exception):
    pass


if __name__ == "__main__":
    # curses.wrapper(PitchDetector)
    curses.wrapper(PianoPitchDetector)