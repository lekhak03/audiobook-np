import wave
from piper import PiperVoice

voice = PiperVoice.load("en_US-ryan-high.onnx")
with wave.open("test.wav", "wb") as wav_file:
    voice.synthesize_wav("Welcome to the world of speech synthesis!", wav_file)
    