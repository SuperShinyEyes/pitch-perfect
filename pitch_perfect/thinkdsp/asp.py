
import numpy as np
from pitch_perfect.data import FREQUENCY_KEY_MAP, FREQUENCY_ARRAY


def autocorrelate(ys):
    N = len(ys)
    lengths = range(N, N//2, -1)
    
    corrs = np.correlate(
        ys, 
        ys, 
        mode='same'  # Range of lag. 'same' is in the range from -N/2 to N/2,
                     # where N is the length of the given segment
        )
    
    # The 'same' mode return a symmetric autocorrelation values which is in 
    # the range from -N/2 to N/2. Take only the positive half.
    corrs = corrs[N//2:]
    
    # Offset diminish over time
    corrs /= lengths
    # Normalize so -1 <= corrs <= 1
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



def get_sound_pressure_level(ys, p0=2E-6):
    """Get sound pressure level of given chunk
    https://en.wikipedia.org/wiki/Sound_pressure#Sound_pressure_level
    
    Args:
        ys (np.array): 1-D signal
        p0 (float): Reference sound pressure. 
                    Default value is the commonly used 20 micropascals.

    """
    n = len(ys)
    p = np.sqrt(np.sum(ys ** 2) / n)
    return 20 * np.log10(p / p0)


def is_quiet(spl):
    """Evaluates if there was an input or just ambient noise. The threshold is
    based on the following chart:
    https://en.wikipedia.org/wiki/Sound_pressure#Examples_of_sound_pressure

    Args:
        spl (float): Sound pressur level

    """
    return spl < 60


def freq2key(freq):
    return FREQUENCY_KEY_MAP[
        FREQUENCY_ARRAY[
            np.argmin(
                np.abs(FREQUENCY_ARRAY - freq)
                )
            ]
        ]


def get_pitch_freq(ys):
    corrs = autocorrelate(ys)

    try:
        freq = get_frequency(corrs, *get_next_peak_range(corrs)); 
    except ValueError:
        is_high_pitch = False
        pitch, freq = None, None
    else:
        pitch = freq2key(freq)
        is_high_pitch = True if int(pitch[-1]) > 4 else False
    finally:
        return pitch, freq

class YIN:

    def __init__(self, ys, samplerate=44100):
        self.ys = ys
        self.samplerate = samplerate

        self._diff = self.difference(self.ys)
        self._cmn = self.cumulative_mean_normalized(self._diff)
        self.freq = self.absolute_threshold(self._cmn, samplerate=samplerate)
        self.pitch = freq2key(self.freq)
    
    def difference(self, ys):
        N = len(ys)    
        return np.array(
            [ np.sum(
                ( ys[lag:] - ys[:N-lag] ) ** 2
                ) for lag in range(N//2) ]
            )

    
    def cumulative_mean_normalized(self, diffs):
        """
        Args:
            diffs (np.array): Difference over range of lags
        """
        cmn = np.zeros(diffs.shape)
        cmn[0] = 1
        for lag in range(1, len(diffs)) :
            cmn[lag] = diffs[lag] / (
            np.sum(diffs[1:lag+1]) / lag
            )  
        return cmn


    def absolute_threshold(self, cmn, samplerate=44100):
        """
        Args:
            cmn (np.array): Cumulative mean normalized difference
        """
        def cannot_apply_absolute_threshold(cmn):
            return np.alltrue(cmn > 0.1)
        
        if cannot_apply_absolute_threshold(cmn):
            # Return global minimum period
            return  44100 / np.argmin(cmn)
        
        first_dip_start = np.argmax(cmn < 0.1)
        first_dip_end = np.argmax(cmn[first_dip_start:] > 0.1) + first_dip_start

        absolute_threshold_min = np.argmin(
            cmn[first_dip_start:first_dip_end]
        ) + first_dip_start

        return 44100 / absolute_threshold_min