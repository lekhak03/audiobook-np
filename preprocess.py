import re
import unicodedata
import json
from pathlib import Path
import nltk, pdfplumber

nltk.download("punkt")
from nltk.tokenize import sent_tokenize
import wordninja

"""
This module provides utility functions to process a PDF and convert it into a
structured JSON format (chapters.json), followed by splitting the content into
smaller, manageable chunks for downstream tasks such as text-to-speech (TTS),
summarization, or semantic search.

Pipeline:
    1. Extract raw text from a PDF.
    2. Clean and normalize the text for consistency.
    3. Organize the text into chapters and save as chapters.json.
    4. Further split each chapter into chunks while preserving readability.

The functions ensure that formatting issues from PDFs (e.g., missing spaces,
hyphenated line breaks, merged words) are corrected to produce high-quality,
well-structured text output.
"""

# converts pdf to json
def pdf_to_json(pdf_path, json_path):
    """
    Extracts text from each page of a PDF and saves as a JSON list of strings.
    Args:
        pdf_path (str): Path to the PDF file.
        json_path (str): Path to save the JSON file.
    """
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            pages_text.append(text if text else "")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(pages_text, f, ensure_ascii=False, indent=2)
        
        
# cleaning the converted json
def split_merged_words_safe(text: str) -> str:
    words = []
    for word in text.split():
        if word.isalpha():
            words.extend(wordninja.split(word))
        else:
            words.append(word)
    return " ".join(words)

def fix_missing_spaces_after_punctuation(text: str) -> str:
    # Add a space after ., !, ? if not already followed by whitespace
    text = re.sub(r'([.!?])([^\s])', r'\1 \2', text)
    return text


def fix_pdf_line_breaks(text: str) -> str:
    text = re.sub(r"([a-zA-Z])\n([a-zA-Z])", r"\1\2", text)
    text = re.sub(r"-\n([a-zA-Z])", r"\1", text)
    text = re.sub(r"([A-Z])\n([A-Z])", r"\1 \2", text)
    return text


def normalize_whitespace(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)  # normalize Unicode
    text = re.sub(r"[\x00-\x1f\x7f]", "", text)  # remove control chars
    text = text.replace("\u00a0", " ")  # non-breaking space
    text = re.sub(r"\s+", " ", text)    # collapse whitespace
    return text.strip()


def clean_text_for_tts(text: str) -> str:
    if not text:
        return ""
    text = normalize_whitespace(text)
    text = fix_pdf_line_breaks(text)
    text = fix_missing_spaces_after_punctuation(text)
    # text = split_merged_words_safe(text)
    return text


def split_into_chunks_simple(text: str, sentences_per_chunk: int = 2):
    # Fix line breaks
    text = re.sub(r"([a-zA-Z])\n([a-zA-Z])", r"\1 \2", text)
    text = re.sub(r"-\n([a-zA-Z])", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Split by sentence-ending punctuation (.!?)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Group into chunks of N sentences
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk_text = " ".join(sentences[i:i + sentences_per_chunk])
        chunks.append(chunk_text.strip())

    return chunks


def preprocess_book_into_chunks(input_path: str, output_path: str, sentences_per_chunk: int = 2):
    """Load chapters.json and convert into nested JSON with chapter -> chunks."""
    # Load chapters.json
    with open(input_path, "r", encoding="utf-8") as f:
        raw_chapters = json.load(f)

    book_chunks = {}

    for chapter_idx, raw_text in enumerate(raw_chapters, start=1):
        # Clean the chapter text for TTS
        clean_text = clean_text_for_tts(raw_text)
        # Split into 2-sentence chunks
        sentence_chunks = split_into_chunks_simple(clean_text, sentences_per_chunk)


        # Build dictionary for chunks in this chapter
        chunk_dict = {}
        for i, chunk_text in enumerate(sentence_chunks, start=1):
            chunk_id = f"ch{chapter_idx}_{i:03}"
            chunk_dict[f"chunk_{i}"] = {
                "id": chunk_id,
                "text": chunk_text,
                "wav_audio": f"{chunk_id}.wav"  # placeholder for generated audio
            }

        book_chunks[f"chapter_{chapter_idx}"] = chunk_dict
        
    # Save JSON
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(book_chunks, f, ensure_ascii=False, indent=2)

    print(f"✅ Preprocessed book with chunks saved to {output_path}")


preprocess_book_into_chunks("chapters.json", "atomic-habits-chunks.json", sentences_per_chunk=2)
