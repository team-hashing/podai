import json
import time
import os
import piper
import wave
from pydub import AudioSegment
from typing import List, Dict
import logging
from io import BytesIO
import random

from src.models import Podcast
from src.storage import FirebaseStorage

logger = logging.getLogger("uvicorn")
firebase_storage = FirebaseStorage()

voices_folder = 'voices/'
"""
voices = {
    "male": (voices_folder + "en_US-libritts-high.onnx", voices_folder + "en_US-libritts-high.onnx.json"),
    "female": (voices_folder + "en_GB-northern_english_male-medium.onnx", voices_folder + "en_GB-northern_english_male-medium.onnx.json")
}
"""
voices = {
    "male": (voices_folder + "male.onnx", voices_folder + "male.json"),
    "female": (voices_folder + "female.onnx", voices_folder + "female.json")
}

def get_audio_files(user_id: str, podcast_id: str) -> List[BytesIO]:
    """
    Get a list of .wav files from Firebase Storage.

    :param user_id: The user ID.
    :param podcast_id: The podcast ID.
    :return: A sorted list of .wav files as BytesIO objects.
    """
    try:
        files = firebase_storage.list_temp_audio_files(user_id, podcast_id)
        files = [file.split('/')[-1] for file in files if file.endswith('.wav')]


        # sort files by string order
        files.sort()
        logger.info(f"Found {len(files)} .wav files for podcast {podcast_id}")
        
        audio_files = []
        for file in files:
            logger.debug(f"Attempting to load audio file: {file}")
            audio_file = firebase_storage.get_temp_audio_file(user_id, podcast_id, file)
            if audio_file is None:
                logger.error(f"Error loading audio file: {file}")
            else:
                audio_files.append(audio_file)
        
        return audio_files
    
    except Exception as e:
        logger.error(f"Error while getting audio files: {e}")
        return []


def concatenate_audio_files(files: List[BytesIO]) -> AudioSegment:
    """
    Concatenate audio files into a single AudioSegment, starting with a random intro melody.

    :param files: The list of BytesIO objects to concatenate.
    :return: The concatenated AudioSegment.
    """
    audio_files = []

    # Select a random intro melody from the 'audios' folder
    intro_folder = 'audios'
    intro_files = [f for f in os.listdir(intro_folder) if f.endswith('.wav')]
    if intro_files:
        intro_file_path = os.path.join(intro_folder, random.choice(intro_files))
        try:
            logger.debug(f"Loading intro melody from {intro_file_path}")
            intro_audio = AudioSegment.from_wav(intro_file_path)
            intro_audio = intro_audio.fade_out(duration=2000)  # Fade out in the last 2 seconds
            audio_files.append(intro_audio)
            logger.info(f"Successfully loaded intro melody")
        except Exception as e:
            logger.error(f"Error loading intro melody: {e}")

    for file in files:
        try:
            if isinstance(file, bytes):
                file = BytesIO(file)
            elif not isinstance(file, BytesIO):
                logger.error(f"Invalid file type: {type(file)}. Expected BytesIO or bytes.")
                continue
            
            logger.debug(f"Loading audio file")
            file.seek(0)  # Ensure the file pointer is at the beginning
            audio = AudioSegment.from_wav(file)
            audio_files.append(audio)
            logger.info(f"Successfully loaded audio file")
            
        except Exception as e:
            logger.error(f"Error loading audio file: {e}")
            continue

    return sum(audio_files, AudioSegment.empty())

def export_audio(audio: AudioSegment, user_id: str, podcast_id: str) -> None:
    """
    Export an AudioSegment to Firebase Storage.

    :param audio: The AudioSegment to export.
    :param user_id: The user ID.
    :param podcast_id: The podcast ID.
    """
    try:
        logger.debug(f"Exporting audio for podcast {podcast_id}")
        buffer = BytesIO()
        audio.export(buffer, format='wav')
        firebase_storage.save_audio(user_id, podcast_id, buffer.getvalue())
        logger.info(f"Successfully exported audio for podcast {podcast_id}")
    except Exception as e:
        logger.error(f"Error exporting audio: {e}")

def remove_temp_files(user_id: str, podcast_id: str) -> None:
    """
    Remove temporary audio files from Firebase Storage.

    :param user_id: The user ID.
    :param podcast_id: The podcast ID.
    """
    try:
        logger.debug(f"Removing temporary files for podcast {podcast_id}")
        firebase_storage.remove_temp_audio_files(user_id, podcast_id)
        logger.info(f"Successfully removed temporary files for podcast {podcast_id}")
    except Exception as e:
        logger.error(f"Error removing temporary files: {e}")

def concatenate_audio(user_id: str, podcast_id: str) -> None:
    """
    Concatenate .wav files in Firebase Storage into a single .wav file, then remove the original files.

    :param user_id: The user ID.
    :param podcast_id: The podcast ID.
    """
    try:
        logger.debug("Getting audio files")
        files = get_audio_files(user_id, podcast_id)
        logger.info(f"Got {len(files)} audio files")

        logger.debug("Concatenating audio files")
        combined = concatenate_audio_files(files)
        logger.info("Successfully concatenated audio files")

        logger.debug(f"Exporting audio for podcast {podcast_id}")
        export_audio(combined, user_id, podcast_id)
        logger.info(f"Successfully exported audio for podcast {podcast_id}")

        logger.debug("Removing temporary audio files")
        remove_temp_files(user_id, podcast_id)
        logger.info("Successfully removed temporary audio files")

    except Exception as e:
        logger.error(f"Error in audio processing: {e}")

def generate_audio_for_host(host_sentences: Dict[str, str], voice_type: str, user_id: str, podcast_id: str) -> None:
    """
    Generate audio files for each sentence spoken by a host and save to Firebase Storage.

    :param host_sentences: A dictionary where keys are sentence IDs and values are sentences.
    :param voice_type: The type of voice to use ("male" or "female").
    :param user_id: The user ID.
    :param podcast_id: The podcast ID.
    """
    for sentence_id, sentence in host_sentences.items():
        voice = piper.PiperVoice.load(voices[voice_type][0], voices[voice_type][1], True)
        buffer = BytesIO()
        with wave.open(buffer, 'wb') as wav:
            try:
                logger.debug(f"Synthesizing audio for sentence {sentence_id}")
                voice.synthesize(sentence, wav)
                # if number is only less than 4 digits, add the corresponding ammount of 0 to the front
                if sentence_id < 1000:
                    sentence_id = f"{sentence_id:04}"
                logger.info(f"Successfully synthesized audio for sentence {sentence_id}")
                firebase_storage.save_temp_audio_file(user_id, podcast_id, f"{sentence_id}.wav", buffer.getvalue())
            except Exception as e:
                logger.error(f"Error in generating audio for sentence {sentence_id}: {e}. Skipping to next sentence.")

def generate_audio(male_host: Dict[str, str], female_host: Dict[str, str], user_id: str, podcast_id: str) -> None:
    """
    Generate audio files for each sentence spoken by the male and female hosts, then concatenate the audio files.

    :param male_host: A dictionary where keys are sentence IDs and values are sentences spoken by the male host.
    :param female_host: A dictionary where keys are sentence IDs and values are sentences spoken by the female host.
    :param user_id: The user ID.
    :param podcast_id: The podcast ID.
    """
    generate_audio_for_host(male_host, "male", user_id, podcast_id)
    generate_audio_for_host(female_host, "female", user_id, podcast_id)
    concatenate_audio(user_id, podcast_id)

def split_script_by_host(script: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """
    Split a script into sentences spoken by the male host and sentences spoken by the female host.

    :param script: A dictionary where keys are sentence IDs and values are sentences.
    :return: A dictionary where keys are "male" and "female" and values are dictionaries where keys are sentence IDs and values are sentences.
    """
    male_host = {}
    female_host = {}
    line = 0

    for section_name in script.keys():   
        for i in script[section_name]:
            line += 1
            try:
                logger.debug(f"Processing line {line}")
                if "male_host" in i:
                    male_host[line] = i['male_host']
                    logger.info(f"Added line {line} to male_host")
                elif "female_host" in i:
                    female_host[line] = i['female_host']
                    logger.info(f"Added line {line} to female_host")
            except Exception as e:
                logger.error(f"Error processing line {line}: {e}")
                continue

    return {"male": male_host, "female": female_host}

def generate_podcast(podcast: Podcast) -> None:
    """
    Generate a podcast from a script.

    :param podcast: The Podcast object containing podcast information.
    """
    try:
        start_time = time.time()

        # Load script from Firebase
        script = firebase_storage.get_script(podcast.user_id, podcast.podcast_id)
        if script is None:
            logger.error(f"Script not found: {podcast.podcast_id}")
            return
        
        # order the script by section names
        script = {k: script[k] for k in sorted(script.keys())}

        logger.info(f"Successfully loaded script {podcast.podcast_name}")


        # Split script by host
        logger.debug("Splitting script by host")
        hosts = split_script_by_host(script)
        logger.info("Successfully split script by host")

        logger.debug("Generating podcast")

        # Generate audio
        logger.debug("Generating audio")
        generate_audio(hosts["male"], hosts["female"], podcast.user_id, podcast.podcast_id)
        logger.info("Successfully generated audio")

        end_time = time.time()
        logger.info(f"Podcast generated in {end_time - start_time:.2f} seconds.")
    except Exception as e:
        logger.error(f"Error in generating podcast: {e}")