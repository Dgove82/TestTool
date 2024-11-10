from src.frontend.components.dialogs.dialog_base import BaseDialog
from src.frontend.components.control import CommonButton
from PyQt5.QtWidgets import *
from src.intermediary.center import ControlCenter
from PyQt5.QtCore import Qt
from src.frontend.public import app_root


class DefineParamDialog(BaseDialog):
    def __init__(self, parent):
        self.running = False
        self.form_data = {}

        self.dialog_layout = QVBoxLayout()
        # self.watch_thread = WatchThread()
        self.watch_thread = app_root.key_watch
        self.info_label = QLabel('录制参数配置')
        self.start_btn = CommonButton('开始录制')

        super().__init__(parent)

        self.deal_action()

    def init_ui(self):
        self.setWindowTitle('键鼠录制')
        self.setGeometry(100, 100, 250, 100)
        self.center_on_parent()

        self.info_label.setAlignment(Qt.AlignCenter)
        self.dialog_layout.addWidget(self.info_label)

        self.param_ui()

        self.dialog_layout.addWidget(self.start_btn)
        self.setLayout(self.dialog_layout)

    def param_ui(self):
        param_body_ui = QVBoxLayout()

        line_layout = QHBoxLayout()
        line_label = QLabel('插入至第几步')
        line_edit = QLineEdit(str(len(ControlCenter.steps) + 1))

        line_layout.addWidget(line_label)
        line_layout.addWidget(line_edit)
        line_layout.setStretchFactor(line_edit, 1)
        line_layout.setStretchFactor(line_label, 1)
        self.form_data.update({'self_process_index': line_edit})

        name_layout = QHBoxLayout()
        name_label = QLabel('为录制方法取名')
        name_edit = QLineEdit()
        name_edit.setPlaceholderText('自定义命名')
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_edit)
        name_layout.setStretchFactor(name_edit, 1)
        name_layout.setStretchFactor(name_label, 1)
        self.form_data.update({'name': name_edit})

        param_body_ui.addLayout(line_layout)
        param_body_ui.addLayout(name_layout)
        self.dialog_layout.addLayout(param_body_ui)

    def deal_action(self):
        self.start_btn.clicked.connect(self.action_recoding)
        # self.watch_thread.start_signal.connect(self.start_record)
        self.watch_thread.start_run_signal.connect(self.start_record)

    def action_recoding(self):
        self.running = True
        # self.watch_thread.start()
        self.watch_thread.update_status_signal.emit(10)
        self.update_tip('按下<⬇>键开录|<esc>结束')
        self.start_btn.setEnabled(False)
        for obj in self.form_data.values():
            obj.setEnabled(False)

    def make_data(self):
        res = {}
        for key in self.form_data:
            value = self.form_data.get(key).text()
            res.update({key: None if not value else value})
        return res

    def start_record(self, msg):
        self.update_tip(msg)
        app_root.root.mini_window()

    def update_tip(self, msg):
        self.start_btn.setText(msg)

    def end_record(self):
        self.running = False
        self.start_btn.setEnabled(True)
        self.form_data['self_process_index'].setText(f"{int(self.form_data['self_process_index'].text()) + 1}")
        for obj in self.form_data.values():
            obj.setEnabled(True)
        self.update_tip('继续添加')

    def closeEvent(self, event):
        if self.running:
            self.watch_thread.update_status_signal.emit(1)
            app_root.ui_log.info('已取消录制')
        self.watch_thread.start_run_signal.disconnect(self.start_record)
        super().closeEvent(event)

