import os

from src.frontend.components.dialogs.dialog_base import BaseDialog
from src.frontend.components.control import CommonButton, TitleLabel
from PyQt5.QtWidgets import *
from src.intermediary.center import handler
from PyQt5.QtCore import Qt
import re
import settings


class GeneratePyDialog(BaseDialog):
    def __init__(self, parent=None):
        self.out_layout = QVBoxLayout()
        self.define_layout = QVBoxLayout()
        self.edit_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        self.label_info = TitleLabel('输入的值仅可为英文数字组合')
        self.module_name = QLineEdit()
        self.inner_text = QTextEdit()

        self.confirm = CommonButton('确定')
        self.save_btn = CommonButton('另存为')
        self.cancel = CommonButton('关闭')
        super().__init__(parent)

    def init_ui(self):
        self.setWindowTitle('脚本编辑')
        self.setGeometry(100, 100, 700, 400)
        self.center_on_parent()
        self.out_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.out_layout)

        self.load_before_body_ui()
        self.load_bottom_ui()

        self.load_action()

    def load_before_body_ui(self):
        self.define_layout.addWidget(self.label_info)
        self.label_info.setFixedHeight(100)
        self.label_info.setAlignment(Qt.AlignCenter)

        param_layout = QHBoxLayout()
        label = QLabel('模块名')
        label.setAlignment(Qt.AlignCenter)
        param_layout.addWidget(label)
        param_layout.addWidget(self.module_name)
        param_layout.setStretchFactor(label, 1)
        param_layout.setStretchFactor(self.module_name, 1)

        self.define_layout.addLayout(param_layout)

        self.out_layout.addLayout(self.define_layout)

    def load_body_ui(self):
        module_name = self.module_name.text()
        content = handler.generate_py(module_name)
        self.inner_text.setLineWrapMode(QTextEdit.NoWrap)
        self.inner_text.setText(content)
        self.out_layout.addWidget(self.inner_text)
        self.out_layout.setStretchFactor(self.inner_text, 10)

    def load_bottom_ui(self):
        self.button_layout.addWidget(self.confirm)
        self.button_layout.addWidget(self.cancel)
        self.out_layout.addLayout(self.button_layout)
        self.out_layout.setStretchFactor(self.button_layout, 1)

    def load_action(self):
        self.cancel.clicked.connect(self.close_dialog)
        self.confirm.clicked.connect(self.show_body_ui)
        self.save_btn.clicked.connect(self.action_save_file)

    def show_body_ui(self):
        name = self.module_name.text()
        if re.match(r'^[A-Z][a-zA-Z0-9]*(_[A-Z][a-zA-Z0-9]*)*$', name):
            self.out_layout.removeItem(self.define_layout)
            self.out_layout.removeItem(self.button_layout)
            self.button_layout.replaceWidget(self.confirm, self.save_btn)
            self.load_body_ui()
            self.out_layout.addLayout(self.button_layout)
        else:
            self.label_info.setText('不符合命名规则，请取类似:CaseXx的名字')

    def action_save_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "另存为脚本", str(settings.Files.CASE_DIR),
                                                   "PYTHON Files (*.py)", options=options)
        if file_path:
            file_name = os.path.basename(file_path)
            if re.match(r'^[A-Za-z][_a-zA-Z0-9]*', file_name):
                content = self.inner_text.toPlainText()
                handler.script_save(content, file_path)
            else:
                QMessageBox.warning(self, '警告', '文件名只能包含英文字符，请重新输入')
                self.action_save_file()
