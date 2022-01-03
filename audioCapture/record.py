import pyaudio
from .param import sample_format, sample_rate, channel, chunk_size, dev_index
from .utils import save_wav

sample_record_duration = 60


def record(duration):
    audio = pyaudio.PyAudio()  # create pyaudio instantiation

    # create pyaudio stream
    stream = audio.open(format=sample_format,
                        rate=sample_rate,
                        channels=channel,
                        input_device_index=dev_index,
                        input=True,
                        frames_per_buffer=chunk_size
                        )

    print("start recording")

    frames = []

    # loop through stream and append audioCapture chunks to frame array
    for ii in range(0, int((sample_rate / chunk_size) * duration)):
        data = stream.read(chunk_size, exception_on_overflow=False)
        frames.append(data)

    print("stop recording")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()

    return frames


def record_samples(user):
    frames = record(sample_record_duration)
    # save_wav(f'users/{user}/sample', frames)

    n_samples = 10
    step = int(len(frames) / n_samples)
    splits = [frames[i:i + step] for i in range(0, len(frames), step)]

    if len(splits[-1]) < step / 2:
        splits.pop(-1)

    for i, split in enumerate(splits):
        save_wav(f'resources/users/{user}/sample' + str(i), split)
