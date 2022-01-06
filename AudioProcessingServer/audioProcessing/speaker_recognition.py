import glob
import json
import os

from .utils import read_wav
from .interface import ModelInterface

model_dir = 'root/resources/model/speaker_recognition/'


def enroll(output_model):
    model = ModelInterface()
    base_user_dir = 'root/resources/users/'
    user_dirs = os.listdir(base_user_dir)

    if len(user_dirs) == 0:
        print("No user available !")
        return

    for user in user_dirs:
        print(user)
        label = user
        samples = glob.glob(base_user_dir + user + '/*.wav')
        if len(samples) == 0:
            print(f"No wav file found for {user}")
            pass
        for sample in samples:
            print(sample)
            try:
                fs, signal = read_wav(sample)
                model.enroll(label, fs, signal)
            except Exception as e:
                print(f"Error for sample {sample} in {user}")

    model.train()
    model.dump(model_dir + output_model)


def batch_predict(input_files, rttm, input_model):
    model = ModelInterface.load(model_dir + input_model)
    prediction = []

    for i, f in enumerate(input_files):
        fs, signal = read_wav(f)
        label, score = model.predict(fs, signal)
        prediction.append({'track': f, 'label': label, 'score': score, 'start': rttm[i]['start'], 'end': rttm[i]['end']})

    return prediction


def predict(fname, input_model):
    model = ModelInterface.load(model_dir + input_model)
    fs, signal = read_wav(fname)
    label, score = model.predict(fs, signal)

    return {'fname': fname, 'label': label, 'score': score}


def live_predict(fs, signal, input_model):
    model = ModelInterface.load(model_dir + input_model)
    label, score = model.predict(fs, signal)
    print(label, ", score->", score)

