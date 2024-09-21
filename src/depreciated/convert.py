import sys
import tempfile
import wave

import numpy as np
import pyaudio
from lightning_whisper_mlx import LightningWhisperMLX

# import wavfile

# Initialize the Whisper model
whisper = LightningWhisperMLX(model="distil-medium.en", batch_size=12, quant=None)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1 if sys.platform == "darwin" else 2
RATE = 44100
RECORD_SECONDS = 5

# Keep the structure, except that we would directly process each CHUNK here with Whisper

with wave.open("output.wav", "wb") as wf:
    p = pyaudio.PyAudio()
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

    print("Recording...")
    for _ in range(0, RATE // CHUNK * RECORD_SECONDS):
        # Read audio data from the stream
        data = stream.read(CHUNK)
        # Convert audio data to numpy array
        audio_data = np.frombuffer(data, dtype=np.float32)

        # Whisper Processing & Transcribe on the chunk of text
        print(f"Type of audio_data: {type(audio_data)}")

        # Save the audio data as a temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio_path = temp_audio.name
            audio_data = (audio_data * 32767).astype(
                np.int16
            )  # Scale and convert to int16
            # Use wave module to write audio data to a temporary file
            with wave.open(temp_audio_path, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(audio_data.tobytes())

        # Transcribe the audio data from the temporary file
        text = whisper.transcribe(temp_audio_path)["text"]
        print(text)

        wf.writeframes(stream.read(CHUNK))

    print("Done")

    stream.close()
    p.terminate()
