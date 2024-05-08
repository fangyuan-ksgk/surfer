import os
import select
import sys
import time
import wave

import numpy as np
import pyaudio
# from lightning_whisper_mlx import LightningWhisperMLX

# Set up the audio parameters
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 16000
CHUNK = 2048  # Increased chunk size

# Initialize the Whisper model
# whisper = LightningWhisperMLX(model="distil-medium.en", batch_size=12, quant=None)

audio_path = "./src/record/tmp.wav"


# Function to record audio from the microphone and save to a file
# One press some 'button' and the recording started
def record_audio(file_path=audio_path):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    frames = []

    print("Recording...")
    print("Press Enter to stop...")

    try:
        while True:
            if select.select([sys.stdin], [], [], 0)[0]:
                input()
                break
            data = stream.read(1024)
            frames.append(data)

    except Exception as e:
        print(f"An error occurred: {e}")

    print("Recording stopped.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(file_path, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b"".join(frames))
    wf.close()


def transcribe(whisper, audio_path=audio_path):
    text = whisper.transcribe(audio_path=audio_path)["text"]
    return text


def listen(whisper=None, audio_path=audio_path):
    pass
    record_audio(audio_path)
    return transcribe(whisper, audio_path)


# record_audio(audio_path)
# test = transcribe(whisper, audio_path)
# print(test)
