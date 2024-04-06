from diart import SpeakerDiarization
from diart.inference import StreamingInference
from diart.sinks import RTTMWriter
from diart.sources import MicrophoneAudioSource

pipeline = SpeakerDiarization()
mic = MicrophoneAudioSource()
inference = StreamingInference(pipeline, mic, do_plot=True)
inference.attach_observers(RTTMWriter(mic.uri, "/output/file.rttm"))
prediction = inference()
