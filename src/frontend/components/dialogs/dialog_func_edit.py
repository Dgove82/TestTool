from src.frontend.components.dialogs.dialog_base import BaseDialog
from src.frontend.components.control import CommonButton, TitleLabel, CommonLineEdit, CommonInfoBox
from PyQt5.QtWidgets import *
from src.intermediary.center import ControlCenter
from PyQt5.QtCore import Qt
import json


class EditParamDialog(BaseDialog):
    def __init__(self, parent=None):
        self.out_layout = QVBoxLayout()
        self.form_data = {}

        self.confirm = CommonButton('确定')
        self.cancel = CommonButton('取消')
        self.body_layout = QVBoxLayout()
        super().__init__(parent)
        self.setStyleSheet("""
                            QDialog {
                                background-color: #E5EAF3; 
                            }
                        """ + self.styleSheet())

    def init_ui(self):
        self.setWindowTitle('编辑')
        self.setGeometry(100, 100, 300, 300)
        self.center_on_parent()
        self.setLayout(self.out_layout)

        self.param_config_body_ui()
        self.param_config_bottom_ui()

    def param_config_body_ui(self):

        if ControlCenter.checked != -1:
            func = ControlCenter.steps[ControlCenter.checked]

            f_type = func.get("type", None)
            if f_type == "exist":
                title = CommonInfoBox(f'{func.get("depict_func", None)}')
                self.body_layout.addWidget(title)
                params = json.loads(func.get('params', None))
                depict_params = json.loads(func.get('depict_params', None))
                for param in params:
                    ly = QHBoxLayout()
                    k = TitleLabel(str(depict_params.get(param, None)))
                    v = CommonLineEdit(str(params.get(param, None)))
                    ly.addWidget(k)
                    ly.addWidget(v)
                    ly.setStretchFactor(k, 1)
                    ly.setStretchFactor(v, 1)
                    self.form_data.update({param: v})
                    self.body_layout.addLayout(ly)
            elif f_type == "define":
                self.param_define_body_ui(func)
            elif f_type == "loop":
                self.param_loop_body_ui(func)

            line_layout = QHBoxLayout()
            label_info = TitleLabel('更新至第几步')
            line_edit = CommonLineEdit()
            line_edit.setText(str(ControlCenter.checked + 1))
            line_layout.addWidget(label_info)
            line_layout.addWidget(line_edit)
            line_layout.setStretchFactor(line_edit, 1)
            line_layout.setStretchFactor(label_info, 1)
            self.form_data.update({'self_process_update_index': line_edit})
            self.body_layout.addLayout(line_layout)

        self.out_layout.addLayout(self.body_layout)

    def param_define_body_ui(self, func):
        title = TitleLabel(f'录制方法编辑')
        title.setAlignment(Qt.AlignCenter)
        self.body_layout.addWidget(title)

        self.body_layout.addLayout(self.param_line_ui('录制方法名', func, 'name'))

    def param_loop_body_ui(self, func):
        title = TitleLabel(f'循环方法编辑')
        title.setAlignment(Qt.AlignCenter)
        self.body_layout.addWidget(title)

        self.body_layout.addLayout(self.param_line_ui('循环后面几步', func, 'loop_steps'))
        self.body_layout.addLayout(self.param_line_ui('循环次数', func, 'loop_count'))
        self.body_layout.addLayout(self.param_line_ui('循环方法名', func, 'name'))

    def param_line_ui(self, label: str, func: dict, key: str):
        line_layout = QHBoxLayout()
        label_info = TitleLabel(label)
        value = func.get(key, None)
        line_edit = CommonLineEdit(f"{value}")
        self.form_data.update({key: line_edit})
        line_layout.addWidget(label_info)
        line_layout.addWidget(line_edit)
        line_layout.setStretchFactor(line_edit, 1)
        line_layout.setStretchFactor(label_info, 1)
        return line_layout

    def param_config_bottom_ui(self):
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.confirm)
        bottom_layout.addWidget(self.cancel)
        self.out_layout.addLayout(bottom_layout)

    def make_data(self):
        res = {}
        for key, obj in self.form_data.items():
            res.update({key: obj.text()})
        return res
