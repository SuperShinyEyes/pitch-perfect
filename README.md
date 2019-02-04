# Pitch Detector

## Installation
```
make init

# Validate your installation
python -c 'import pitch_perfect; print("Pitch_perfect installation ok.")'
```

## Run
```
. activate pitch-perfect
# Run the following command in any path
perfect
```

## Octave issue
- e3: e5
- f3: f5

## Polyphonic pitch detection
Hard because of [overtone](https://www.pianonoise.com/Article.overtone-series.htm).
An overtone of c1(32.703 Hz) is a multiplication of 32.703 Hz.

- https://dsp.stackexchange.com/questions/18131/thoretically-what-makes-multi-pitch-detection-so-difficult

### MiRex competition
- https://www.music-ir.org/mirex/wiki/2017:Multiple_Fundamental_Frequency_Estimation_%26_Tracking_Results_-_MIREX_Dataset