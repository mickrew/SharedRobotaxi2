import pyaudio
from .param import sample_format, sample_rate, channel, chunk_size, dev_index
from .utils import save_wav

sample_record_duration = 60
UNTIL_STOP = -1


def record(duration, status_queue, button=None):
    # create pyaudio stream
    audio = pyaudio.PyAudio()  # create pyaudio instantiation

    stream = audio.open(format=sample_format,
                        rate=sample_rate,
                        channels=channel,
                        input_device_index=dev_index,
                        input=True,
                        frames_per_buffer=chunk_size
                        )

    print("Start recording")
    status_queue.put('{"status": "Recording"}')
    frames = []
    if duration == UNTIL_STOP:
        while not button.is_pressed:
            data = stream.read(chunk_size, exception_on_overflow=False)
            frames.append(data)
    else:
        for ii in range(0, int((sample_rate / chunk_size) * duration)):
            data = stream.read(chunk_size, exception_on_overflow=False)
            frames.append(data)

    print("Stop recording")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    return frames


def record_samples(user, status_queue):
    frames = record(sample_record_duration, status_queue)

    n_samples = 10
    step = int(len(frames) / n_samples)
    splits = [frames[i:i + step] for i in range(0, len(frames), step)]

    if len(splits[-1]) < step / 2:
        splits.pop(-1)

    for i, split in enumerate(splits):
        save_wav(f'resources/users/{user}/sample' + str(i), split)
