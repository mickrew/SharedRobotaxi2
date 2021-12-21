# This is a sample Python script.
from pydub import AudioSegment
import glob
import speech_recognition as sr


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def transcriptWav(filename):
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        try:
            # listen for the data (load audio to memory)
            audio_data = r.record(source)
            # recognize (convert from speech to text)
            text = r.recognize_google(audio_data)
            print(text)
        except:
            print("Error !")


def readRTTM(filename):
    i = -1
    with open(filename) as file:
        for line in file:
            i = i + 1
            line = line.rstrip().split(' ')
            print(line)
            t1 = float(line[3]) * 1000              # Works in milliseconds
            t2 = t1 + float(line[4]) * 1000
            if t2 - t1 < 500:
                continue
            print(str(t1) + " to " + str(t2))
            newNameAudio = "Resources/Audio/Split/track" + str(i) + ".wav"
            newAudio = AudioSegment.from_wav("Resources/Audio/track.wav")
            newAudio = newAudio[t1:t2]
            newAudio.export(newNameAudio, format="wav")  # Exports to a wav file in the current path.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Start {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    filename = 'Resources/speaker_diarization.rttm'
    readRTTM(filename)

    # All files ending with .txt
    list = glob.glob("Resources/Audio/Split/track*.wav")

    print(list)

    #transcriptWav("Resource/Audio/track.wav")
    for line in list:
        print(line)
        transcriptWav(line)
    #transcriptWav("Resources/Audio/Split/track10.wav")





