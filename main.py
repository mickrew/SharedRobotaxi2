# This is a sample Python script.
from datetime import datetime
import os

from pydub import AudioSegment
import glob
import speech_recognition as sr
from scipy.io import wavfile

import speech_detection as sd
import time
import noisereduce as nr
import speakerRecognition

import MongoDBConnection as mongo


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
def noiseReduce(filename):
    # load data
    rate, data = wavfile.read(filename)
    # perform noise reduction
    rate = 44100
    reduced_noise = nr.reduce_noise(y=data, sr=rate)
    newName = "Resources/Audio/NoiseReduced/" + filename.split("\\")[1].replace(".wav", "") + "-reduced.wav"
    reduced_noise.export(newName, format="wav")


def transcriptWav(filename):
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        try:
            #calibrates the recognizer to the noise level of the audio
            r.adjust_for_ambient_noise(source, 1)
            # listen for the data (load audio to memory)
            audio_data = r.record(source)
            # recognize (convert from speech to text)
            text = r.recognize_google(audio_data,language="it-IT")
            print(text)
            return text
        except:
            print("Error ! \t" + filename.split('/')[3])

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
    listAudio = glob.glob("Resources/Audio/*.wav")
    print(listAudio)

    docList = []

    for list in listAudio:
        #noiseReduce(list)
        docList.clear()
        #transcriptWav(list)
        start = time.time()
        print(list)
        newPath = "Resources/Audio/NoiseReduced/" + list.split("\\")[1].replace(".wav", "") + "-reduced.wav"
        newPath1 = list
        #print(newPath)
        sd.diarization(list)
        end = time.time()
        print ("\nDiarization: " + str(end-start)+"\n")

        text=''
        author=''
        timestamp=''

        readRTTM(list.replace('.wav', '.rttm'), list)
        listSplit = glob.glob("Resources/Audio/Split/track*.wav")
        for line in listSplit:
            text = transcriptWav(line)
            author = speakerRecognition.task_predict(line, "model.out")
            now = datetime.now()
            timestamp = now.strftime("%Y/%m/%d %H:%M:%S")
            doc = {"author": author, "transcription": text, "timestap": datetime.strptime(timestamp, '%Y/%m/%d %H:%M:%S')}
            docList.append(doc)

        mongo.insertMongoTranscription(docList)

        for line in listSplit:
            os.remove(line)
            #os.remove(list.replace('.wav', '.rttm'))






