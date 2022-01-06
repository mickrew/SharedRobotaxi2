import json

import speech_recognition as sr
from vosk import Model, KaldiRecognizer, SetLogLevel
import wave

base_dir = 'resources/model/'


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

    with wave.open(f'{track}.wav', "rb") as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("Audio file must be WAV format mono PCM.")
            exit(1)

        print("speech2text running")

        model = Model(base_dir + "speech2text_ita")
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)

        while True:
            data = wf.readframes(4096)
            if len(data) == 0:
                break
            rec.AcceptWaveform(data)

        return (rec.FinalResult())

        #with open('output.json', 'w', encoding='utf-8') as out:
        #    out.write(rec.FinalResult())
        #    print("speech2text complete")

''' https://alphacephei.com/vosk/models '''

