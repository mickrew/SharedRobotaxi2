import glob
import os
import threading
from xmlrpc.server import SimpleXMLRPCServer
from pyftpdlib import servers
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer

from audioProcessing.audioProcessing_interface import *

from AudioProcessingServer.audioProcessing.transcription import google_speech2text

authorizer = DummyAuthorizer()
authorizer.add_anonymous(os.getcwd() + '/root', perm='elradfmwMT')

handler = FTPHandler
handler.authorizer = authorizer
handler.permit_foreign_addresses = True

ftp_server = servers.FTPServer(("0.0.0.0", 21), handler)


rpc_server = SimpleXMLRPCServer(('0.0.0.0', 8000),  allow_none=True)

rpc_server.register_function(audio_processing_pipeline, 'audio_processing_pipeline')
rpc_server.register_function(update_model, 'update_model')

if __name__ == '__main__':
    threading.Thread(target=ftp_server.serve_forever).start()
    threading.Thread(target=rpc_server.serve_forever).start()
    #google_speech2text('1641637494')
