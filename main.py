# This is a sample Python script.
from pydub import AudioSegment
import glob
import speech_recognition as sr


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def transcriptWav(filename):
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data)
        print(text)


def readRTTM(filename):
    i = -1
    with open(filename) as file:
        for line in file:
            i = i + 1
            line = line.rstrip().split(' ')
            print(line)
            t1 = float(line[3])  # Works in milliseconds
            t2 = t1 + float(line[4])
            print(str(t1) + " to " + str(t2))
            newNameameAudio = "track" + str(i) + ".wav"
            newAudio = AudioSegment.from_wav("./data/track.wav")
            newAudio = newAudio[t1:t2]
            newAudio.export(newNameameAudio, format="wav")  # Exports to a wav file in the current path.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Start {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    filename = 'C:\\Users\\Micky\\PycharmProjects\\SharedRobotaxi\\data\\speaker_diarization.rttm'
    readRTTM(filename)

    # All files ending with .txt
    list = glob.glob("C:\\Users\\Micky\\PycharmProjects\\SharedRobotaxi\\track*.wav")

    print(list)

    transcriptWav("C:\\Users\\Micky\\PycharmProjects\\SharedRobotaxi\\data\\track.wav")
    # for line in list:
    #    transcriptWav(line)






