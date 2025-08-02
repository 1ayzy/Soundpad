import pyaudio
p = pyaudio.PyAudio()

import os

def get_all_sounds():
    files = []
    directory = 'sounds'
    for entry in os.scandir(directory):
        if entry.is_file():
            files.append(entry.path)
    return files

def get_input_names(devices):
    names = []
    for i in devices:
        if i["maxInputChannels"] and i["hostApi"]:
            name = (i["name"].encode("WINDOWS-1251", "ignore")).decode("UTF-8")
            names.append(name)
    return names

def get_output_names(devices):
    names = []
    for i in devices:
        if i["maxOutputChannels"] and i["hostApi"]:
            name = (i["name"].encode("WINDOWS-1251", "ignore")).decode("UTF-8")
            names.append(name)
    return names

def get_soundpad_device(devices):
    for device in devices:
        if "CABLE Input" in device["name"]:
            return device
    return ReferenceError

def get_input_devices(devices):
    input_devices = []
    for i in devices:
        if i["maxInputChannels"] and i["hostApi"] == 0:
            name = (i["name"].encode("WINDOWS-1251", "ignore")).decode("UTF-8")
            names = get_input_names(devices)
            for n in names:
                if name in n:
                    n = n.replace("( ", "(").replace(" )", ")")
                    i["name"] = n
                    break
                else:
                    i["name"] = ""
            if i["name"]:
                input_devices.append(i)
    return input_devices

def get_output_devices(devices):
    output_devices = []
    for i in devices:
        if i["maxOutputChannels"] and i["hostApi"] == 0:
            name = (i["name"].encode("WINDOWS-1251", "ignore")).decode("UTF-8")
            names = get_output_names(devices)
            for n in names:
                if name in n:
                    n = n.replace("( ", "(").replace(" )", ")")
                    i["name"] = n
                    break
                else:
                    i["name"] = ""
            if i["name"]:
                output_devices.append(i)
    return output_devices