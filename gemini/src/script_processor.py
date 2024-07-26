from collections import OrderedDict

SPEAKER_MAPPING = {
    "Male Host": "male_host",
    "Female Host": "female_host",
    "male host": "male_host",
    "female host": "female_host",
    "Male_Host": "male_host",
    "Female_Host": "female_host",
    "male_host": "male_host",
    "female_host": "female_host",
    "male": "male_host",
    "female": "female_host",
}

def standardize_speaker_name(speaker: str) -> str:
    return SPEAKER_MAPPING.get(speaker, "unknown_speaker")

def process_script_line(line: dict) -> dict:
    processed_line = {}
    speaker = line.pop("speaker", None)
    if speaker:
        standard_speaker = standardize_speaker_name(speaker)
        if "text" in line and isinstance(line["text"], dict):
            processed_line[standard_speaker] = line["text"].pop("text", "")
        else:
            processed_line[standard_speaker] = line.pop(speaker, "")
    return processed_line or line

def standardize_script_format(script: dict) -> dict:
    # Copy the keys of the original script in the original order
    original_order = list(script.keys())
    
    standardized_script = OrderedDict()
    for section, lines in script.items():
        try:
            standardized_section = {section: [process_script_line(line) for line in lines if line]}
            standardized_script.update(standardized_section)
        except Exception as e:
            continue
    
    standardized_script = fix_host_names(standardized_script)
    
    # Reorder the standardized_script to match the original order
    ordered_standardized_script = OrderedDict()
    for section in original_order:
        if section in standardized_script:
            ordered_standardized_script[section] = standardized_script[section]
    
    return ordered_standardized_script

def fix_host_names(script: dict) -> dict:
    for section in script.values():
        for item in section:
            keys_to_update = [key for key in item if key in SPEAKER_MAPPING]
            for key in keys_to_update:
                item[SPEAKER_MAPPING[key]] = item.pop(key)
    return script