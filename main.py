# This is a sample Python script.
import os

from pydub import AudioSegment
import glob
import speech_recognition as sr
import speech_detection as sd


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def transcriptWav(filename):
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        try:
            #calibrates the recognizer to the noise level of the audio
            r.adjust_for_ambient_noise(source, 1)
            # listen for the data (load audio to memory)
            audio_data = r.record(source)
            # recognize (convert from speech to text)
            text = r.recognize_google(audio_data)
            print(text)
        except:
            print("Error !")

def readRTTM(filename, fileAudio):
    i = -1
    with open(filename) as file:
        for line in file:
            i = i + 1
            line = line.rstrip().split(' ')
            #print(line)
            t1 = float(line[3]) * 1000              # Works in milliseconds
            t2 = t1 + float(line[4]) * 1000
            if t2 - t1 < 500:
                continue
            #print(str(t1) + " to " + str(t2))
            newNameAudio = "Resources/Audio/Split/track" + str(i) + ".wav"
            newAudio = AudioSegment.from_wav(fileAudio)
            newAudio = newAudio[t1:t2]
            newAudio.export(newNameAudio, format="wav")  # Exports to a wav file in the current path.

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Start {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm Start')
    listAudio = glob.glob("Resources/Audio/track*.wav")

    for list in listAudio:
        #transcriptWav(list)
        sd.diarization(list)
        readRTTM(list.replace('.wav', '.rttm'), list)
        listSplit = glob.glob("Resources/Audio/Split/track*.wav")
        for line in listSplit:
            transcriptWav(line)

        for line in listSplit:
            os.remove(line)
            os.remove(list.replace('.wav', '.rttm'))






