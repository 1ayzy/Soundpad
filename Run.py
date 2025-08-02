import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from _internal.SoundPadWindow import MainWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWidget()
    fault = ex.fault
    if not fault:
        try:
            ex.show()
            sys.exit(app.exec_())
        except Exception as e:
            print(e)
    else:
        app = QApplication(sys.argv)
        if fault == "soundpad_device":
            link = "https://vb-audio.com/Cable"
            text = 'Ошибка чтения драйверов, <br> попробуйте установить'
            link_text = "VB-Virtual Cabel"
        elif fault == "input_devices":
            link = "https://vb-audio.com/Cable"
            text = 'Ошибка чтения входных устройств (микрофонов), <br> - Попробуйте отключить/подключить устройства, <br> - Проверьте их работоспособность, <br> - Попробуйте переустановить'
            link_text = "VB-Virtual Cabel"
        elif fault == "output_devices":
            link = "https://vb-audio.com/Cable"
            text = 'Ошибка чтения выходных устройств (динамиков), <br> - Попробуйте отключить/подключить устройства, <br> - Проверьте их работоспособность, <br> - Попробуйте переустановить'
            link_text = "VB-Virtual Cabel"
        else:
            sys.exit()
        link_msg = "{} <a href={}>{}</a>".format(text, link, link_text)
        result = QMessageBox.critical(None, 'Error: {}'.format(fault), link_msg)
        if result:
            sys.exit()
        app.exec_()
