import argparse
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, HarmCategory, HarmBlockThreshold
# ModelContent
from vertexai.generative_models._generative_models import Content, Part


import json
import time

# TODO(developer): Update and un-comment below line
project_id = "podai-425012"

vertexai.init(project=project_id, location="us-central1")

#### CONFIGS ####################

generation_config = {
    "temperature": 0.7,
    # "top_p": 0.9,
    # "top_k": 40,
    # "max_output_tokens": 1024,
    "response_mime_type": "application/json",
}

safety_settings = [
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
]


model = GenerativeModel(
    model_name="gemini-1.5-flash-001",
    # safety_settings=safety_settings,
    generation_config=generation_config,

)

# Separate model configuration for generating JSON
json_generation_config = {
    "temperature": 0.7,
    # "top_p": 0.9,
    # "top_k": 40,
    # "max_output_tokens": 1024,
    "response_mime_type": "application/json",
}

json_model = GenerativeModel(
    model_name="gemini-1.5-flash-001",
    # safety_settings=safety_settings,
    generation_config=json_generation_config,
)


def generate_script_part(chat_session, message):
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = chat_session.send_message(message)
            break
        except Exception as e:
            if attempt < max_attempts - 1:  # if it's not the last attempt
                for i in range(30, 0, -1):
                    print(f"Max uses per minute: Retrying in {i} seconds...", end='\r')
                    time.sleep(1)
                print()
            else:
                print("Error: Maximum number of attempts reached.")
                return None
    else:
        print("No response received.")
        return None

    if response.text:
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            print("AAAA JSON FAIL: ", response.text)
            print("Failed to decode JSON response.")
            return None


def generate_sections(subject):
    sections_prompt = f"""
    Generate a detailed outline for a podcast script on the subject "{subject}". 
    The outline should include many fine-grained sections that cover various aspects of the topic comprehensively.
    Provide the output as a JSON array with a string for each section's title.
    """
    # Create a Part object
    part = Part.from_text("sections_prompt")

    # Create a Content object
    # content = Content(role="user", parts=[part])

    # sections_response = json_model.start_chat(history=[content]).send_message(sections_prompt)

    sections_response = json_model.generate_content(sections_prompt)
    return sections_response.text.strip()

def generate_detailed_section(chat_session, subject, section_title):
    section_prompt = f"""
    Based on the subject "{subject}" and the section title "{section_title}", write a detailed section for a podcast.
    Alternate between Male Host and Female Host. Provide multiple viewpoints, subpoints, and examples. Be simple with your sentences, be aware this will be spoken and it has to sound natural.
    """
    detailed_content = {}
    # Generate content in smaller segments
    for i in range(2):  # Adjust the range if needed
        segment_prompt = f"{section_prompt}\nSegment {i+1}:\nMale Host: (start discussing)\nFemale Host: (continue)\nMale Host: (add more details)"
        segment_content = generate_script_part(chat_session, segment_prompt)
        if not segment_content:
            print("Failed to generate segment content.")
            return None

        if section_title not in detailed_content.keys():
            detailed_content.update(segment_content)
        
        else:
            # TODO No me fio de que esto este bien
            if isinstance(detailed_content[section_title], str):
                # Convert string to list
                detailed_content[section_title] = [detailed_content[section_title]]
            detailed_content[section_title].extend(segment_content[section_title])
    
    return detailed_content

def generate_podcast_script(subject):

    # Generate podcast structure
    print("AAA Geneating sections...")
    sections_response = generate_sections(subject)

    # Parse the JSON response
    try:
        sections_response = sections_response.replace("```json", "").replace("```", "")
        sections = json.loads(sections_response)
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
        return None

    # Initialize chat session with the main model
    chat_session = model.start_chat(history=[])

    # Step 2: Generate the Introduction
    intro_prompt = f'Based on the subject "{subject}", write a detailed and engaging introduction for a podcast. Alternate between Male Host and Female Host. Be simple with your sentences, be aware this will be spoken and it has to sound natural. Here is the outline for reference:\n{json.dumps(sections)}\n\nMale Host: (start the introduction)\nFemale Host: (continue the introduction)'
    print("AAA Generating script...")
    introduction = generate_script_part(chat_session, intro_prompt)

    # Step 3: Generate the Detailed Discussions
    full_script = {}
    full_script = introduction

    for i, section_title in enumerate(sections):
        print(f"AAA Generating section {i}...")
        section_content = generate_detailed_section(chat_session, subject, section_title)
        if section_content is None:
            print("Failed to generate detailed section.")
            return None
        else:
            full_script.update(section_content)

    # Step 4: Generate the Conclusion
    conclusion_prompt = f'Based on the subject "{subject}", write a conclusion for the podcast. Summarize the key points discussed and provide final thoughts or actionable insights. Alternate between Male Host and Female Host. Be simple with your sentences, be aware this will be spoken and it has to sound natural\n\nOutline: {json.dumps(sections)}\n\nMale Host: (start the conclusion)\nFemale Host: (continue the conclusion)\nMale Host: (finish the conclusion)'
    print("AAA Generating conclusion...")
    conclusion = generate_script_part(chat_session, conclusion_prompt)

    full_script.update(conclusion)
    # Save the script to a file
    with open("script.json", "w") as script_file:
        script_file.write(json.dumps(full_script))  # Convert the dictionary to a string before writing

    return full_script


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a podcast script.')
    parser.add_argument('subject', type=str, help='The subject of the podcast')

    args = parser.parse_args()


    start_time = time.time()

    script = generate_podcast_script(args.subject)

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Execution time: {execution_time} seconds")