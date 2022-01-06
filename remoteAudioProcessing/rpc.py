import glob
import xmlrpc.client
from ftplib import FTP

base_user_dir = 'resources/users/'


def update_sr_model(user, model_name):
    session = FTP('DELL-8565U')
    session.login()
    session.mkd(base_user_dir + user)
    files = glob.glob(f'{base_user_dir}{user}/*')
    for file in files:
        with open(file, 'rb') as f:
            session.storbinary(f'STOR {f.name}', f)
    session.quit()

    with xmlrpc.client.ServerProxy("http://DELL-8565U:8000/") as proxy:
        proxy.update_model(model_name)


def audio_processing_pipeline(track_name, diar_model, sr_model):
    session = FTP('DELL-8565U')
    session.login()
    with open('run/dialog1.wav', 'rb') as file:
        session.storbinary(f'STOR {track_name}', file)
    session.quit()
    with xmlrpc.client.ServerProxy("http://DELL-8565U:8000/") as proxy:
        result = proxy.audio_processing_pipeline(track_name, diar_model, sr_model)

    return result
