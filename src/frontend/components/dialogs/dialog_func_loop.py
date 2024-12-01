from src.frontend.components.dialogs.dialog_base import BaseDialog
from src.frontend.components.control import CommonButton, TitleLabel, CommonLineEdit
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from src.intermediary.center import ControlCenter


class LoopParamDialog(BaseDialog):
    def __init__(self, *args, **kwargs):
        self.form_data = {}

        self.dialog_layout = QVBoxLayout()
        self.info_label = TitleLabel('循环方法配置')
        self.confirm_btn = CommonButton('确定')
        self.cancel_btn = CommonButton('取消')

        super().__init__(*args, **kwargs)

        self.setStyleSheet("""
                                QDialog {
                                    background-color: #E5EAF3; 
                                }
                            """ + self.styleSheet())

    def init_ui(self):
        self.setWindowTitle('循环方法')
        self.setGeometry(100, 100, 320, 350)
        self.center_on_parent()

        self.info_label.setAlignment(Qt.AlignCenter)
        self.dialog_layout.addWidget(self.info_label)
        self.setLayout(self.dialog_layout)

        self.param_ui()
        self.button_group_ui()
        self.load_actions()

    def load_actions(self):
        self.cancel_btn.clicked.connect(self.close_dialog)

    def param_ui(self):
        param_body_ui = QVBoxLayout()

        line_layout = QHBoxLayout()
        line_label = TitleLabel('插入至第几步')
        line_edit = CommonLineEdit(str(len(ControlCenter.steps) + 1))

        line_layout.addWidget(line_label)
        line_layout.addWidget(line_edit)
        line_layout.setStretchFactor(line_edit, 1)
        line_layout.setStretchFactor(line_label, 1)
        self.form_data.update({'self_process_index': line_edit})

        loop_layout = QHBoxLayout()
        loop_label = TitleLabel('循环后面几步')
        loop_edit = CommonLineEdit("1")
        loop_layout.addWidget(loop_label)
        loop_layout.addWidget(loop_edit)
        loop_layout.setStretchFactor(loop_label, 1)
        loop_layout.setStretchFactor(loop_edit, 1)
        self.form_data.update({'loop_steps': loop_edit})

        count_layout = QHBoxLayout()
        count_label = TitleLabel('循环次数')
        count_edit = CommonLineEdit("1")
        count_layout.addWidget(count_label)
        count_layout.addWidget(count_edit)
        count_layout.setStretchFactor(count_label, 1)
        count_layout.setStretchFactor(count_edit, 1)
        self.form_data.update({'loop_count': count_edit})

        name_layout = QHBoxLayout()
        name_label = TitleLabel('为循环方法取名')
        name_edit = CommonLineEdit()
        name_edit.setPlaceholderText('自定义命名')
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_edit)
        name_layout.setStretchFactor(name_edit, 1)
        name_layout.setStretchFactor(name_label, 1)
        self.form_data.update({'name': name_edit})

        param_body_ui.addLayout(line_layout)
        param_body_ui.addLayout(loop_layout)
        param_body_ui.addLayout(count_layout)
        param_body_ui.addLayout(name_layout)
        self.dialog_layout.addLayout(param_body_ui)

    def button_group_ui(self):
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.confirm_btn)
        btn_layout.addWidget(self.cancel_btn)
        self.dialog_layout.addLayout(btn_layout)

    def make_data(self):
        res = {}
        for key in self.form_data:
            value = self.form_data.get(key).text()
            res.update({key: None if not value else value})
        return res

