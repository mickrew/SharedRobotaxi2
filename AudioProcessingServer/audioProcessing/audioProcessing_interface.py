import glob

from .diarization import speaker_activity_detection
from .speaker_recognition import batch_predict, enroll
from .transcription import local_speech2text
from .utils import split_track

run_dir = 'root/run/'
split_dir = run_dir + 'split/'


def audio_processing_pipeline(track_name, diarization_model, sr_model):

    rttm = speaker_activity_detection(track_name, diarization_model)
    split_track(f'{run_dir}{track_name}', rttm)
    diarization = batch_predict(glob.glob(f'{split_dir}{track_name}*.wav'), rttm, sr_model)
    text = local_speech2text(track_name)

    return {'diarization': diarization, 'text': text}


def update_model(model_name):
    enroll(model_name)
