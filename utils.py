import pdfplumber
import json, os
import wave
from piper import PiperVoice
import unicodedata
import re
import time

import soundfile as sf
import torch
import numpy as np
from pathlib import Path
from kokoro import KPipeline
pipeline = KPipeline(lang_code='a',) # <= make sure lang_code matches voice, reference above.

start_time = time.time()
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

import re
import unicodedata
import os
import re
import json
import torch
import numpy as np
import soundfile as sf
from pathlib import Path

def batch_tts_from_json(json_path, pipeline, voice_path, output_dir="output_audio", 
                        list_of_voices=None, max_chars=2000):
    """Generate batched TTS from JSON chapters using only 'content' field."""
    
    # Load chapters
    with open(json_path, "r", encoding="utf-8") as f:
        chapters = json.load(f)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    voice_tensor = torch.load(voice_path, weights_only=True)

    for ch_idx, chapter in enumerate(chapters):
        chapter_num = chapter.get("id", ch_idx + 1)
        chapter_text = chapter.get("content", "")

        # Split into smaller batches
        batches = [chapter_text[i:i+max_chars] for i in range(0, len(chapter_text), max_chars)]


        voice_name = (list_of_voices[ch_idx] if list_of_voices and ch_idx < len(list_of_voices) 
                      else f"chapter_{chapter_num}")
        chapter_audio, part_files = [], []

        for b_idx, batch_text in enumerate(batches):

            # Prepend "Chapter X" to the first batch
            if b_idx == 0:
                batch_text = f"{batch_text}"

            # Run TTS generator
            generator = pipeline(
                batch_text,
                voice=voice_tensor,
                speed=1,
                split_pattern=r'\n+'
            )

            for _, _, audio in generator:
                chapter_audio.append(audio)
                part_path = f"{output_dir}/{voice_name}_part{b_idx}.wav"
                sf.write(part_path, audio, 24000)
                part_files.append(part_path)

        # Join all batch audios
        if chapter_audio:
            full_audio = np.concatenate(chapter_audio)
            full_path = f"{output_dir}/{voice_name}_full.wav"
            sf.write(full_path, full_audio, 24000)
            print(f"✅ Saved {full_path} with {len(batches)} batches")

        # Delete temporary part files
        for part_path in part_files:
            try:
                os.remove(part_path)
            except Exception as e:
                print(f"⚠️ Could not delete {part_path}: {e}")
        exit()


voice_path = 'models--hexgrad--Kokoro-82M/snapshots/f3ff3571791e39611d31c381e3a41a3af07b4987/voices/bf_isabella.pt'
json_path_chapter = 'atomic-habits-processed.json'

batch_tts_from_json(json_path_chapter, pipeline, voice_path)
print(f"Program took: {time.time() - start_time} seconds to complete")