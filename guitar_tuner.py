import soundcard as sc
import numpy as np
import matplotlib.pyplot as plt


import sys,os
import curses


FRAME_RATE = 44100    


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
        stdscr.clear()
        stdscr.refresh()

        # Start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        self.__update_canvas(stdscr)


    def __update_canvas(self, stdscr):
        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Declaration of strings
        title = "Guitar Tuner"[:width-1]
        subtitle = "Written by Seyoung Park"[:width-1]

        # Centering calculations
        start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
        start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        start_y = int((height // 2) - 2)

        # Rendering some text
        whstr = "Width: {}, Height: {}".format(width, height)
        stdscr.addstr(0, 0, whstr, curses.color_pair(1))

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.attroff(curses.color_pair(3))

        # Turning on attributes for title
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)

        # Rendering title
        stdscr.addstr(start_y, start_x_title, title)

        # Turning off attributes for title
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.A_BOLD)

        # Print rest of text
        stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
        stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)

        stdscr.addstr(height - 1, width -1, '')
        # Refresh the screen
        stdscr.refresh()

        k = stdscr.getch()


class GuitarTuner(PitchDetector):

    def __init__(self, stdscr):
        super(GuitarTuner, self).__init__(stdscr)

    def listen(self):
        with self.default_mic.recorder(samplerate=FRAME_RATE) as mic:
            while True:
                ys = mic.record(numframes=1024)
                sp.play(data)
                

    
class BuiltInMicrophoneNotFoundError(Exception):
    pass


if __name__ == "__main__":
    # curses.wrapper(PitchDetector)
    curses.wrapper(GuitarTuner)