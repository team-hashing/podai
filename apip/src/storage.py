# src/storage.py

import datetime
import os
import json
from typing import Dict, List
import firebase_admin
from firebase_admin import credentials, storage, firestore
from google.cloud.exceptions import NotFound
from src.log import setup_logger

logger = setup_logger("uvicorn")

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

        # inside storage, in podcast folder, check the duration of every audio.wav
    
    async def save_podcast(self, user_id: str, podcast_id: str, name: str, subject: str):
        """Save podcast details to Firestore"""
        try:
            doc_ref = self.db.collection('podcasts').document(podcast_id)
            now = datetime.datetime.now()
            doc_ref.set({
                'user_id': user_id,
                'script': "",
                'name': name,
                'subject': subject,
                'likes': 0,
                'liked_by': [],
                'created_at': now.timestamp(),
                'duration': 10000,
                'status': 'empty'
            })
        except Exception as e:
            raise

    def save_podcast_name(self, podcast_id: str, podcast_name: str, podcast_subject: str):
        """Save podcast name to Firestore"""
        doc_ref = self.db.collection('podcasts').document(podcast_id)
        doc_ref.update({'name': podcast_name, 'subject': podcast_subject, 'status': 'script done'})

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
    
    def get_user_podcasts(self, user_id: str, page: int, per_page: int) -> List[Dict[str, str]]:
        """List all podcasts for a user"""
        docs = self.db.collection('podcasts').where('user_id', '==', user_id).stream()
        user_ids_to_usernames = {}
        podcasts = []
        for doc in docs:
            podcast = doc.to_dict()
            podcast['id'] = doc.id
            pod_user_id = podcast['user_id']
            if pod_user_id not in user_ids_to_usernames:
                user_ids_to_usernames[pod_user_id] = self.get_username_from_id(pod_user_id)
            podcast['username'] = user_ids_to_usernames[pod_user_id]
            podcasts.append(podcast)

        total_pages = len(podcasts) // per_page
        if page != 0:
            start = (page - 1) * per_page
            end = start + per_page
            podcasts = podcasts[start:end]
        
        if page == 0:
            return podcasts
        return {'podcasts': podcasts, 'total_pages': total_pages}
    
    def get_podcasts_by_likes(self, user_id: str, page: int = 0, per_page: int = 10) -> List[Dict[str, str]]:
        """List all podcasts ordered by likes"""
        docs = self.db.collection('podcasts').order_by('likes', direction=firestore.Query.DESCENDING).stream()
        podcasts = []
        user_ids_to_usernames = {}
        for doc in docs:
            podcast = doc.to_dict()
            podcast['id'] = doc.id
            pod_user_id = podcast['user_id']
            if pod_user_id not in user_ids_to_usernames:
                user_ids_to_usernames[pod_user_id] = self.get_username_from_id(pod_user_id)
            podcast['username'] = user_ids_to_usernames[pod_user_id]
            podcasts.append(podcast)
        total_pages = len(podcasts) // per_page
        
        if page != 0:
            start = (page - 1) * per_page
            end = start + per_page
            podcasts = podcasts[start:end]
        if page == 0:
            return podcasts
        return {'podcasts': podcasts, 'total_pages': total_pages}
    
    def get_username_from_id(self, user_id: str) -> str:
        """Get username from Firestore"""
        doc_ref = self.db.collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()['username']
        return "unknown"
    
    def get_user_info(self, user_id: str) -> Dict:
        """Get user information from Firestore"""

        # get user info
        info = {}
        doc_ref = self.db.collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            info = doc.to_dict()
        
        # get image if exists
        try:
            blob = self.bucket.blob(f'users/{user_id}/image.png')
            info['image'] = blob.generate_signed_url(expiration=datetime.timedelta(hours=1))
        except NotFound:
            info['image'] = None
        
        return info
    
    def like_podcast(self, user_id: str, podcast_id: str):
        """Like a podcast"""

        # podcasts database
        doc_ref = self.db.collection('podcasts').document(podcast_id)
        doc = doc_ref.get()
        if doc.exists:
            podcast = doc.to_dict()
            if user_id not in podcast['liked_by']:
                podcast['liked_by'].append(user_id)
                podcast['likes'] = len(podcast['liked_by'])
                doc_ref.update(podcast)
        
        # users database
        doc_ref = self.db.collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            user = doc.to_dict()
            if podcast_id not in user['liked_podcasts']:
                user['liked_podcasts'].append(podcast_id)
                doc_ref.update(user)


    def unlike_podcast(self, user_id: str, podcast_id: str):
        """Unlike a podcast"""

        # podcasts database
        doc_ref = self.db.collection('podcasts').document(podcast_id)
        doc = doc_ref.get()
        if doc.exists:
            podcast = doc.to_dict()
            if user_id in podcast['liked_by']:
                podcast['liked_by'].remove(user_id)
                podcast['likes'] = len(podcast['liked_by'])
                doc_ref.update(podcast)
        
        # users database
        doc_ref = self.db.collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            user = doc.to_dict()
            if podcast_id in user['liked_podcasts']:
                user['liked_podcasts'].remove(podcast_id)
                doc_ref.update(user)
    
    def get_liked_podcasts(self, user_id: str, page: int = 0, per_page: int = 10) -> List[Dict[str, str]]:
        """Get all podcasts liked by a user"""
        docs = self.db.collection('podcasts').where('liked_by', 'array_contains', user_id).stream()
        podcasts = []
        user_ids_to_usernames = {}

        for doc in docs:
            podcast = doc.to_dict()
            podcast['id'] = doc.id
            if podcast['user_id'] not in user_ids_to_usernames:
                user_ids_to_usernames[podcast['user_id']] = self.get_username_from_id(podcast['user_id'])
            podcast['username'] = user_ids_to_usernames[podcast['user_id']]
            podcasts.append(podcast)
        
        total_pages = len(podcasts) // per_page
        if page != 0:
            start = (page - 1) * per_page
            end = start + per_page
            podcasts = podcasts[start:end]
        
        if page == 0:
            return podcasts
        return {'podcasts': podcasts, 'total_pages': total_pages}
    
    def use_token(self, user_id: str) -> bool:
        """Use a token to generate a podcast"""
        doc_ref = self.db.collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            user = doc.to_dict()
            if user['tokens'] > 0:
                user['tokens'] -= 1
                doc_ref.update(user)
                return True
        return False
    
    def create_user(self, user_id: str, username: str):
        """Create a new user"""
        doc_ref = self.db.collection('users').document(user_id)
        doc_ref.set({
            'username': username,
            'tokens': 5,
            'liked_podcasts': []
        })


    def get_podcast_info(self, user_id:str, podcast_id: str) -> Dict:
        """Get podcast information from Firestore"""
        doc_ref = self.db.collection('podcasts').document(podcast_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def get_podcast_status(self, user_id:str, podcast_id: str) -> str:
        """Get podcast status from Firestore"""
        doc_ref = self.db.collection('podcasts').document(podcast_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()['status']
        return None
    
    def set_error(self, user_id: str, podcast_id: str):
        """Set podcast status to error"""
        doc_ref = self.db.collection('podcasts').document(podcast_id)
        doc_ref.update({'status': 'error'})


# Create a global instance of FirebaseStorage
firebase_storage = FirebaseStorage()