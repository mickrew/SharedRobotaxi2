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

import audioProcessing
from audioCapture.record import record_samples, record
from audioCapture.stream import stream_audio
from audioCapture.utils import save_wav
from audioProcessing.diarization import speaker_activity_detection, speaker_change_detection
from audioProcessing.speaker_recognition import enroll, batch_predict, live_predict
from audioProcessing.utils import read_rttm, split_track

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


def run():
    #print("SAD DIHARD")
    rttm = speaker_activity_detection('dialog2', 'dihard')
    split_track('test/dialog2', rttm)
    res = batch_predict(glob.glob('test/split/*.wav'), rttm, 'model.out')

    json.dump(res, open('test/res2.json', 'w'))
    res = json.load(open('test/res2.json', 'r'))
    for p in res:
        print(p['track'], p['label'], '\t', p['start'], p['end'])


if __name__ == '__main__':
    #app.run()
    run()

