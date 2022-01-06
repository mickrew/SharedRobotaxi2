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

app = Flask(__name__)
sock = Sock(app)

run_dir = 'run/'
split_dir = run_dir + 'split/'
base_user_dir = 'resources/users/'

#button = Button(2)
recording = False


@app.errorhandler(404)
def handler_404(error):
    return render_template('error_handlers/404.html')


@app.errorhandler(500)
def handler_500(error):
    return render_template('error_handlers/500.html')


@app.route('/')
def index():
    # users = db.loadAllUsers() # TODO

    users = [{'fname': 'federico', 'lname': 'cristofani', 'last_activity': '22-01-04'},
             {'fname': 'michelangelo', 'lname': 'martorana', 'last_activity': '22-01-04'}]
    # for i in range(0, 10):
    #    users.append({'fname': 'federico', 'lname': 'cristofani', 'last_activity': '22-01-04'})

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
        update_sr_model(f'{fname}_{lname}', 'model.out')
    ws.receive()  # TODO close websocket


@app.route('/details')
def get_detail():
    user = request.args.get('user')
    # detail = db.getConversations([fname, lname]]) # TODO

    phrases = []
    for i in range(0, 100):
        phrases.append({'timestamp': datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                        'text': ''.join('a ' for j in range(0, 200))})
    detail = {
        'user': {'fname': 'federico', 'lname': 'cristofani', 'last_activity': '22-01-04'},
        'phrases': phrases
    }

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

    result = audio_processing_pipeline(track, 'dihard', 'model.out')
    # save_to_db(result['diarization'], result['text']) # TODO

    # button.when_pressed = start_recording


if __name__ == '__main__':
    app.run(host='0.0.0.0')
