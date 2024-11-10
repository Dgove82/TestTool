from src.frontend.components.dialogs.dialog_base import BaseDialog
from src.frontend.components.control import CommonButton, TitleLabel
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import settings
from src.frontend.public import app_root, control_func
from src.frontend.components.threads.thread_load import LoadThread


class LoadDialog(BaseDialog):
    def __init__(self, parent=None):
        self.out_layout = QVBoxLayout()

        self.info = TitleLabel()
        self.confirm = CommonButton('加载')
        self.cancel = CommonButton('关闭')
        self.load_task = LoadThread()
        super().__init__(parent)

    def init_ui(self):
        self.setWindowTitle('方法加载')
        self.setGeometry(100, 100, 300, 300)
        self.center_on_parent()
        self.setLayout(self.out_layout)

        self.body_ui()
        self.bottom_ui()

        self.load_action()

    def load_action(self):
        self.confirm.clicked.connect(self.action_load_func)
        self.cancel.clicked.connect(self.close_task)
        self.load_task.finished.connect(self.task_finished)

    def body_ui(self):
        msg = f'将从\n{settings.Files.LIBRARY_PATH}\n文件中解析方法'
        self.info.setText(msg)
        self.info.setWordWrap(True)
        self.info.setAlignment(Qt.AlignCenter)
        self.out_layout.addWidget(self.info)

    def bottom_ui(self):
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.confirm)
        button_layout.addWidget(self.cancel)
        self.out_layout.addLayout(button_layout)

    def action_load_func(self):
        app_root.ui_log.info('开始加载')
        self.info.setText('解析中')
        self.confirm.setDisabled(True)
        self.load_task.start()

    def task_finished(self):
        self.confirm.setDisabled(False)
        self.info.setText('加载完成')
        control_func.actions.action_search()
        app_root.ui_log.success('加载完毕')

    def close_task(self):
        app_root.dialog = None
        if self.load_task.isRunning():
            self.load_task.terminate()
            self.load_task.wait()
            app_root.ui_log.success('解析被中断')
        self.reject()

    def closeEvent(self, event):
        self.close_task()
