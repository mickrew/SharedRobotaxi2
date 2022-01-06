import torch

scd_model = {'dihard': 'scd_dihard', 'ami': 'scd_ami', 'etape': 'scd_etape'}  # the latter may be unavailable
sad_model = {'dihard': 'sad_dihard', 'ami': 'sad_ami', 'etape': 'sad_etape'}  # the latter may be unavailable

test_dir = 'root/test/'
run_dir = 'root/run/'


def speaker_change_detection(track, model):
    # load scd pipeline
    scd_pipeline = torch.hub.load('pyannote/pyannote-audio', scd_model[model], pipeline=True)

    # apply speech activity detection pipeline on your audio file
    scd = scd_pipeline({'audio': f'{run_dir}{track}.wav'})

    rttm = []
    for i, turn in enumerate(scd.itertracks(yield_label=True)):
        rttm.append({'track': f'{track}_{str(i).zfill(2)}', 'start': turn[0].start, 'end': turn[0].end})
    return rttm


def speaker_activity_detection(track, model):
    # load sad pipeline
    sad_pipeline = torch.hub.load('pyannote/pyannote-audio', sad_model[model], pipeline=True)

    # apply speech activity detection pipeline on your audio file
    sad = sad_pipeline({'audio': f'{run_dir}{track}.wav'})

    rttm = []
    for i, speech_region in enumerate(sad.get_timeline()):
        rttm.append({'track': f'{track}_{str(i).zfill(2)}', 'start': speech_region.start, 'end': speech_region.end})

    return rttm
