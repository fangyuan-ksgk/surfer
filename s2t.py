import pyaudio
import numpy as np
from lightning_whisper_mlx import LightningWhisperMLX

# Set up the audio parameters
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 16000
CHUNK = 2048  # Increased chunk size

# Initialize the Whisper model
whisper = LightningWhisperMLX(model="distil-medium.en", batch_size=12, quant=None)

# Create a PyAudio stream
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

print("Listening...")

try:
    while True:
        try:
            # Read audio data from the stream
            data = stream.read(CHUNK)
        except OSError as e:
            if e.errno == -9981:  # Input overflowed
                print("Input overflowed. Skipping...")
                continue
            else:
                raise

        # Convert audio data to numpy array
        audio_data = np.frombuffer(data, dtype=np.float32)

        # Transcribe the audio data
        text = whisper.transcribe(audio_data)['text']

        # Print the transcribed text
        print(text)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()