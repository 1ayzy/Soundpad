import time
import numpy as np
import pyaudio
from wave import open
import soundfile as sf
import SCbtr as sc

class AudioFile:
    chunk = 1024

    def __init__(self, file, device, volume):
        self.format = file.split(".")[-1]

        self.playing = False
        self.stopped = True

        self.device = device
        self.file = file

        self.volume = volume

        if self.format == "wav":
            self.wf = open(file, 'rb')
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(
                output_device_index = self.device["index"],
                format = self.p.get_format_from_width(self.wf.getsampwidth()),
                channels = self.wf.getnchannels(),
                rate = self.wf.getframerate(),
                output = True
            )
            self.typ = {1: np.int8, 2: np.int16, 4: np.int32}.get(self.wf.getsampwidth())

        elif self.format == "mp3":
            self.speaker = sc.get_speaker(self.device["name"])
            self.samples, self.samplerate = sf.read(self.file)


    def play(self):
        self.playing = True
        if self.format == "wav":
            if self.stopped:
                self.data = self.wf.readframes(self.chunk)
                self.data = (np.frombuffer(self.data, dtype=self.typ) / 100 * self.volume).astype(self.typ).tobytes()
                self.stopped = False
            while self.data != b'' and not self.stopped:
                if self.playing:
                    self.stream.write(self.data)
                    self.data = self.wf.readframes(self.chunk)
                    self.data = (np.frombuffer(self.data, dtype=self.typ) / 100 * self.volume).astype(self.typ).tobytes()
                else:
                    time.sleep(0.1)
            self.playing = False
        elif self.format == "mp3":
            file = sf.SoundFile(file=self.file)
            with self.speaker.player(samplerate=file.samplerate, channels=file.channels) as self.sp:
                data = file.read()
                self.sp.play(data, self.volume)

    def pause(self):
        if self.format == "wav":
            if self.playing:
                self.playing = False
            else:
                self.playing = True
        elif self.format == "mp3":
            self.sp.pause()

    def stop(self):
        if self.format == "wav":
            self.playing = False
            self.stopped = True
        elif self.format == "mp3":
            self.sp.stop()

    def set_volume(self, volume):
        if self.format == "wav":
            self.volume = volume
        elif self.format == "mp3":
            self.sp.set_volume(volume)

    def close(self):
        self.stream.close()


