import argparse
import json
import logging
import time
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

class PodcastGenerationRequest(BaseModel):
    subject: str

import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    SafetySetting,
    HarmCategory,
    HarmBlockThreshold,
    Content,
    Part,
)

# Configuration
PROJECT_ID = "podai-425012"
LOCATION = "us-central1"
MODEL_NAME = "gemini-1.5-flash-001"
MAX_RETRIES = 3
RETRY_DELAY = 30

# Model configurations
GENERATION_CONFIG = {
    "temperature": 0.7,
    "response_mime_type": "application/json",
}

SAFETY_SETTINGS = [
    SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
    SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
]

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIModelError(Exception):
    """Custom exception for AI model related errors."""
    pass

class PodcastGenerator:
    def __init__(self):
        self.initialize_vertexai()
        self.json_model = self.create_model(GENERATION_CONFIG)
        self.main_model = self.create_model(GENERATION_CONFIG)
        self.chat_session = None

    @staticmethod
    def initialize_vertexai():
        vertexai.init(project=PROJECT_ID, location=LOCATION)

    @staticmethod
    def create_model(config: Dict) -> GenerativeModel:
        return GenerativeModel(
            model_name=MODEL_NAME,
            safety_settings=SAFETY_SETTINGS,
            generation_config=config,
        )

    @staticmethod
    def retry_operation(func: callable, *args, **kwargs) -> Any:
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    # If e contains 429
                    if "429" in str(e):
                        logger.warning(f"Rate limit exceeded. Retrying in {RETRY_DELAY} seconds...")
                        time.sleep(RETRY_DELAY)
                    else:
                        raise AIModelError(f"Failed to execute operation: {e}")
                else:
                    logger.error(f"Error: Maximum number of attempts reached. {e}")
                    raise AIModelError(f"Failed to execute operation after {MAX_RETRIES} attempts: {e}")
        return None

    def generate_content(self, prompt: str) -> Optional[str]:
        response = self.retry_operation(self.json_model.generate_content, prompt)
        return response.text.strip() if response else None

    @staticmethod
    def parse_json_response(response: str) -> Optional[Dict]:
        try:
            return json.loads(response.replace("```json", "").replace("```", ""))
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON response.")
            return None

    def generate_sections(self, subject: str) -> Optional[List[str]]:
        sections_prompt = f"""
        Generate a detailed outline for a podcast script on the subject "{subject}". 
        The outline should include many fine-grained sections that cover various aspects of the topic comprehensively.
        Provide the output as a JSON array with a string for each section's title.
        """
        sections_response = self.generate_content(sections_prompt)
        return self.parse_json_response(sections_response) if sections_response else None

    def generate_script_part(self, message: str) -> Optional[Dict]:
        format = "Format: {section_title: [{'male_host': '...'}, {'female_host': '...'}, {'male_host': '...'}, {'female_host': '...'}, {'male_host': '...'}, {'female_host': '...'}, ...]}"
        for _ in range(3):  # Intentar hasta 3 veces
            response = self.retry_operation(self.chat_session.send_message, message + format)
            if response and response.text:
                try:
                    return self.parse_json_response(response.text)
                
                except ValueError:
                    continue
        return None

    def generate_detailed_section(self, subject: str, section_title: str) -> Optional[Dict]:
        section_prompt = f"""
        Based on the subject "{subject}" and the section title "{section_title}", write a detailed section for a podcast.
        Alternate between Male Host and Female Host. Provide multiple viewpoints, subpoints, and examples. Be simple with your sentences, 
        be aware this will be spoken and it has to sound natural. Male Host has a host role where he usually drives the conversation, while
        Female Host explains and adds more details, but this can be flexible. Conversation needs to be engaging and informative, but not too formal, and natural.
        """

        for i in range(3):
            segment_prompt = f"{section_prompt}\nSegment {i+1}:\nMale Host: (start discussing)\nFemale Host: (continue)\nMale Host: (add more details)"
            segment_content = self.generate_script_part(segment_prompt)
            
            if not segment_content:
                logger.error("Failed to generate segment content.")
            else:
                return segment_content
            
        return None
            
            

    async def generate_podcast_script(self, request: str) -> Optional[Dict]:
        subject = request
        logger.info(f"Generating podcast script for subject: {subject}")

        try:
            logger.info("Generating sections...")
            sections = self.generate_sections(subject)
            if not sections:
                logger.error("Failed to generate sections")
                return None

            self.chat_session = self.main_model.start_chat(history=[])

            logger.info("Generating introduction...")
            intro_prompt = self.create_intro_prompt(subject, sections)

            max_attempts = 3
            attempts = 0
            introduction = None
            full_script = {}

            section_number = 1


            """ INTRODUCTION IS AGAIN DONE AS SECTION
            while attempts < max_attempts:
                introduction = self.generate_script_part(intro_prompt)
                if introduction:
                    break
                attempts += 1
                logger.warning(f"Attempt {attempts} failed to generate introduction")

            if not introduction:
                logger.error("Failed to generate introduction after 3 attempts")
                return None

            introduction = {f"{section_number:03d}_{list(introduction.keys())[0]}": list(introduction.values())[0]}
            full_script.update(introduction)
            
            section_number += 1
            """

            for i, section_title in enumerate(sections, 1):
                logger.info(f"Generating section {i}...")
                attempts = 0
                max_attempts = 3    # It can fail
                section_content = None

                while attempts < max_attempts:
                    section_content = self.generate_detailed_section(subject, section_title)
                    if section_content:
                        break
                    attempts += 1
                    logger.warning(f"Attempt {attempts} failed for section {i}. Retrying...")

                if not section_content:
                    logger.error(f"Failed to generate section {i} after {max_attempts} attempts")
                    return None

                section_content = {f"{section_number:03d}_{list(section_content.keys())[0]}": list(section_content.values())[0]}
                full_script.update(section_content)
                section_number += 1


            """
            logger.info("Generating conclusion...")
            conclusion_prompt = self.create_conclusion_prompt(subject, sections)

            max_attempts = 3
            attempts = 0
            conclusion = None

            while attempts < max_attempts:
                conclusion = self.generate_script_part(conclusion_prompt)
                if conclusion:
                    break
                attempts += 1
                logger.warning(f"Attempt {attempts} failed to generate conclusion")

            if not conclusion:
                logger.error("Failed to generate conclusion after 3 attempts")
                return None

            conclusion = {f"{section_number:03d}_{list(conclusion.keys())[0]}": list(conclusion.values())[0]}
            full_script.update(conclusion)
            """


            return full_script
        
        except Exception as e:
            logger.exception(f"An error occurred while generating the podcast script: {e}")
            return None


    @staticmethod
    def create_intro_prompt(subject: str, sections: List[str]) -> str:
        return f'Based on the subject "{subject}", write a detailed and engaging introduction for a podcast. Alternate between Male Host and Female Host. Be simple with your sentences, be aware this will be spoken and it has to sound natural. Here is the outline for reference:\n{json.dumps(sections)}\n\nMale Host: (start the introduction)\nFemale Host: (continue the introduction)'

    @staticmethod
    def create_conclusion_prompt(subject: str, sections: List[str]) -> str:
        return f'Based on the subject "{subject}", write a conclusion for the podcast. Summarize the key points discussed and provide final thoughts or actionable insights. Alternate between Male Host and Female Host. Be simple with your sentences, be aware this will be spoken and it has to sound natural\n\nOutline: {json.dumps(sections)}\n\nMale Host: (start the conclusion)\nFemale Host: (continue the conclusion)\nMale Host: (finish the conclusion)'

def main():
    parser = argparse.ArgumentParser(description='Generate a podcast script.')
    parser.add_argument('subject', type=str, help='The subject of the podcast')
    args = parser.parse_args()

    podcast_generator = PodcastGenerator()

    start_time = time.time()
    try:
        script = podcast_generator.generate_podcast_script(args.subject)
        if script:
            end_time = time.time()
            logger.info(f"Script generated successfully. Execution time: {end_time - start_time:.2f} seconds")
        else:
            logger.error("Failed to generate the complete script.")
    except AIModelError as e:
        logger.error(f"AI Model Error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")

if __name__ == "__main__":
    main()