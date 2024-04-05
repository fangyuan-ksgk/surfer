import pyaudio
import wave
import os
import time
import numpy as np
from lightning_whisper_mlx import LightningWhisperMLX

# Set up the audio parameters
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 16000
CHUNK = 2048  # Increased chunk size

# Initialize the Whisper model
whisper = LightningWhisperMLX(model="distil-medium.en", batch_size=12, quant=None)

# Function to record audio from the microphone and save to a file
# One press some 'button' and the recording started
def record_audio(file_path):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    frames = []

    print("Recording...")

    try:
        while True:
            data = stream.read(1024)
            frames.append(data)
    except KeyboardInterrupt:
        pass

    print("Recording stopped.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()

record_audio('smalltest.wav')