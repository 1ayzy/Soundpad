import pyaudio

import json

from threading import Thread

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QAction, QPushButton, QListWidgetItem

from _internal.Initialisation import get_input_devices, get_soundpad_device, get_output_devices, get_all_sounds
from _internal.SoundFile import AudioFile

class MainWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('_internal\\MainWindow.ui', self)

        self.file = "sounds\\armatura_P29FH2w.mp3"
        self.format = self.file.split(".")[-1]

        self.test_volume = 100
        self.soundpad_volume = 100

        self.fault = False

        self.get_devices()

        if not self.fault:

            self.init_settings()

            self.queue = 0

            try:
                self.in_stream = self.p.open(
                    input_device_index = self.input_device["index"],
                    format = pyaudio.paInt16,
                    channels = 1,
                    rate = int(self.input_device["defaultSampleRate"]),
                    input = True
                )
            except Exception as e:
                print(e)

            self.soundpad_stream = self.p.open(
                output_device_index = self.soundpad_device["index"],
                format = pyaudio.paInt16,
                channels = 1,
                rate = 44100,
                output = True
            )

            self.start_merge()

            self.PlayButton.clicked.connect(self.play_clicked)
            self.PauseButton.clicked.connect(self.pause_clicked)
            self.StopButton.clicked.connect(self.stop_clicked)

            self.TestVolume.valueChanged[int].connect(self.update_test_volume)
            self.SoundpadVolume.valueChanged[int].connect(self.update_soundpad_volume)

            self.update_menus()

            self.update_sounds()

    def get_devices(self):
        self.p = pyaudio.PyAudio()
        self.devices = [self.p.get_device_info_by_index(i) for i in range(self.p.get_device_count())]

        self.soundpad_device = get_soundpad_device(self.devices)
        self.input_devices = get_input_devices(self.devices)
        self.output_devices = get_output_devices(self.devices)

        if self.soundpad_device == ReferenceError:
            self.fault = "soundpad_device"
        if not self.input_devices:
            self.fault = "input_devices"
        if not self.output_devices:
            self.fault = "output_devices"

        self.input_device = self.input_devices[0]
        self.output_device = self.output_devices[0]

    def update_test_volume(self, volume):
        self.test_volume = volume
        self.TestVolume_label.setText(str(volume))
        if self.queue:
            self.stream_listen.set_volume(volume)

    def update_soundpad_volume(self, volume):
        self.soundpad_volume = volume
        self.SoundpadVolume_label.setText(str(volume))
        if self.queue:
            self.main_stream.set_volume(volume)

    def update_sounds(self):
        self.listWidget.clear()
        self.files = get_all_sounds()

        for file in self.files:
            NewButton = QPushButton(file.split("\\")[-1], self)
            NewButton.clicked.connect(lambda ch, f=file: self.choose_file(f))

            listWidgetItem = QListWidgetItem()
            listWidgetItem.setSizeHint(NewButton.sizeHint())
            self.listWidget.addItem(listWidgetItem)
            if file.split("\\")[-1] == self.file.split("\\")[-1]:
                NewButton.setStyleSheet('QPushButton{background-color:rgb(100, 100, 255);font-size:15px;border-radius:5px;color:"white"}')
            self.listWidget.setItemWidget(listWidgetItem, NewButton)

    def update_menus(self):
        self.menuMicrophone_settings.clear()
        self.menuSpeakers_settings.clear()

        for device in self.input_devices:
            NewAction = QAction(device["name"], self)
            NewAction.triggered.connect(lambda ch, dev=device: self.choose_input_device(dev))
            NewAction.setCheckable(True)
            if device["name"] == self.input_device["name"]:
                NewAction.setChecked(True)
            else:
                NewAction.setChecked(False)
            self.menuMicrophone_settings.addAction(NewAction)

        for device in self.output_devices:
            NewAction = QAction(device["name"], self)
            NewAction.triggered.connect(lambda ch, dev=device: self.choose_output_device(dev))
            NewAction.setCheckable(True)
            if device["name"] == self.output_device["name"]:
                NewAction.setChecked(True)
            else:
                NewAction.setChecked(False)
            self.menuSpeakers_settings.addAction(NewAction)

    def init_settings(self):
        with open("_internal/settings.json", 'r', encoding="UTF-8") as f:
            if not f.readlines():
                jsn = {
                    "input-device": self.input_device,
                    "output-device": self.output_device
                }

                with open("_internal/settings.json", 'w', encoding="UTF-8") as f:
                    json.dump(jsn, f, ensure_ascii=False)

        with open("_internal/settings.json", 'r', encoding="UTF-8") as f:
            self.settings_devices = json.loads(f.readline())

        self.input_device = self.settings_devices["input-device"]
        self.output_device = self.settings_devices["output-device"]


    def update_settings(self):
        jsn = {
            "input-device": self.input_device,
            "output-device": self.output_device
        }

        with open("_internal/settings.json", 'w', encoding="UTF-8") as f:
            json.dump(jsn, f, ensure_ascii=False)

        with open("_internal/settings.json", 'r', encoding="UTF-8") as f:
            self.settings_devices = json.loads(f.readline())

        self.input_device = self.settings_devices["input-device"]
        self.output_device = self.settings_devices["output-device"]

    def choose_file(self, f):
        self.file = f
        self.update_sounds()
        self.stop_clicked()

    def choose_input_device(self, device):
        self.input_device = device

        self.update_settings()

        self.stop_merging()

        self.in_stream.close()

        self.in_stream = self.p.open(
            input_device_index=self.input_device["index"],
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True
        )

        self.start_merge()

        self.update_menus()

    def choose_output_device(self, device):
        self.output_device = device

        self.update_settings()

        self.update_menus()

    def play_clicked(self):
        try:
            self.play_clicked = Thread(target=self.playsound, daemon=True)
            self.play_clicked.start()

            self.listen = Thread(target=self.listensound, daemon=True)
            self.listen.start()
        except Exception as e:
            print(e)

    def stop_clicked(self):
        try:
            self.queue = 0
            self.main_stream.stop()
            self.stream_listen.stop()
        except Exception as e:
            print(e)

    def pause_clicked(self):
        try:
            self.main_stream.pause()
            self.stream_listen.pause()
        except Exception as e:
            print(e)

    def playsound(self):
        if self.queue >= 1:
            self.stop_clicked()
        self.queue += 1
        self.main_stream = AudioFile(self.file, self.soundpad_device, self.soundpad_volume)
        self.main_stream.play()

    def listensound(self):
        self.stream_listen = AudioFile(self.file, self.output_device, self.test_volume)
        self.stream_listen.play()


    def start_merge(self):
        self.merge = Thread(target=self.merge_mic_into_stream, daemon=True)
        self.merge.start()

    def stop_merging(self):
        self.running = False

    def merge_mic_into_stream(self):
        self.running = True
        while self.running:
            self.soundpad_stream.write(self.in_stream.read(1024))