from PyQt5.QtCore import QThread, pyqtSignal
from src.intermediary.center import handler


class TaskThread(QThread):
    finish_signal = pyqtSignal()

    def run(self):
        handler.steps_exec()
        self.finish_signal.emit()
