import re
import unicodedata
import json
from pathlib import Path

import re
import unicodedata
import json
from pathlib import Path
import wordninja

def clean_for_tts(text: str) -> str:
    """Clean text for TTS input and fix merged words."""
    if not text:
        return ""

    # Remove control characters
    text = re.sub(r"[\x00-\x1f\x7f]", "", text)

    # Normalize Unicode
    text = unicodedata.normalize("NFKC", text)

    # Replace smart punctuation
    replacements = {
        "\u2013": "-", "\u2014": "-", "\u2015": "-", "\u2212": "-",
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2026": "...",
        "\u00a0": " ", "\u200b": "", "\u200c": "", "\u200d": "",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Fix PDF line break artifacts
    # Fix PDF line break artifacts
    text = re.sub(r"([a-zA-Z])\n([a-zA-Z])", r"\1\2", text)  # join wrapped words
    text = re.sub(r"-\n([a-zA-Z])", r"\1", text)             # remove hyphenated line breaks
    text = re.sub(r"([A-Z])\n([A-Z])", r"\1 \2", text)       # separate acronyms

    # Remove unwanted special characters, but don't split words with spaces
    text = re.sub(r"[^a-zA-Z0-9,.!?;:'\"\s]", "", text)

    # Now split merged words
    text = " ".join([w for word in text.split() for w in wordninja.split(word)])


    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()



def preprocess_book_json(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        raw_chapters = json.load(f)

    structured_chapters = []

    for idx, raw_text in enumerate(raw_chapters, start=1):
        lines = raw_text.split("\n")
        chapter_num = idx
        chapter_title_text = f"Chapter {idx}"
        content_raw = raw_text

        # If first line is a number, try extracting title
        if len(lines) >= 2 and lines[0].strip().isdigit():
            chapter_num = int(lines[0].strip())
            # Take all lines after number until the first line that looks like content
            title_lines = []
            content_start_idx = 1
            for i in range(1, len(lines)):
                line = lines[i].strip()
                if line == "":
                    continue
                # Heuristic: if line starts with capital letter and likely content, stop title
                if re.match(r"^[A-Z0-9]", line):
                    content_start_idx = i
                    break
                title_lines.append(line)
            # If title_lines empty, take second line
            if not title_lines:
                title_lines = [lines[1].strip()]
                content_start_idx = 2
            chapter_title_text = " ".join(title_lines)
            content_raw = "\n".join(lines[content_start_idx:])

        # Clean only the content
        content = clean_for_tts(content_raw)

        chapter_title = f"Chapter {chapter_num}: {chapter_title_text}"

        structured_chapters.append({
            "id": chapter_num,
            "chapter_title": chapter_title,
            "content": chapter_title + '. ' + content
        })

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(structured_chapters, f, ensure_ascii=False, indent=2)

    print(f"✅ Preprocessed book saved to {output_path}")




preprocess_book_json('chapters.json', 'atomic-habits-processed.json')
