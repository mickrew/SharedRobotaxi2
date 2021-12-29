import os

from flask import Flask, render_template, request, Response
from pydub import AudioSegment, effects     #normalize audio

app = Flask(__name__)


def normalize_audio(track):
    rawsound = AudioSegment("test1.wav", "wav")
    normalizedsound = effects.normalize(rawsound)
    normalizedsound.export("./normalized.wav", format="wav")

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/enroll', methods=['POST'])
def enroll():
    # enroll new user

    fname = request.form.get('fname')
    lname = request.form.get('lname')

    samples = []
    for file in request.files.lists():
        sample = file[1][0]

        # check format

        if sample.content_type != "audio/wav" and sample.content_type != "audio/webm;codecs=opus" and sample.content_type != "audio/wav; codecs=ms_pcm":
            print(sample.content_type)
            data = {'msg': 'Only wav files allowed'}
            return data, 406

        samples.append(sample)

    user_dir = "users/{0}_{1}".format(fname, lname)
    try:
        os.mkdir(user_dir)
    except:
        msg = "User {0} {1} already enrolled !".format(fname, lname)
        return {'msg': msg}, 400

    for i, sample in enumerate(samples):
        sample.save(user_dir + '/' + 'track' + str(i) + ".wav")
    msg = "{0} {1} enrolled !", fname, lname

    return {'msg': msg}, 200


if __name__ == '__main__':
    app.run()
