import pyaudio

sample_format = pyaudio.paInt16     # 16-bit resolution
channel = 1                         # 1 channel
sample_rate = 44100                 # 44.1kHz sampling rate
chunk_size = 44100                 # samples for buffer
dev_index = 1                       # device index found by p.get_device_info_by_index(ii)
