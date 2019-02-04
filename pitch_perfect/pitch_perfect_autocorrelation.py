import soundcard as sc
import numpy as np
import matplotlib.pyplot as plt

import sys,os
import curses

import thinkdsp
from constants import FREQUENCY_KEY_MAP, FREQUENCY_ARRAY

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

def autocorrelate(ys):
    N = len(ys)
    lengths = range(N, N//2, -1)
    
    corrs = np.correlate(ys, ys, mode='same')
    lags = np.arange(-N//2, N//2)
    
    # Take only the positive half
    corrs = corrs[N//2:]
    
    corrs /= lengths
    corrs /= corrs[0]
    return corrs

def get_next_peak_range(ys):
    a = np.argmax(ys < 0.7)

    start = np.argmax(ys[a:] > 0.7) + a

    end = np.argmax(ys[start:] < 0.7) + start
    return start, end

def get_frequency(ys, start, end):
    lag = ys[start:end].argmax() + start
    period = lag / 44100
    return 1/period

def freq2key(freq):
    return FREQUENCY_KEY_MAP[
        FREQUENCY_ARRAY[
            np.argmin(
                np.abs(FREQUENCY_ARRAY - freq)
                )
            ]
        ]

'''
You want to ignore ambient sound. However, you shouldn't ignore high pitches
which tend to have low energy. 

1E-06 ignores E4 guitar string
'''
AMBIENCE_THRESHOLD = 1E-07
class PianoPitchDetector(PitchDetector):

    def __init__(self, stdscr):
        super(PianoPitchDetector, self).__init__(stdscr)
        self.__is_high_pitch = False
        self.update_canvas()
        self.listen()

    def listen(self):
        with self.default_mic.recorder(samplerate=FRAMERATE, channels=1) as mic:
            while True:
                ys = mic.record(numframes=FRAMERATE//4)
                if not self.__is_high_pitch and np.abs(ys.mean()) < AMBIENCE_THRESHOLD:
                    # self.update_canvas(f'Too quiet. mean:{ys.mean()}, max: {ys.max()}')
                    self.update_canvas()
                    continue
                
                corrs = autocorrelate(ys)
                try:
                    freq = get_frequency(corrs, *get_next_peak_range(corrs)); 
                except ValueError:
                    self.__is_high_pitch = False
                    pass
                else:
                    pitch = freq2key(freq)
                    
                    self.__is_high_pitch = True if int(pitch[-1]) > 4 else False
                        
                    sentence = f'{pitch}: {freq:.2f}HZ'
                    self.update_canvas(sentence)

                

    
class BuiltInMicrophoneNotFoundError(Exception):
    pass


if __name__ == "__main__":
    # curses.wrapper(PitchDetector)
    curses.wrapper(PianoPitchDetector)