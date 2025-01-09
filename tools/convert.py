import json, re
import sys, os

if len(sys.argv) != 3:
    print(f"Usage: {__file__} <input_file> <output_file>")
    sys.exit(1)

file_path = os.path.join(os.path.dirname(__file__), 'data.json')
input_text_file = sys.argv[1]
output_text_file = sys.argv[2]


# Function to create the character-to-pronunciation map
def create_char_pronunciation_map(data):
    char_to_pronunciation = {}

    for entry in data:
        characters = entry.get("字頭", [])
        pronunciations = []

        # Extract pronunciations from "義項"
        for meaning in entry.get("義項", []):
            for reading in meaning.get("讀音", []):
                pronunciation = reading.get("粵拼讀音")
                if pronunciation:
                    pronunciations.append(pronunciation)

        # Map each character to its pronunciations
        for char in characters:
            char_to_pronunciation[char] = pronunciations
        
        # Add pronunciations for "異體"
        variants = entry.get("_校訂補充", {}).get("異體", [])
        for variant in variants:
            if variant not in char_to_pronunciation:
                char_to_pronunciation[variant] = pronunciations

    return char_to_pronunciation

# Read JSON data from a file
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Replace characters in text with <ruby> tags within <body> tag
# Handle body tag with class or attributes
def replace_characters_with_ruby_in_body(text, char_map):
    def replace_in_body(match):
        body_tag_open = match.group(1)
        body_content = match.group(2)
        replaced_content = []
        for char in body_content:
            if re.match(r"[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df\u2a700-\u2b73f\u2b740-\u2b81f\uf900-\ufaff]", char) and char in char_map:
                pronunciation = char_map[char][0]  # Use the first pronunciation if available
                replaced_content.append(f"<ruby>{char}<rt>{pronunciation}</rt></ruby>")
            else:
                replaced_content.append(char)
        return f"{body_tag_open}{''.join(replaced_content)}</body>"

    return re.sub(r"(<body[^>]*>)(.*?)(</body>)", replace_in_body, text, flags=re.DOTALL)


# Read the JSON data
json_data = read_json_file(file_path)

# Create the map
char_map = create_char_pronunciation_map(json_data)

# Read the input text
with open(input_text_file, 'r', encoding='utf-8') as file:
    input_text = file.read()

# Replace characters in the text
output_text = replace_characters_with_ruby_in_body(input_text, char_map)

# Write the output text to a file
with open(output_text_file, 'w', encoding='utf-8') as file:
    file.write(output_text)

print("Text replacement completed. Output written to", output_text_file)