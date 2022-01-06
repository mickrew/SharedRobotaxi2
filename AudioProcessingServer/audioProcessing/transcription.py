import json

import speech_recognition as sr
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer, SetLogLevel
import wave

model_dir = 'root/resources/model/'
test_dir = 'root/test/'
run_dir = 'root/run/'

def google_speech2text(filename):
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        try:
            # calibrates the recognizer to the noise level of the audio
            r.adjust_for_ambient_noise(source, 1)
            # listen for the data (load audio to memory)
            audio_data = r.record(source)
            # recognize (convert from speech to text)
            text = r.recognize_google(audio_data, language="it-IT")
            print(text)
        except Exception as e:
            print("Error ! \t" + filename.split('/')[3])


def local_speech2text(track):
    SetLogLevel(level=-1)
    audio = AudioSegment.from_wav(f'{run_dir}{track}.wav')
    audio = audio.set_channels(1)
    audio.export(f'{run_dir}{track}.wav', format='wav')

    with wave.open(f'{run_dir}{track}.wav', "rb") as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("Audio file must be WAV format mono PCM.")
            exit(1)

        model = Model(model_dir + "speech2text_ita")
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)

        while True:
            data = wf.readframes(4096)
            if len(data) == 0:
                break
            rec.AcceptWaveform(data)

        return json.loads(rec.FinalResult())

''' https://alphacephei.com/vosk/models '''

