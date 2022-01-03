import wave
import pyaudio
from .param import sample_format, sample_rate, channel


def save_wav(output, frames):
    wavefile = wave.open(output + '.wav', 'wb')
    wavefile.setnchannels(channel)
    wavefile.setsampwidth(pyaudio.PyAudio().get_sample_size(sample_format))
    wavefile.setframerate(sample_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()


def list_devices():
    audio = pyaudio.PyAudio()  # create pyaudio instantiation
    for i in range(audio.get_device_count()):
        dev = audio.get_device_info_by_index(i)
        print((i, dev['name'], dev['maxInputChannels'], dev['defaultSampleRate']))
