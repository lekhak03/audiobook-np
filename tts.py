import wave
from piper import PiperVoice
import time

start = time.time()

def prepare_for_tts(text):
    # Collapse multiple newlines into a single space
    clean_text = " ".join(text.splitlines())
    # Optionally normalize spaces
    clean_text = " ".join(clean_text.split())
    return clean_text


text = prepare_for_tts(text)
voice = PiperVoice.load("en_US-ryan-high.onnx")
with wave.open("93.wav", "wb") as wav_file:
    voice.synthesize_wav(text, wav_file)

end = time.time()
print(f"Execution time: {end - start:.4f} seconds")