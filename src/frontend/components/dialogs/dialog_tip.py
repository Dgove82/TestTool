from PyQt5.QtWidgets import QVBoxLayout
from src.frontend.components import CommonButton, TitleLabel
from src.frontend.components.dialogs.dialog_base import BaseDialog


class DialogTip(BaseDialog):

    def __init__(self, info, *args, **kwargs):
        self.dialog_layout = QVBoxLayout()
        self.confirm = CommonButton('确定')
        self.info = info
        super().__init__(*args, **kwargs)

    def init_ui(self):
        self.setWindowTitle('提示')
        self.setGeometry(100, 100, 200, 100)
        self.center_on_parent()

        self.setLayout(self.dialog_layout)

        self.load_tip_body()
        self.load_action()

    def load_tip_body(self):
        label = TitleLabel(self.info)
        self.dialog_layout.addWidget(label)
        self.dialog_layout.addWidget(self.confirm)

    def load_action(self):
        self.confirm.clicked.connect(self.close_dialog)

