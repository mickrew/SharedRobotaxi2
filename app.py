import os
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import json
from flask_sock import Sock
from audioCapture.record import record, record_samples
from audioCapture.utils import save_wav
from audioCapture.record import UNTIL_STOP
from gpiozero import Button
from remoteAudioProcessing.rpc import audio_processing_pipeline, update_sr_model
from database import MongoDBConnection as mongo

app = Flask(__name__)
sock = Sock(app)

run_dir = 'run/'
split_dir = run_dir + 'split/'
base_user_dir = 'resources/users/'

# button = Button(2)
recording = False


@app.errorhandler(404)
def handler_404(error):
    return render_template('error_handlers/404.html')


@app.errorhandler(500)
def handler_500(error):
    return render_template('error_handlers/500.html')


@app.route('/')
def index():
    users = mongo.loadAllUsers()
    return render_template("index.html", users=users)


def register(fname, lname):
    user_dir = f'resources/users/{fname}_{lname}'
    try:
        os.mkdir(user_dir)
    except Exception as e:
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

    msg, code = register(fname, lname)
    if code != 200:
        return msg, code

    samples = []
    for file in request.files.lists():
        sample = file[1][0]
        # check format
        if sample.content_type != "audio/wav":
            msg = 'Only wave files allowed'
            return jsonify({'msg': msg}), 406

        samples.append(sample)

    if len(samples) < 5:
        msg = 'Required at least 5 audio samples'
        return jsonify({'msg': msg}), 406

    user_dir = f'{base_user_dir}{fname}_{lname}'
    for i, sample in enumerate(samples):
        sample.save(user_dir + '/' + 'sample' + str(i) + ".wav")

    update_sr_model(f'{fname}_{lname}', 'model.out')

    mongo.insertUser([fname, lname])

    msg = "Sample uploaded !"
    return jsonify({"msg": msg}), 200


@sock.route('/record_samples')
def record_sample(ws):
    ws_request = json.loads(ws.receive())

    fname = ws_request['fname']
    lname = ws_request['lname']

    msg, code = register(fname, lname)
    if code != 200:
        ws.send(json.dumps({'action': 'already enrolled'}))
        ws.receive()

    if ws_request['command'] == 'start':
        sample_text = json.load(open('resources/sample_text.json', encoding='UTF-8'))
        ws.send(json.dumps({'action': 'start', 'text': ("".join(sample_text['text1']))}))
        record_samples(fname + '_' + lname)
        ws.send(json.dumps({'action': 'stop'}))
        mongo.insertUser([fname, lname])
        update_sr_model(f'{fname}_{lname}', 'model.out')
    ws.receive()  # TODO close websocket


@app.route('/details')
def get_detail():
    fname = request.args.get('fname')
    lname = request.args.get('lname')
    lastActivity = request.args.get('lastActivity')
    detail = {'user': [fname,lname,lastActivity], 'phrases': mongo.getConversations([fname, lname])}

    return render_template('details.html', detail=detail)


@app.route('/start', methods=['POST'])
def start_app():
    global button
    button.when_pressed = start_recording
    msg = "started"
    return jsonify({"msg": msg}), 200


@app.route('/stop', methods=['POST'])
def stop_app():
    global button
    button.when_pressed = None
    msg = "stopped"
    return jsonify({"msg": msg}), 200


@app.route('/check', methods=['GET'])
def check():
    global recording
    msg = "ready"
    if recording:
        msg = "recording"

    return jsonify({"msg": msg}), 200


def start_recording():
    print('start recording main')
    global button
    global recording
    button.when_pressed = None
    recording = True
    frames = record(UNTIL_STOP, button)
    recording = False
    track = str(time.time())
    save_wav(f'{run_dir}{track}', frames)

    result = crossDiarizationSpeech(track)
    mongo.insertTranscription(result)

    # button.when_pressed = start_recording


def crossDiarizationSpeech(track):
    result = audio_processing_pipeline(track, 'dihard', 'model.out')
    res = result['diarization']
    transcription = result['text']

    timestamp = float(track)
    listWords = transcription['result']

    listUsers = []
    # nomeuntente1
    # text, timestamp
    # text , timestamp
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
            counterWords += 1
            if (float(word['start']) <= endPeriodPointer and float(word['start']) >= startPeriodPointer):
                phrase = phrase + str(word['word']) + " "
            elif (float(word['start']) >= endPeriodPointer):
                break
        if (counterDiarization < sizeDiarization - 1):
            if (res[counterDiarization + 1]['label'] == label):
                counterDiarization += 1
                continue
            else:
                timestampPhrase = timestamp + endPeriodPointer
                doc = [phrase, timestampPhrase]
                listPeriods[indexUser].append(doc)
                phrase = ""
                counterDiarization += 1
    listPeriods.append(listUsers)
    return listPeriods


if __name__ == '__main__':
    app.run(host='0.0.0.0')

