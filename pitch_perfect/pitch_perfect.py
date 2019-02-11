import soundcard as sc
import numpy as np
import matplotlib.pyplot as plt

import sys,os
import curses

from pitch_perfect.data import FREQUENCY_KEY_MAP, FREQUENCY_ARRAY
from pitch_perfect.thinkdsp import asp, thinkdsp
import time 

FRAMERATE = 44100    


class PitchUI:

    def __init__(self, stdscr, title):
        self.stdscr = stdscr
        self.title = title

        self.__load_canvas(stdscr)

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
        title = self.title[:width-1]
        subtitle = "Written by Seyoung Park"[:width-1]

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

'''
You want to ignore ambient sound. However, you shouldn't ignore high pitches
which tend to have low energy. 

1E-06 ignores E4 guitar string
'''
AMBIENCE_THRESHOLD = 1E-07
class PitchDetectorAudioSystem():

    def __init__(self):

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


class PitchDetector(PitchDetectorAudioSystem):
    def __init__(self, detection_method):
        super(PitchDetector, self).__init__()
        self.detection_method = detection_method
        

    def listen(self, ui):
        with self.default_mic.recorder(samplerate=FRAMERATE, channels=1) as mic:
            while True:
                ys = mic.record(numframes=FRAMERATE//4)
                spl = asp.get_sound_pressure_level(ys)

                if asp.is_quiet(spl, threshold=60):
                    # self.update_canvas(f'Too quiet. mean:{ys.mean()}, max: {ys.max()}')
                    ui.update_canvas()
                    continue
                
                # pitch, freq = asp.Autocorrelation.get_pitch_freq(ys, samplerate=FRAMERATE)
                pitch, freq = self.detection_method.get_pitch_freq(ys, samplerate=FRAMERATE)
                
                # self.__is_high_pitch = True if int(pitch[-1]) > 4 else False
                    
                sentence = f'{pitch}: {freq:.2f}HZ'
                ui.update_canvas(sentence)

                
class PitchTransfer(PitchDetectorAudioSystem):

    def __init__(self, detection_method, samplerate=FRAMERATE, numframes=FRAMERATE//16):
        super(PitchTransfer, self).__init__()
        self.detection_method = detection_method
        self.samplerate = samplerate
        self.numframes = numframes

    def should_wait_for_input(self, last_input_timestamp):
        timedelta = time.time() - last_input_timestamp
        return timedelta % 60 < 0.9

    def synthesize(self, frequencies):
        signals = tuple(
            thinkdsp.CosSignal(freq=fs, amp=0.08, offset=0) for fs in frequencies
        )

        duration = self.numframes / self.samplerate
        waves = tuple(
            s.make_wave(
                duration=duration, start=0, framerate=self.samplerate
                ).ys for s in signals
        )

        return np.concatenate(waves)
        

    def play_pitch_transfer(self, frequencies, speaker):
        if len(frequencies) == 0 or speaker is None: return
        wave = self.synthesize(frequencies)
        speaker.play(wave)

    def get_loudness_of_segment(self, old, new):
        """
        """
        new_length = len(new)
        old = old[new_length:]
        segment = np.concatenate([old, new])
        return asp.get_sound_pressure_level(segment)

    def _is_ready_to_transfer(self, spl, ambience_threshold, last_input_timestamp, frequencies):
        return asp.is_quiet(spl, threshold=ambience_threshold) and \
                not self.should_wait_for_input(last_input_timestamp) and \
                len(frequencies) > 0



    def listen(self, ui):
        last_input_timestamp = 0
        frequencies = []
        ambience_threshold = 70
        segment_for_spl = np.zeros(self.samplerate//2)

        with self.default_mic.recorder(samplerate=self.samplerate, channels=1) as mic, \
             self.default_speaker.player(samplerate=self.samplerate) as speaker:
            while True:
                ys = mic.record(numframes=self.numframes)

                # Get loudness of half sec
                spl = self.get_loudness_of_segment(segment_for_spl, ys)
                
                if self._is_ready_to_transfer(spl, ambience_threshold, last_input_timestamp, frequencies):
                    ui.update_canvas(f'Transferring')
                    self.play_pitch_transfer(frequencies, speaker)

                    # You need to sleep 1 second so the system doesn't wrongly 
                    # listen to "echo" of the transfer
                    time.sleep(1)

                    # NOTE: Soundcard module works only with context manager, and
                    # the Recorder.flush() does not flush all the chunks piled
                    # during the playback.
                    # Thus, recursion is needed in order to flush recorded chunk
                    return self.listen(ui)
                    
                
                if asp.is_quiet(spl, threshold=ambience_threshold) and \
                    not self.should_wait_for_input(last_input_timestamp):
                    ui.update_canvas(f'Quiet {spl:.2f} dB')
                    continue

                if not asp.is_quiet(spl, threshold=ambience_threshold):
                    last_input_timestamp = time.time()


                # pitch, freq = asp.Autocorrelation.get_pitch_freq(ys, samplerate=FRAMERATE)
                pitch, freq = asp.YIN.get_pitch_freq(ys, samplerate=FRAMERATE)
                frequencies.append(freq)                
                ui.update_canvas(f'Listening! {spl:.2f} dB,  Pitch: {pitch}')


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


class PitchDetectorApp:

    def __init__(self, detection_method):
        self.ui = curses.wrapper(PitchUI, "Pitch Detector")
        self.ui.update_canvas()

        self.detector = PitchDetector(detection_method)
        self.detector.listen(self.ui)
    
class PitchTransferApp:

    def __init__(self, detection_method):
        self.ui = curses.wrapper(PitchUI, "Pitch Transfer")
        self.ui.update_canvas()

        self.transfer = PitchTransfer(detection_method)
        self.transfer.listen(self.ui)
    

class BuiltInMicrophoneNotFoundError(Exception):
    pass


def main(detection_method=asp.YIN):
    PitchDetectorApp(detection_method)
