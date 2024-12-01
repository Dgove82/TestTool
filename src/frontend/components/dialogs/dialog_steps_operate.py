from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

from src.frontend.components.dialogs.dialog_base import BaseDialog
from src.frontend.components.control import CommonButton, TitleLabel, CommonLineEdit
from PyQt5.QtCore import Qt
from src.intermediary.center import ControlCenter


class StepExportDialog(BaseDialog):

    def __init__(self, *args, **kwargs):
        self.form_data = {}
        self.dialog_layout = QVBoxLayout()
        self.info_label = TitleLabel('步骤导出配置')
        self.confirm_btn = CommonButton('保存')
        self.cancel_btn = CommonButton('取消')

        super().__init__(*args, **kwargs)

        self.setStyleSheet("""
                                QDialog {
                                    background-color: #E5EAF3; 
                                }
                            """ + self.styleSheet())

    def init_ui(self):
        self.setWindowTitle('步骤导出')
        self.setGeometry(100, 100, 320, 350)
        self.center_on_parent()

        self.info_label.setAlignment(Qt.AlignCenter)
        self.dialog_layout.addWidget(self.info_label)
        self.setLayout(self.dialog_layout)

        self.param_body_ui()
        self.button_group_ui()

        self.load_actions()

    def load_actions(self):
        self.cancel_btn.clicked.connect(self.close_dialog)

    def param_body_ui(self):
        body_layout = QVBoxLayout()

        from_layout = QHBoxLayout()
        from_label = TitleLabel("从第几步开始")
        from_edit = CommonLineEdit("1")
        from_layout.addWidget(from_label)
        from_layout.addWidget(from_edit)
        self.form_data.update({"from": from_edit})
        from_layout.setStretchFactor(from_label, 1)
        from_layout.setStretchFactor(from_edit, 1)

        to_layout = QHBoxLayout()
        to_label = TitleLabel("到第几步结束")
        to_edit = CommonLineEdit(str(len(ControlCenter.steps)))
        to_layout.addWidget(to_label)
        to_layout.addWidget(to_edit)
        self.form_data.update({"to": to_edit})
        to_layout.setStretchFactor(to_label, 1)
        to_layout.setStretchFactor(to_edit, 1)

        body_layout.addLayout(from_layout)
        body_layout.addLayout(to_layout)
        self.dialog_layout.addLayout(body_layout)

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


class StepImportDialog(BaseDialog):
    def __init__(self, *args, **kwargs):
        self.form_data = {}
        self.dialog_layout = QVBoxLayout()
        self.info_label = TitleLabel('步骤导入配置')
        self.confirm_btn = CommonButton('导入')
        self.cancel_btn = CommonButton('取消')

        super().__init__(*args, **kwargs)

        self.setStyleSheet("""
                                QDialog {
                                    background-color: #E5EAF3; 
                                }
                            """ + self.styleSheet())

    def init_ui(self):
        self.setWindowTitle('步骤导入')
        self.setGeometry(100, 100, 320, 350)
        self.center_on_parent()

        self.info_label.setAlignment(Qt.AlignCenter)
        self.dialog_layout.addWidget(self.info_label)
        self.setLayout(self.dialog_layout)

        self.param_body_ui()
        self.button_group_ui()

        self.load_actions()

    def load_actions(self):
        self.cancel_btn.clicked.connect(self.close_dialog)

    def param_body_ui(self):
        body_layout = QVBoxLayout()

        to_layout = QHBoxLayout()
        to_label = TitleLabel("插入至第几步")
        to_edit = CommonLineEdit(str(len(ControlCenter.steps) + 1))
        to_layout.addWidget(to_label)
        to_layout.addWidget(to_edit)
        self.form_data.update({"to": to_edit})
        to_layout.setStretchFactor(to_label, 1)
        to_layout.setStretchFactor(to_edit, 1)

        body_layout.addLayout(to_layout)
        self.dialog_layout.addLayout(body_layout)

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
