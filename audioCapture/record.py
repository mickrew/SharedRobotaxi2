import json

import pyaudio

from app import elaborate_audio
from app import run_dir
from .param import sample_format, sample_rate, channel, chunk_size, dev_index
from .utils import save_wav

sample_record_duration = 60
UNTIL_STOP = -1
max_time = 60


def record(duration, websocket, button=None):
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
    websocket.send('{"status": "Recording"}')
    frames = []
    #start = time.time()
    if duration == UNTIL_STOP:
        while not button.is_pressed:
            data = stream.read(chunk_size, exception_on_overflow=False)
            #if time.time() - start > max_time:
            #    threading.Thread(target=worker, args=(str(start), frames.copy(), websocket)).start()
            #    start = time.time()
            #    frames.clear()
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


def record_samples(user, websocket):
    frames = record(sample_record_duration, websocket)

    n_samples = 10
    step = int(len(frames) / n_samples)
    splits = [frames[i:i + step] for i in range(0, len(frames), step)]

    if len(splits[-1]) < step / 2:
        splits.pop(-1)

    for i, split in enumerate(splits):
        save_wav(f'resources/users/{user}/sample' + str(i), split)


def worker(track, frames, websocket):
    save_wav(f'{run_dir}{track}', frames)
    try:
        update = elaborate_audio(track)
        websocket.send(json.dumps(update))
    except Exception as e:
        pass
