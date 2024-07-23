import json
import time
import random
import string
import os
import json
import piper
import wave
from pydub import AudioSegment
from typing import List, Dict
import logging

from src.models import Podcast

logger = logging.getLogger("uvicorn")

voices_folder = 'voices/'
voices = {
    "male": (voices_folder + "en_US-libritts-high.onnx", voices_folder + "en_US-libritts-high.onnx.json"),
    "female": (voices_folder + "en_GB-northern_english_male-medium.onnx", voices_folder + "en_GB-northern_english_male-medium.onnx.json")
}


def get_audio_files(path: str) -> List[str]:
    """
    Get a list of .wav files from the specified directory.

    :param path: The directory to search for .wav files.
    :return: A sorted list of .wav files.
    """
    try:
        files = [f for f in os.listdir(path) if f.endswith('.wav')]
        files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
        logger.info(f"Found {len(files)} .wav files in directory {path}")
        return files
    except Exception as e:
        logger.error(f"Error while getting audio files: {e}")
        return []

def concatenate_audio_files(files: List[str], path: str) -> AudioSegment:
    """
    Concatenate audio files into a single AudioSegment.

    :param files: The list of files to concatenate.
    :param path: The directory where the files are located.
    :return: The concatenated AudioSegment.
    """
    audio_files = []
    temp_audio_files_path = path + "temp/"

    for file in files:
        try:
            logger.debug(f"Loading file {file}")
            audio = AudioSegment.from_wav(temp_audio_files_path + file)
            audio_files.append(audio)
            logger.info(f"Successfully loaded file {file}")
        except Exception as e:
            logger.error(f"Error loading file {file}: {e}")
            continue

    return sum(audio_files, AudioSegment.empty())

def export_audio(audio: AudioSegment, path: str, filename: str) -> None:
    """
    Export an AudioSegment to a .wav file.

    :param audio: The AudioSegment to export.
    :param path: The directory to export the file to.
    :param filename: The name of the file to export.
    """
    try:
        logger.debug(f"Exporting audio to {path + filename}")
        audio.export(path + filename, format='wav')
        logger.info(f"Successfully exported audio to {path + filename}")
    except Exception as e:
        logger.error(f"Error exporting audio: {e}")

def remove_files(files: List[str], path: str) -> None:
    """
    Remove specified files from a directory.

    :param files: The list of files to remove.
    :param path: The directory where the files are located.
    """
    for file in files:
        try:
            logger.debug(f"Removing file {file}")
            os.remove(path + file)
            logger.info(f"Successfully removed file {file}")
        except Exception as e:
            logger.error(f"Error removing file {file}: {e}")

def concatenate_audio(path: str = 'podcasts/', filename: str = 'podcast.wav') -> None:
    """
    Concatenate .wav files in a directory into a single .wav file, then remove the original files.

    :param path: The directory to search for .wav files.
    :param filename: The name of the file to export.
    """
    temp_audio_files_path = path + "temp/"
    try:
        logger.debug("Getting audio files")
        files = get_audio_files(temp_audio_files_path)
        logger.info(f"Got {len(files)} audio files")

        logger.debug("Concatenating audio files")
        combined = concatenate_audio_files(files, path)
        logger.info("Successfully concatenated audio files")

        logger.debug(f"Exporting audio to {filename}")
        export_audio(combined, path, filename)
        logger.info(f"Successfully exported audio to {filename}")

        logger.debug("Removing original audio files")
        remove_files(files, temp_audio_files_path)
        logger.info("Successfully removed original audio files")

    except Exception as e:
        logger.error(f"Error in audio processing: {e}")




def generate_audio_for_host(host_sentences: Dict[str, str], voice_type: str, path: str) -> None:
    """
    Generate audio files for each sentence spoken by a host.

    :param host_sentences: A dictionary where keys are sentence IDs and values are sentences.
    :param voice_type: The type of voice to use ("male" or "female").
    """
    for sentence_id, sentence in host_sentences.items():
        output_file_sentence = f"{path}{sentence_id}.wav"
        voice = piper.PiperVoice.load(voices[voice_type][0], voices[voice_type][1], True)
        with open(output_file_sentence, 'wb') as f:
            with wave.open(f, 'wb') as wav:
                try:
                    logger.debug(f"Synthesizing audio for sentence {sentence_id}")
                    voice.synthesize(sentence, wav)
                    logger.info(f"Successfully synthesized audio for sentence {sentence_id}")
                except Exception as e:
                    logger.error(f"Error in generating audio for sentence {sentence_id}: {e}. Skipping to next sentence.")


def generate_audio(male_host: Dict[str, str], female_host: Dict[str, str], filename: str, path: str) -> None:
    """
    Generate audio files for each sentence spoken by the male and female hosts, then concatenate the audio files.

    :param male_host: A dictionary where keys are sentence IDs and values are sentences spoken by the male host.
    :param female_host: A dictionary where keys are sentence IDs and values are sentences spoken by the female host.
    """
    temp_audio_files_path = path + "temp/"
    if not os.path.exists(temp_audio_files_path):
        os.makedirs(temp_audio_files_path)
    else:
        for file in os.listdir(temp_audio_files_path):
            os.remove(temp_audio_files_path + file)

    generate_audio_for_host(male_host, "male", temp_audio_files_path)
    generate_audio_for_host(female_host, "female", temp_audio_files_path)
    concatenate_audio(path, filename)



def load_script(filename: str) -> Dict[str, str]:
    """
    Load a script from a JSON file.

    :param filename: The name of the JSON file.
    :return: A dictionary where keys are sentence IDs and values are sentences.
    """

    try:
        logger.debug(f"Opening file data/{filename}")
        with open('data/' + filename, "r") as script_file:
            script = json.load(script_file)
        logger.info(f"Successfully loaded script from data/{filename}")
        return script
    except Exception as e:
        logger.error(f"Error loading script from data/{filename}: {e}")

def split_script_by_host(script: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """
    Split a script into sentences spoken by the male host and sentences spoken by the female host.

    :param script: A dictionary where keys are sentence IDs and values are sentences.
    :return: A dictionary where keys are "male" and "female" and values are dictionaries where keys are sentence IDs and values are sentences.
    """
    male_host = {}
    female_host = {}
    line = 0

    for key in script.keys():   
        for i in script[key]:
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

    :param filename: The name of the script file.
    """
    data_path         = os.getenv("DATA_PATH", "/data")
    scripts_directory = f"{data_path}/{podcast.user_id}/scripts/"
    audios_directory  = f"{data_path}/{podcast.user_id}/audios/"
    script_filename   = f"script_{podcast.podcast_id}.json"
    audio_filename    = f"{podcast.podcast_id}.wav"
    user_id           = podcast.user_id
    podcast_id        = podcast.podcast_id


    try:
        start_time = time.time()

        # Load script
        logger.debug(f"Loading script from {script_filename}")
        script_path = f"{scripts_directory}/{script_filename}"

        if not os.path.exists(script_path):
            logger.error(f"Script not found: {script_path}")
            return

        with open(script_path, "r") as script_file:
            script = json.load(script_file)
        logger.info(f"Successfully loaded script {podcast.podcast_name}")

        # Split script by host
        logger.debug("Splitting script by host")
        # logger.info(f"AAAAAAAAAAAAAAAAAAAAAAAAAAAA {script}")
        hosts = split_script_by_host(script)
        logger.info("Successfully split script by host")

        logger.debug("Generating podcast")

        # Create directory if it doesn't exist
        if not os.path.exists(f"{data_path}/{user_id}/audios"):
            os.makedirs(f"{data_path}/{user_id}/audios")


        # Generate audio
        logger.debug("Generating audio")
        generate_audio(hosts["male"], hosts["female"], podcast_id + ".wav", f"{data_path}/{user_id}/audios/")
        logger.info("Successfully generated audio")

        end_time = time.time()
        logger.info(f"Podcast generated in {end_time - start_time:.2f} seconds.")
    except Exception as e:
        logger.error(f"Error in generating podcast: {e}")

