from pydub import AudioSegment
from scipy.io import wavfile

split_dir = 'test/split/'


def read_wav(fname):
    fs, signal = wavfile.read(fname)
    if len(signal.shape) != 1:
        print("convert stereo to mono")
        signal = signal[:, 0]
    return fs, signal


def read_rttm(fname):
    rttm = []
    with open(f'{fname}.rttm', 'r') as file:
        for i, line in enumerate(file):
            line = line.rstrip().split(' ')
            start = float(line[3])
            end = start + float(line[4])
            rttm.append({'split': f'{fname}_{str(i).zfill(2)}', 'start': start, 'end': end})

    return rttm


def split_track(fname, rttm):
    audio = AudioSegment.from_wav(f'{fname}.wav')
    for split in rttm:
        track = audio[split['start'] * 1000:split['end']*1000]
        track.export(f'{split_dir}{split["track"]}.wav', format="wav")
