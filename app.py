import os
import pathlib
import time
from datetime import datetime
from operator import itemgetter

from flask import Flask, render_template, request, jsonify
import json
from flask_sock import Sock
from audioCapture.record import record, record_samples
from audioCapture.utils import save_wav
from audioCapture.record import UNTIL_STOP
from remoteAudioProcessing.rpc import audio_processing_pipeline, update_sr_model
from database import MongoDBConnection as mongo

app = Flask(__name__)
sock = Sock(app)

run_dir = 'run/'
split_dir = run_dir + 'split/'
base_user_dir = 'resources/users/'


class StopRec:
    stop = False


stop_rec = StopRec()
websocket = None


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

    msg, code = register(fname, lname)
    if code != 200:
        return msg, code

    user_dir = f'{base_user_dir}{fname}_{lname}'
    for i, sample in enumerate(samples):
        sample.save(user_dir + '/' + 'sample' + str(i) + ".wav")

    websocket.send('{"status": "Updating model"}')

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

    record_samples(fname + '_' + lname, websocket)
    websocket.send('{"status": "Updating model"}')
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


@app.route('/upload_track', methods=['POST'])
def upload_track():

    for file in request.files.lists():
        track = file[1][0]

    if track.content_type != "audio/wav":
        msg = 'Only wave files allowed'
        return jsonify({'msg': msg}), 406

    track_name = str(time.time())
    track.save(f'{run_dir}{track_name}.wav')

    websocket.send('{"status": "Processing"}')

    msg = {'status': 'update', 'update': []}
    try:
        result = crossDiarizationSpeech(track_name)
        result_copy = result.copy()
        mongo.insertTranscription(result)

        users = result_copy[-1]
        for i, user in enumerate(users):
            phrases = sorted(result_copy[i], key=itemgetter(1))
            for j in range(0, len(phrases)):
                phrases[j][1] = datetime.fromtimestamp(phrases[j][1]).strftime("%Y-%m-%d %H:%M:%S")
            msg['update'].append({'user': user, 'phrases': phrases})
    except Exception:
        pass

    websocket.send(json.dumps(msg))

    return "", 200


@sock.route('/status')
def status(ws):
    global websocket
    websocket = ws
    print(ws.receive())


@app.route('/stop_recording')
def stop_recording():
    global stop_rec
    stop_rec.stop = True
    return "", 200


@app.route('/start_recording')
def start_recording():
    global stop_rec
    stop_rec.stop = False

    frames = record(UNTIL_STOP, websocket, stop_rec)
    websocket.send('{"status": "Processing"}')
    track = str(time.time())
    save_wav(f'{run_dir}{track}', frames)

    msg = {'status': 'update', 'update': []}
    try:
        result = crossDiarizationSpeech(track)
        result_copy = result.copy()
        mongo.insertTranscription(result)

        users = result_copy[-1]
        for i, user in enumerate(users):
            phrases = sorted(result_copy[i], key=itemgetter(1))
            for j in range(0, len(phrases)):
                phrases[j][1] = datetime.fromtimestamp(phrases[j][1]).strftime("%Y-%m-%d %H:%M:%S")
            msg['update'].append({'user': user, 'phrases': phrases})
    except Exception:
        pass

    websocket.send(json.dumps(msg))

    return "", 200


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
                counterWords -= 1
                break

        if counterDiarization < sizeDiarization - 1:
            if (res[counterDiarization + 1]['label'] == label):
                counterDiarization += 1
                continue
            else:
                if phrase == "":
                    counterDiarization += 1
                    continue
                timestampPhrase = timestamp + endPeriodPointer
                doc = [phrase, timestampPhrase]
                listPeriods[indexUser].append(doc)
                phrase = ""
                counterDiarization += 1
        else:
            if phrase == "":
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
    app.run(host='0.0.0.0')
