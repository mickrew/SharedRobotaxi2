# load model and wrap it in a pipeline
import torch

model = ['sad_dihard','sad_ami','sad_etape'] #the latter may be unavailable

pipeline = torch.hub.load('pyannote/pyannote-audio', model[1], pipeline=True)

# apply speech activity detection pipeline on your audio file
speech_activity_detection = pipeline({'audio': 'track.wav'})

# dump result to disk using RTTM format
with open('Resources/speech_detection.rttm', 'w') as f:
    speech_activity_detection.write_rttm(f)

for speech_region in speech_activity_detection.get_timeline():
    print(f'There is speech between t={speech_region.start:.1f}s and t={speech_region.end:.1f}s.')
