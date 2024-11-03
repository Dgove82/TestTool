from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView


class WebTab(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        web_layout = QVBoxLayout()
        self.setLayout(web_layout)
        browser = QWebEngineView()
        browser.setUrl(QUrl('https://baidu.com/'))
        web_layout.addWidget(browser)
