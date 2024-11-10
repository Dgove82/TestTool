from src.frontend.components.dialogs.dialog_base import BaseDialog
from src.frontend.components.control import CommonButton, TitleLabel
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
        super().__init__(parent)

    def init_ui(self):
        self.setWindowTitle('编辑')
        self.setGeometry(100, 100, 300, 300)
        self.center_on_parent()
        self.setLayout(self.out_layout)

        self.param_config_body_ui()
        self.param_config_bottom_ui()

    def param_config_body_ui(self):
        body_layout = QVBoxLayout()

        if ControlCenter.checked is not None:
            func = ControlCenter.steps[ControlCenter.checked]

            func_name = func.get("type", None)
            if func_name == "exist":
                title = TitleLabel(f'{func.get("depict_func", None)}')
                title.setWordWrap(True)
                body_layout.addWidget(title)

                params = json.loads(func.get('params', None))
                depict_params = json.loads(func.get('depict_params', None))
                for param in params:
                    ly = QHBoxLayout()
                    k = QLabel(str(depict_params.get(param, None)))
                    v = QLineEdit(str(params.get(param, None)))
                    ly.addWidget(k)
                    ly.addWidget(v)
                    ly.setStretchFactor(k, 1)
                    ly.setStretchFactor(v, 1)
                    self.form_data.update({param: v})
                    body_layout.addLayout(ly)
            else:
                title = TitleLabel(f'录制方法')
                title.setAlignment(Qt.AlignCenter)
                title.setWordWrap(True)
                body_layout.addWidget(title)

                line_layout = QHBoxLayout()
                label_info = QLabel("修改名字")
                value = func.get('name', None)
                line_edit = QLineEdit(f"{value}")
                self.form_data.update({"name": line_edit})
                line_layout.addWidget(label_info)
                line_layout.addWidget(line_edit)
                body_layout.addLayout(line_layout)

        self.out_layout.addLayout(body_layout)

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
