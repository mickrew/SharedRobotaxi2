import os
import pathlib
import queue
import threading
import time
from datetime import datetime
from operator import itemgetter

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

#button = Button(pin=2)


@app.errorhandler(404)
def handler_404(error):
    return render_template('error_handlers/404.html')


@app.errorhandler(500)
def handler_500(error):
    return render_template('error_handlers/500.html')


@app.route('/')
def index():
    users = mongo.loadAllUsers()
    for user in users:
        if user[2] is not None:
            if isinstance(user[2], str):
                user[2] = user[2][0:10]  # TODO rivedere entry db
            else:
                user[2] = user[2].strftime("%Y-%m-%d")
        else:
            user[2] = 'None'

    return render_template("index.html", users=users)


@app.route('/user_list')
def user_list():
    users = mongo.loadAllUsers()
    for user in users:
        if user[2] is not None:
            if isinstance(user[2], str):
                user[2] = user[2][0:10]  # TODO rivedere entry db
            else:
                user[2] = user[2].strftime("%Y-%m-%d")
        else:
            user[2] = 'None'

    return render_template("user_list.html", users=users)


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
    fname = request.form.get('fname').capitalize()
    lname = request.form.get('lname').capitalize()

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

    status_queue.put('{"status": "Updating model"}')
    update_sr_model(f'{fname}_{lname}', 'model.out')
    mongo.insertUser([fname, lname])
    msg = "Sample uploaded !"
    return jsonify({"msg": msg}), 200


@app.route('/text')
def text():
    fname = request.args.get('fname').capitalize()
    lname = request.args.get('lname').capitalize()
    user_dir = f'resources/users/{fname}_{lname}'
    if pathlib.Path.exists(pathlib.Path(user_dir)):
        msg = "User {0} {1} already enrolled".format(fname, lname)
        return jsonify({'msg': msg}), 400
    sample_text = json.load(open('resources/sample_text.json', encoding='UTF-8'))
    sample = "".join(sample_text['text'])
    return jsonify({'text': sample}), 200


@app.route('/record_samples', methods=['POST'])
def record_sample():
    fname = request.form.get('fname').capitalize()
    lname = request.form.get('lname').capitalize()

    msg, code = register(fname, lname)
    if code != 200:
        return msg, code
    status_queue.put('{"status": "Recording"}')
    record_samples(fname + '_' + lname)
    status_queue.put('{"status": "Updating model"}')
    update_sr_model(f'{fname}_{lname}', 'model.out')
    mongo.insertUser([fname, lname])
    msg = "Sample recorded !"
    return jsonify({"msg": msg}), 200


@app.route('/details')
def get_detail():
    fname = request.args.get('fname')
    lname = request.args.get('lname')
    lastActivity = request.args.get('lastActivity')
    phrases = mongo.getConversations([fname, lname])

    for phrase in phrases:
        if isinstance(phrase[1], str):
            phrase[1] = phrase[1][0:10]  # TODO rivedere entry db
        else:
            phrase[1] = phrase[1].strftime("%Y-%m-%d %H:%M:%S")

    detail = {'user': [fname, lname, lastActivity], 'phrases': phrases, 'len': len(phrases)}

    return render_template('details.html', detail=detail)


status_queue = queue.Queue()


@sock.route('/status')
def status(ws):
    while True:
        status = status_queue.get()
        ws.send(status)

@app.route('/start')
def start_elaboration():
    status_queue.put('{"status": "Processing"}')
    result = crossDiarizationSpeech('1641719348')

    mongo.insertTranscription(result)

    msg = {'status': 'update', 'update': []}
    users = result[-1]
    for i, user in enumerate(users):
        phrases = sorted(result[i], key=itemgetter(1))
        for j in range(0, len(phrases)):
            phrases[j][1] = datetime.fromtimestamp(phrases[j][1]).strftime("%Y-%m-%d %H:%M:%S")
        msg['update'].append({'user': user, 'phrases': phrases})

    status_queue.put(json.dumps(msg))
    return ("" , 200)

def start_recording():
    while True:
        print("Running ...")
        #button.wait_for_press()
        time.sleep(1)
        status_queue.put('{"status": "Recording"}')
        #frames = record(UNTIL_STOP, button)
        status_queue.put('{"status": "Processing"}')
        track = str(time.time())
        #save_wav(f'{run_dir}{track}', frames)
        result = crossDiarizationSpeech(track)

        msg = {'status': 'update', 'update': []}
        users = result[-1]
        for i, user in enumerate(users):
            phrases = sorted(result[i], key=itemgetter(1))
            for j in range(0, len(phrases)):
                phrases[j][1] = datetime.fromtimestamp(phrases[j][1]).strftime("%Y-%m-%d %H:%M:%S")
            msg['update'].append({'user': user, 'phrases': phrases})

        mongo.insertTranscription(result)

        status_queue.put(json.dumps(msg))


def crossDiarizationSpeech(track):
    result = audio_processing_pipeline(track, 'dihard', 'model.out')
    res = result['diarization']
    transcription = result['text']

    timestamp = float(track)
    listWords = transcription['result']

    listUsers = []
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
            if float(word['start']) <= endPeriodPointer and float(word['start']) >= startPeriodPointer:
                phrase = phrase + str(word['word']) + " "
            elif float(word['start']) >= endPeriodPointer:
                break
        if counterDiarization < sizeDiarization - 1:
            if res[counterDiarization + 1]['label'] == label:
                counterDiarization += 1
                continue
            else:
                if (phrase == ""):
                    counterDiarization += 1
                    continue
                timestampPhrase = timestamp + endPeriodPointer
                doc = [phrase, timestampPhrase]
                listPeriods[indexUser].append(doc)
                phrase = ""
                counterDiarization += 1
    listPeriods.append(listUsers)
    return listPeriods


if __name__ == '__main__':
    #threading.Thread(target=start_recording).start()
    app.run(host='0.0.0.0')
