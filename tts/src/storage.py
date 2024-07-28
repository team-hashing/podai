# src/storage.py

import firebase_admin
from firebase_admin import credentials, storage, firestore
from google.cloud.exceptions import NotFound
import json
import os

FIREBASE_KEY = os.environ.get('FIREBASE_KEY')
STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')

class FirebaseStorage:
    def __init__(self):
        # Initialize Firebase app if not already initialized
        if not firebase_admin._apps:
            # open file and load as json
            with open(FIREBASE_KEY, 'r') as file:
                cred = credentials.Certificate(json.load(file))
            print('Initializing Firebase app', cred)
            firebase_admin.initialize_app(cred, {
                'storageBucket': STORAGE_BUCKET
            })
        
        self.bucket = storage.bucket()
        self.db = firestore.client()

    def get_script(self, user_id: str, podcast_id: str) -> dict:
        doc_ref = self.db.collection('podcasts').document(podcast_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()['script']

    def save_audio(self, user_id: str, podcast_id: str, audio_data: bytes):
        # Crear la ruta del blob con la estructura deseada
        blob = self.bucket.blob(f'podcasts/{podcast_id}/audio.wav')
        blob.upload_from_string(audio_data, content_type='audio/wav')

        doc_ref = self.db.collection('podcasts').document(podcast_id)
        doc_ref.update({
            'status': 'ready'
        })

    def get_audio(self, user_id: str, podcast_id: str) -> bytes:
        # Crear la ruta del blob con la estructura deseada
        blob = self.bucket.blob(f'podcasts/{podcast_id}/audio.wav')
        try:
            return blob.download_as_bytes()
        except NotFound:
            return None
    

    # Temp audio files
    def list_temp_audio_files(self, user_id: str, podcast_id: str) -> list:
        blobs = self.bucket.list_blobs(prefix=f'temp/{user_id}/{podcast_id}/')
        return [blob.name for blob in blobs]
    
    def get_temp_audio_file(self, user_id: str, podcast_id: str, file_name: str) -> bytes:
        blob = self.bucket.blob(f'temp/{user_id}/{podcast_id}/{file_name}')
        try:
            return blob.download_as_bytes()
        except NotFound:
            return None
    
    def save_temp_audio_file(self, user_id: str, podcast_id: str, file_name: str, audio_data: bytes):
        blob = self.bucket.blob(f'temp/{user_id}/{podcast_id}/{file_name}')
        blob.upload_from_string(audio_data, content_type='audio/wav')
    
    def remove_temp_audio_files(self, user_id: str, podcast_id: str):
        blobs = self.bucket.list_blobs(prefix=f'temp/{user_id}/{podcast_id}/')
        for blob in blobs:
            blob.delete()


    def download_voices(self):
        voices_folder = 'voices/'
        blobs = self.bucket.list_blobs(prefix='voices/')
        for blob in blobs:
            file_name = blob.name.split('/')[-1]
            if file_name.endswith('.onnx') or file_name.endswith('.json'):
                blob.download_to_filename(voices_folder + file_name)
