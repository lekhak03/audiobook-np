import pdfplumber
import json
import wave
from piper import PiperVoice
import unicodedata

def pdf_to_json(pdf_path, json_path):
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            pages_text.append(text if text else "")  # handle None pages
    
    # Save list of strings to JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(pages_text, f, ensure_ascii=False, indent=2)

def prepare_for_tts(text):
    # Collapse multiple newlines into a single space
    clean_text = " ".join(text.splitlines())
    # Optionally normalize spaces
    clean_text = " ".join(clean_text.split())
    return clean_text

def clean_for_tts(text: str) -> str:
    # 1. Remove nulls and other control chars
    text = re.sub(r"[\x00-\x1f\x7f]", "", text)
    
    # 2. Normalize unicode (turns composed forms into canonical ones)
    text = unicodedata.normalize("NFKC", text)

    # 3. Replace “smart” punctuation with ASCII equivalents
    replacements = {
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
        "\u2018": "'",  # left single quote
        "\u2019": "'",  # right single quote / apostrophe
        "\u201c": '"',  # left double quote
        "\u201d": '"',  # right double quote
        "\u2026": "...",  # ellipsis
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text.strip()

def get_nth_page(json_path, n):
    """
    Get the n-th page text from a JSON file created by pdf_to_json.
    
    Args:
        json_path (str): Path to the JSON file.
        n (int): Page number (0-based index).
    
    Returns:
        str: Text of the n-th page.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        pages = json.load(f)
    
    if n < 0 or n >= len(pages):
        raise IndexError(f"Page {n} is out of range (total {len(pages)} pages).")
    
    return pages[n]


import re


# Segegrates PDF into chapter for chapter: Number + \n
# Args: pdf_path, json_path
def pdf_to_chapters(pdf_path):
    print("Working on it....\n")
    chapters = []
    current_chapter = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""

            # Split into "chapter marker" + rest
            parts = text.split("\n", 1)
            if len(parts) == 2:
                header = parts[0] + "\n"
                body = parts[1]

                # --- Step 1: fix broken words across newlines ---
                body = re.sub(r"([a-z])\n([a-z])", r"\1\2", body)   # join split lowercase words
                body = re.sub(r"([A-Z])\n([A-Z])", r"\1\2", body)   # join split uppercase words (e.g. W\nHY -> WHY)
                body = re.sub(r"-\n([a-zA-Z])", r"\1", body)        # remove hyphen + newline (e.g. sto-\nry -> story)

                # --- Step 2: replace all remaining newlines with spaces ---
                body = body.replace("\n", " ")

                text = header + body
            else:
                # no chapter header, just flatten text
                text = text.replace("\n", " ")

            # If page starts with "number + newline" → new chapter
            if re.match(r"^\d+\n", text.strip()):
                # Save previous chapter if not empty
                if current_chapter.strip():
                    chapters.append(current_chapter.strip())
                # Start new chapter
                text = re.sub(r"^(\d+)\n", r"Chapter \1\n", text.strip())
                current_chapter = text
            else:
                # Continuation of the same chapter
                current_chapter += "\n" + text

    # Append last chapter
    if current_chapter.strip():
        chapters.append(current_chapter.strip())
        

    for i in range(1, 10):
        text = chapters[i]
        # text = prepare_for_tts(text)
        text = clean_for_tts(text)
        voice = PiperVoice.load("en_US-ryan-high.onnx")
        with wave.open(f"chapter_{i}.wav", "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)
        print(f"Chapter {i} Done!")


pdf_to_chapters('atomic-habits.pdf')
print("Done\n")