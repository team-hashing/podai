import datetime
import os
import json
from typing import Dict, List, Optional
import firebase_admin
from firebase_admin import credentials, storage, firestore
from google.cloud.exceptions import NotFound
import logging
from PIL import Image as PILImage
from io import BytesIO
from vertexai.preview.vision_models import GeneratedImage
import tempfile


logger = logging.getLogger(__name__)
FIREBASE_KEY = os.environ.get('FIREBASE_KEY')
STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')

class FirebaseStorage:
    def __init__(self):
        # Initialize Firebase app if not already initialized
        if not firebase_admin._apps:
            # open file and load as json
            with open(FIREBASE_KEY, 'r') as file:
                cred = credentials.Certificate(json.load(file))
            firebase_admin.initialize_app(cred, {
                'storageBucket': STORAGE_BUCKET
            })
        
        self.bucket = storage.bucket()
        self.db = firestore.client()

        # get all elements from collection podcasts and add update them so they inlcude the fields (if they dont have them already) "likes: 0" and "liked_by: []", 
        # created_at: timestamp (1 of january of 1970), druration: 1000
        podcasts = self.db.collection('podcasts').stream()

    async def save_podcast(self, user_id: str, podcast_id: str, script_content: Dict):
        """Save podcast details to Firestore"""
        try:
            doc_ref = self.db.collection('podcasts').document(podcast_id)
            doc_ref.update({
                'script': script_content,
            })
            logger.info(f'Podcast saved for ID: {podcast_id}')
        except Exception as e:
            logger.error(f'Failed to save podcast: {str(e)}')
            raise
    
    async def save_image(self, user_id: str, podcast_id: str, image_data):
        """Save image to Firebase Storage"""
        try:
            # Create a temporary directory if it does not exist
            temp_dir = tempfile.gettempdir()
            temp_image_path = os.path.join(temp_dir, f'{podcast_id}.png')

            # Save the image locally
            image_data.save(temp_image_path)

            # Read the image data from the local file
            with open(temp_image_path, 'rb') as image_file:
                image_bytes = image_file.read()

            # Upload the image to Firebase Storage
            blob = self.bucket.blob(f'podcasts/{podcast_id}/image.png')
            blob.upload_from_string(image_bytes, content_type='image/png')
            logger.info(f'Image saved for podcast ID: {podcast_id}')

            # Delete the local image file
            os.remove(temp_image_path)
        except Exception as e:
            logger.error(f'Failed to save image: {str(e)}')
    
        """
        # Save the image to a file
        for i, image in enumerate(images):
            image.save("output_{}.png".format(i))
        """
