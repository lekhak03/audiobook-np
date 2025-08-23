import time
from kokoro import KPipeline
from kokoro.model import KModel
my_model = KModel()

quie_pl = KPipeline(lang_code='a', model=False) # must do this so KPipeline knows no need to download the model

# make sure lang_code matches voice, reference above.
# use model='' to load a local pth model
pipeline = KPipeline(lang_code='a', model="models--hexgrad--Kokoro-82M/snapshots/f3ff3571791e39611d31c381e3a41a3af07b4987/kokoro-v1_0.pth")

start_time = time.time()

def chunk_tts_from_json(json_path, pipeline, voice_path, output_dir="output_audio"):
    """
    Generate TTS wav files for each chunk in a hierarchical chapters.json.
    JSON format:
    {
        "chapter_1": {
            "chunk_1": {
                "id": "ch1_001",
                "text": "...",
                "wav_audio": "ch1_001.wav"
            },
            ...
        },
        "chapter_2": { ... }
    }
    """

    import json, torch, os, soundfile as sf
    from pathlib import Path
    import numpy as np

    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        chapters = json.load(f)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    voice_tensor = torch.load(voice_path, weights_only=True)

    # Loop through chapters and chunks
    for chapter_key, chapter_content in chapters.items():
        for chunk_key, chunk in chapter_content.items():
            chunk_id = chunk.get("id", f"{chapter_key}_{chunk_key}")
            chunk_text = chunk.get("text", "")
            wav_filename = chunk.get("wav_audio", f"{chunk_id}.wav")
            wav_path = os.path.join(output_dir, wav_filename)

            if not chunk_text.strip():
                print(f"⚠️ Skipping empty chunk: {chunk_id}")
                continue

            # Run TTS generator
            generator = pipeline(
                chunk_text,
                voice=voice_tensor,
                speed=1,
                split_pattern=r'\n+'
            )

            audios = []
            for _, _, audio in generator:
                audios.append(audio)

            if audios:
                full_audio = np.concatenate(audios)
                sf.write(wav_path, full_audio, 24000)
                print(f"✅ Saved {wav_path}")

    print("🎧 All chunks processed successfully.")


voice_path = 'models--hexgrad--Kokoro-82M/snapshots/f3ff3571791e39611d31c381e3a41a3af07b4987/voices/bf_isabella.pt'
json_path_chapter = 'atomic-habits-chunks.json'

chunk_tts_from_json(json_path_chapter, pipeline, voice_path)
print(f"Program took: {time.time() - start_time} seconds to complete")