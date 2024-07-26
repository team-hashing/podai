# src/storage.py

import datetime
import os
import json
from typing import Dict, List
import firebase_admin
from firebase_admin import credentials, storage, firestore
from google.cloud.exceptions import NotFound


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

    def save_podcast_name(self, podcast_id: str, podcast_name: str, podcast_subject: str):
        """Save podcast name to Firestore"""
        doc_ref = self.db.collection('podcasts').document(podcast_id)
        doc_ref.update({'name': podcast_name, 'subject': podcast_subject})

    def get_podcast_name(self, podcast_id: str) -> str:
        """Get podcast name from Firestore"""
        doc_ref = self.db.collection('podcasts').document(podcast_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()['name']
        return None
    
    def get_podcast_subject(self, podcast_id: str) -> str:
        """Get podcast subject from Firestore"""
        doc_ref = self.db.collection('podcasts').document(podcast_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()['subject']
        return

    def save_script(self, user_id: str, podcast_id: str, script_content: str):
        """Save script to Firebase Storage"""
        blob = self.bucket.blob(f'scripts/{user_id}/{podcast_id}.json')
        blob.upload_from_string(json.dumps(script_content))

    def get_script(self, user_id: str, podcast_id: str) -> Dict:
        """Get script from Firebase Storage"""
        blob = self.bucket.blob(f'scripts/{user_id}/{podcast_id}.json')
        try:
            return json.loads(blob.download_as_text())
        except NotFound:
            return None

    def get_audio(self, user_id: str, podcast_id: str) -> bytes:
        """
        Descarga un archivo de audio desde Firebase Storage.

        Args:
            user_id (str): ID del usuario.
            podcast_id (str): ID del podcast.

        Returns:
            bytes: El contenido del archivo de audio en bytes, o None si no se encuentra.
        """
        # Crear la ruta del blob con la estructura deseada
        blob = self.bucket.blob(f'podcasts/{podcast_id}/audio.wav')
        try:
            return blob.download_as_bytes()
        except NotFound:
            return None
        except Exception as e:
            return None
        
    def get_image(self, user_id: str, podcast_id: str) -> str:
        """Get signed URL for image from Firebase Storage"""
        blob = self.bucket.blob(f'podcasts/{podcast_id}/image.png')
        try:
            # Generate a signed URL valid for 1 hour (3600 seconds)
            url = blob.generate_signed_url(expiration=datetime.timedelta(hours=1))
            return url
        except NotFound:
            return None

    def list_scripts(self, user_id: str) -> List[Dict[str, str]]:
        """List all scripts for a user"""
        blobs = self.bucket.list_blobs(prefix=f'scripts/{user_id}/')
        scripts = []
        for blob in blobs:
            podcast_id = blob.name.split('/')[-1].replace('.json', '')
            podcast_name = self.get_podcast_name(podcast_id)
            if podcast_name:
                scripts.append({"id": podcast_id, "name": podcast_name})
        return scripts
    
    def get_user_podcasts(self, user_id: str) -> List[Dict[str, str]]:
        """List all podcasts for a user"""
        docs = self.db.collection('podcasts').where('user_id', '==', user_id).stream()
        podcasts = []
        for doc in docs:
            podcast = doc.to_dict()
            podcast['id'] = doc.id  # Add the document ID to the podcast dictionary
            podcasts.append(podcast)
        return podcasts

# Create a global instance of FirebaseStorage
firebase_storage = FirebaseStorage()