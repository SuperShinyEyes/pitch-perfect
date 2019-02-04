import soundcard as sc
import numpy as np
import matplotlib.pyplot as plt


import sys,os
import curses


FRAME_RATE = 44100    


class PitchDetectorGUI:

    def __init__(self, stdscr):
        self.__stdscr = stdscr

        self.__load_canvas()


    def __load_canvas(self):
        # Clear and refresh the screen for a blank canvas
        self.__stdscr.clear()
        self.__stdscr.refresh()

        # Start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        # self.update_canvas()


    def update_canvas(self, pitch):
        # Initialization
        self.__stdscr.clear()
        height, width = self.__stdscr.getmaxyx()

        # Declaration of strings
        title = "Guitar Tuner"[:width-1]
        subtitle = "Written by Seyoung Park"[:width-1]

        # Centering calculations
        start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
        start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        start_y = int((height // 2) - 2)

        # Rendering some text
        whstr = "Width: {}, Height: {}".format(width, height)
        self.__stdscr.addstr(0, 0, whstr, curses.color_pair(1))

        # Render status bar
        self.__stdscr.attron(curses.color_pair(3))
        self.__stdscr.attroff(curses.color_pair(3))

        # Turning on attributes for title
        self.__stdscr.attron(curses.color_pair(2))
        self.__stdscr.attron(curses.A_BOLD)

        # Rendering title
        self.__stdscr.addstr(start_y, start_x_title, title)

        # Turning off attributes for title
        self.__stdscr.attroff(curses.color_pair(2))
        self.__stdscr.attroff(curses.A_BOLD)

        # Print rest of text
        self.__stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
        self.__stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)

        self.__stdscr.addstr(height - 1, width -1, '')
        # Refresh the screen
        self.__stdscr.refresh()

        _ = self.__stdscr.getch()

class PitchDetector:

    def __init__(self, framerate=44100):
        self.framerate = framerate        
        # get a list of all speakers:
        speakers = sc.all_speakers()
        # get the current default speaker on your system:
        self.default_speaker = sc.default_speaker()
        # get a list of all microphones:
        mics = sc.all_microphones()
        # get the current default microphone on your system:
        self.default_mic = self.__get_build_in_mic(mics)

    def __get_build_in_mic(self, mics):
        for m in mics:
            if m.name == 'Built-in Microphone':
                return m
        else:
            raise BuiltInMicrophoneNotFoundError


class GuitarTuner(PitchDetector):

    def __init__(self, gui, framerate=44100):
        super(GuitarTuner, self).__init__(framerate)
        self.gui = gui
        gui.update_canvas()

    def listen(self):
        with self.default_mic.recorder(samplerate=self.framerate) as mic:
            while True:
                ys = mic.record(numframes=1024)
                

    
class BuiltInMicrophoneNotFoundError(Exception):
    pass

def main():
    gui = curses.wrapper(PitchDetectorGUI)
    tuner = GuitarTuner(gui, framerate=44100)

if __name__ == "__main__":
    # curses.wrapper(PitchDetector)
    # curses.wrapper(GuitarTuner)
    main()