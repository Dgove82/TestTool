from PyQt5.QtCore import QThread, pyqtSignal
from src.intermediary.data_load import FuncParse
import settings


class LoadThread(QThread):
    finish_signal = pyqtSignal()

    def run(self):
        try:
            FuncParse(settings.Files.LIBRARY_PATH).handler()
        except Exception as e:
            settings.log.warning(str(e))
        finally:
            self.finish_signal.emit()
