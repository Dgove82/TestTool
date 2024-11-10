from PyQt5.QtCore import QThread, pyqtSignal
from src.intermediary.data_load import FuncParse
import settings


class LoadThread(QThread):
    finish_signal = pyqtSignal()

    def run(self):
        FuncParse(settings.Files.LIBRARY_PATH).handler()
        self.finish_signal.emit()
