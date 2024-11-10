from src.frontend.components.dialogs.dialog_base import BaseDialog
from src.frontend.components.control import CommonButton, TitleLabel
from PyQt5.QtWidgets import *
from src.intermediary.center import ControlCenter
import json


class FuncParamDialog(BaseDialog):
    """
    方法参数设置会话框
    """

    def __init__(self, parent=None):
        self.out_layout = QVBoxLayout()
        self.form_data = {}

        self.confirm = CommonButton('确定')
        self.cancel = CommonButton('取消')
        super().__init__(parent)

    def init_ui(self):
        self.setWindowTitle('配置')
        self.setGeometry(100, 100, 300, 300)
        self.center_on_parent()

        self.setLayout(self.out_layout)
        self.param_config_body_ui()
        self.param_config_bottom_ui()

    def param_config_body_ui(self):
        body_layout = QVBoxLayout()
        line_layout = QHBoxLayout()

        if ControlCenter.record_checked is not None:
            func = ControlCenter.search_record[ControlCenter.record_checked]

            title = TitleLabel(f'{func.depict_func}')
            title.setWordWrap(True)
            body_layout.addWidget(title)

            # 插入至第几步
            label_info = QLabel('插入至第几步')
            line_edit = QLineEdit()
            end_step_index = len(ControlCenter.steps) + 1
            line_edit.setText(str(end_step_index))
            line_layout.addWidget(label_info)
            line_layout.addWidget(line_edit)
            line_layout.setStretchFactor(line_edit, 1)
            line_layout.setStretchFactor(label_info, 1)

            self.form_data.update({'self_process_index': line_edit})

            body_layout.addLayout(line_layout)

            params = json.loads(func.params)
            depict_params = json.loads(func.depict_params)
            for param in params:
                ly = QHBoxLayout()
                k = QLabel(str(depict_params.get(param, param)))
                v = QLineEdit()
                v.setText(str(params.get(param, None)))
                ly.addWidget(k)
                ly.addWidget(v)
                ly.setStretchFactor(k, 1)
                ly.setStretchFactor(v, 1)
                self.form_data.update({param: v})
                body_layout.addLayout(ly)

        self.out_layout.addLayout(body_layout)

    def param_config_bottom_ui(self):
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.confirm)
        bottom_layout.addWidget(self.cancel)
        self.out_layout.addLayout(bottom_layout)

    def make_data(self):
        res = {}
        temp_res = {}
        for key, obj in self.form_data.items():
            if key == 'self_process_index':
                res.update({key: obj.text()})
            else:
                temp_res.update({key: obj.text()})
        res.update({'params': json.dumps(temp_res)})
        return res
