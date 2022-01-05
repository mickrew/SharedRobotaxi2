import glob
import os
import time
from datetime import datetime

import numpy
import pyaudio
from flask import Flask, render_template, request, jsonify
import json
from flask_sock import Sock
from numpy import int16
from pydub import AudioSegment
from scipy.io import wavfile

import audioProcessing
from audioCapture.record import record_samples, record
from audioCapture.stream import stream_audio
from audioCapture.utils import save_wav
from audioProcessing.diarization import speaker_activity_detection, speaker_change_detection
from audioProcessing.speaker_recognition import enroll, batch_predict, live_predict
from audioProcessing.transcription import local_speech2text
from audioProcessing.utils import read_rttm, split_track
from database import MongoDBConnection

app = Flask(__name__)
sock = Sock(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/enroll', methods=['POST'])
def register():
    fname = request.form.get('fname')
    lname = request.form.get('lname')

    user_dir = f'resources/users/{fname}_{lname}'
    try:
        os.mkdir(user_dir)
    except:
        msg = "User {0} {1} already enrolled".format(fname, lname)
        return jsonify({'msg': msg}), 400

    with open(f'{user_dir}/{fname}_{lname}.json', 'w') as user_file:
        json.dump({'fname': fname, 'lname': lname}, user_file)

    msg = "{0} {1} enrolled !".format(fname, lname)

    return jsonify({'msg': msg}), 200


@app.route('/upload_sample', methods=['POST'])
def upload_samples():
    fname = request.form.get('fname')
    lname = request.form.get('lname')

    samples = []
    for file in request.files.lists():
        sample = file[1][0]

        # check format
        if sample.content_type != "audioCapture/wav":
            msg = 'Only wave files allowed'
            return jsonify({'msg': msg}), 406

        samples.append(sample)

    if len(samples) < 5:
        msg = 'Required at least 5 audioCapture samples'
        return jsonify({'msg': msg}), 406

    user_dir = f'users/{fname}_{lname}'
    for i, sample in enumerate(samples):
        sample.save(user_dir + '/' + 'sample' + str(i) + ".wav")

    msg = "Sample uploaded !"
    return jsonify({"msg": msg}), 200


@sock.route('/record_samples')
def record_sample(ws):
    ws_request = json.loads(ws.receive())
    if ws_request['command'] == 'start':
        sample_text = json.load(open('resources/sample_text.json', encoding='UTF-8'))
        ws.send(json.dumps({'action': 'start', 'text': "".join(sample_text['text1'])}))
        record_samples(ws_request['fname'] + '_' + ws_request['lname'])
        ws.send(json.dumps({'action': 'stop'}))

    ws.receive()  # TODO close websocket


@app.route('/start')
def start():
    stream_audio(300, )
    pass  # wait_for_input() --> press button


@app.route('/stop')
def stop():
    pass



def callback(in_data, frame_count, time_info, flag):
    #live_predict(44100, numpy.frombuffer(buffer=in_data, dtype=int16), 'm.out')
    return None, pyaudio.paContinue

def crossDiarizationSpeech():
    #res = open('test/res2.json')
    #transcription = open('output.json')
    #res = json.load(res)
    ##################
    print("SAD DIHARD")
    rttm = speaker_activity_detection('Conversation-02', 'dihard')
    split_track('test/Conversation-02', rttm)
    res = (batch_predict(glob.glob('test/split/*.wav'), rttm, 'model.out'))
    transcription = json.loads(local_speech2text('test/Conversation-02'))
    #################
    #transcription = json.load(transcription)

    #timestamp = nameFileTimestamp
    timestamp = 0.0 #long(timestamp)
    listWords = transcription['result']

    listUsers = []
    #nomeuntente1
        #text, timestamp
        #text , timestamp
    listPeriods = []

    endPeriodPointer = 0.0
    phrase = ""

    sizeDiarization = len(res)
    counterDiarization = 0

    sizeWords = len(listWords)
    counterWords = 0

    for diarizationDocument in res:
        label = diarizationDocument['label']
        indexuser = 0
        try:
            indexUser = listUsers.index(label)
        except:
            listUsers.append(label)
            listPeriods.append([])
            indexUser = listUsers.index(label)

        startPeriodPointer = endPeriodPointer
        endPeriodPointer = float(diarizationDocument['end'])

        for i in range(counterWords, len(listWords)):
            word = listWords[i]
            counterWords+=1
            if (float(word['end']) <= endPeriodPointer and float(word['end']) >= startPeriodPointer):
                phrase = phrase + str(word['word']) + " "
            elif (float(word['end']) >= endPeriodPointer):
                break
        if (counterDiarization<sizeDiarization-1):
            if(res[counterDiarization+1]['label']==label):
                counterDiarization += 1
                continue
            else:
                timestampPhrase = timestamp + endPeriodPointer
                doc = [phrase, timestampPhrase]
                listPeriods[indexUser].append(doc)
                phrase = ""
                counterDiarization+=1
    listPeriods.append(listUsers)
    return listPeriods


if __name__ == '__main__':
    #app.run()

    timeStart = time.time()
    enroll('model.out')
    timeEnroll = time.time() - timeStart
    print("Time to enroll Model: " + str(round(timeEnroll,2)))

    MongoDBConnection.insertUser(["Michelangelo", "Martorana"])
    MongoDBConnection.insertUser(["Federico", "Cristofani"])

    timeStart = time.time()
    results = crossDiarizationSpeech()
    timeCrossDiarizationSpeech = time.time() - timeStart
    print("Time to cross Diarization and speech data: " + str(round(timeCrossDiarizationSpeech, 2)))

    MongoDBConnection.insertTranscription(results)
    listConversation = MongoDBConnection.getConversations(["Michelangelo", "Martorana"])
    print("Michelangelo Martorana")
    for i in listConversation:
        print(i)
    listConversation = MongoDBConnection.getConversations(["Federico", "Cristofani"])
    print("Federico Cristofani")
    for i in listConversation:
        print(i)
    #sound = AudioSegment.from_wav('test/Conversation-02.wav')
    #sound = sound.set_channels(1)
    #sound.export('test/Conversation-02.wav', format="wav")
    #local_speech2text('test/Conversation-02')


