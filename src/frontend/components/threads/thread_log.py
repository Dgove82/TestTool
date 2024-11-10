from PyQt5.QtCore import QThread, pyqtSignal

import settings


class LogThread(QThread, settings.Log):
    log_signal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def capture_msg(self, message):
        super().capture_msg(message)
        self.log_signal.emit(message)
