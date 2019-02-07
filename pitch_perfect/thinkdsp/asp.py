
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