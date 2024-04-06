import asyncio
import base64
import json
import os

import pyaudio
import websockets
from dotenv import load_dotenv

load_dotenv()

GLADIA_API_KEY = os.environ["GLADIA_API_KEY"]

GLADIA_URL = "wss://api.gladia.io/audio/text/audio-transcription"


ERROR_KEY = "error"
TYPE_KEY = "type"
TRANSCRIPTION_KEY = "transcription"
LANGUAGE_KEY = "language"

LANGUAGE_BEHAVIOUR = "manual"  # Default: "automatic single language"
LANGUAGE = "english"

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

FINISH_COMMAND_TRESHOLD = 30

P = pyaudio.PyAudio()


async def send_audio(socket):
    print("Connected!")
    config = {"x-gladia-key": GLADIA_API_KEY, "language_behaviour": LANGUAGE_BEHAVIOUR, "reinject_context": "true"}
    if LANGUAGE_BEHAVIOUR == "manual":
        config["language"] = LANGUAGE
    await socket.send(json.dumps(config))

    stream = P.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=FRAMES_PER_BUFFER)

    print("Please ask me a question:")
    while socket.open:
        try:
            data = stream.read(FRAMES_PER_BUFFER)
            data = base64.b64encode(data).decode("utf-8")
            json_data = json.dumps({"frames": str(data)})
            await socket.send(json_data)
        except websockets.exceptions.ConnectionClosedError as e:
            print(e)
            assert e.code == 4008
            break
        except Exception as e:
            assert False, "Not a websocket 4008 error"
        await asyncio.sleep(0.01)


# get ready to receive transcriptions
async def receive_transcription(socket):
    while True:
        response = await socket.recv()
        utterance = json.loads(response)

        if utterance:
            if ERROR_KEY in utterance:
                print(f"{utterance[ERROR_KEY]}")
                break
            else:
                if TYPE_KEY in utterance:
                    print(f"{utterance[TYPE_KEY]}: ({utterance[LANGUAGE_KEY]}) {utterance[TRANSCRIPTION_KEY]}")
                    if utterance[TYPE_KEY] == "final":
                        print(
                            f"Final transcription received: "
                            f"({utterance[LANGUAGE_KEY]}) {utterance[TRANSCRIPTION_KEY]}"
                        )
                        return utterance[TRANSCRIPTION_KEY]
        else:
            print("Empty, waiting for next utterance...")


async def listen():
    async with websockets.connect(GLADIA_URL) as socket:
        send_task = asyncio.create_task(send_audio(socket))
        receive_task = asyncio.create_task(receive_transcription(socket))
        # await asyncio.gather(send_task, receive_task)
        final_transcription = await receive_task
        send_task.cancel()
        return final_transcription
