from src.frontend.components.dialogs.dialog_base import BaseDialog
from src.frontend.components.control import CommonButton, TitleLabel
from PyQt5.QtWidgets import *
from src.intermediary.center import ControlCenter
from src.frontend.public import app_root
from PyQt5.QtCore import Qt
from src.frontend.components.threads import TaskThread


class ExecDialog(BaseDialog):
    """
    执行会话框
    """

    def __init__(self, parent=None):
        self.info_label = TitleLabel('执行流程')
        self.dialog_layout = QVBoxLayout()
        self.confirm = CommonButton('执行')
        self.cancel = CommonButton('取消')

        self.run_task = TaskThread()

        self.form = []
        super().__init__(parent)

    def init_ui(self):
        self.setWindowTitle('流程')
        self.setGeometry(100, 100, 200, 100)
        self.center_on_parent()

        self.setLayout(self.dialog_layout)
        self.param_body_ui()
        self.param_bottom_ui()

        self.load_action()

    def param_body_ui(self):
        self.info_label.setAlignment(Qt.AlignCenter)
        self.dialog_layout.addWidget(self.info_label)

        self.add_item('从第几步开始', str(ControlCenter.exec_step_start))
        self.add_item('执行到第几步', str(ControlCenter.exec_step_end))
        self.add_item('执行次数', str(ControlCenter.count))

    def param_bottom_ui(self):
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.confirm)
        bottom_layout.addWidget(self.cancel)
        self.dialog_layout.addLayout(bottom_layout)

    def add_item(self, label, val):
        line = QHBoxLayout()
        param = QLabel(label)
        edit = QLineEdit(val)
        line.addWidget(param)
        line.addWidget(edit)
        self.form.append(edit)
        line.setStretchFactor(param, 1)
        line.setStretchFactor(edit, 1)
        self.dialog_layout.addLayout(line)

    def load_action(self):
        self.confirm.clicked.connect(self.start_task)
        self.cancel.clicked.connect(self.close_task)

    def start_task(self):
        try:
            vals = self.make_data()
        except ValueError:
            self.info_label.setText('参数仅可为整数')
            return
        ControlCenter.exec_step_start = vals[0]
        ControlCenter.exec_step_end = vals[1]
        ControlCenter.count = vals[2]

        self.confirm.setDisabled(True)
        app_root.ui_log.info('开始执行流程')
        self.info_label.setText('执行中')
        app_root.root.mini_window()
        self.run_task.start()
        self.run_task.finished.connect(self.task_finished)

    def task_finished(self):
        app_root.root.normal_window()
        self.info_label.setText('执行完毕')
        self.confirm.setDisabled(False)

    def make_data(self):
        res = []
        for obj in self.form:
            res.append(int(obj.text()))
        return res

    def close_task(self):
        app_root.dialog = None
        if self.run_task.isRunning():
            self.run_task.terminate()
            self.run_task.wait()
            app_root.ui_log.success('流程已被中断')
            app_root.root.normal_window()
        self.reject()

    def closeEvent(self, event):
        self.close_task()
