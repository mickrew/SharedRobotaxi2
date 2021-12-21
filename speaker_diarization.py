# load pipeline
import torch
model = ['dia_dihard','dia_ami','dia_etape']
pipeline = torch.hub.load('pyannote/pyannote-audio', model[1])

# apply diarization pipeline on your audio file
diarization = pipeline({'audio': 'track.wav'})

# dump result to disk using RTTM format
with open('Resources/speaker_diarization.rttm', 'w') as f:
    diarization.write_rttm(f)
  
# iterate over speech turns
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f'Speaker "{speaker}" speaks between t={turn.start:.1f}s and t={turn.end:.1f}s.')

