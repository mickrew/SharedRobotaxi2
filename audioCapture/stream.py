import time
from .param import *

FOREVER = -1


def stream_audio(duration, callback):
    audio = pyaudio.PyAudio()  # create pyaudio instantiation

    # create pyaudio stream
    stream = audio.open(format=sample_format,
                        rate=sample_rate,
                        channels=channel,
                        input_device_index=dev_index,
                        input=True,
                        frames_per_buffer=chunk_size,
                        stream_callback=callback,
                        )

    stream.start_stream()

    print("Straming")

    while stream.is_active():
        time.sleep(duration)
        stream.stop_stream()

    print("Stopped")

    stream.close()
    audio.terminate()
