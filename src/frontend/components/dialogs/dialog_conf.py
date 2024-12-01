from src.frontend.components.dialogs.dialog_base import BaseDialog
from src.frontend.components.control import CommonButton, TitleLabel, CommonLineEdit, CommonScrollArea
from PyQt5.QtWidgets import *
import settings
from src.intermediary.center import handler
from src.frontend.public import app_root


class ConfDialog(BaseDialog):
    def __init__(self, parent=None):
        self.out_layout = QVBoxLayout()
        self.scroll_area = CommonScrollArea()
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)

        self.form = []
        self.apply = CommonButton('应用')
        self.cancel = CommonButton('关闭')
        super().__init__(parent)

    def init_ui(self):
        self.setWindowTitle('系统变量设置')
        self.setGeometry(100, 100, 700, 400)
        self.center_on_parent()
        self.setStyleSheet("background-color: white;")

        # 创建滚动区域
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area.setWidget(self.container_widget)

        self.out_layout.setContentsMargins(0, 0, 0, 0)
        self.out_layout.addWidget(self.scroll_area)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        self.setLayout(self.out_layout)

        self.part_conf_settings_ui()
        self.part_conf_definsight_ui()

        self.container_layout.addStretch()
        self.out_layout.setStretchFactor(self.scroll_area, 10)
        # self.out_layout.addStretch()

        self.part_button_group_ui()

        self.load_action()

    def load_action(self):
        self.apply.clicked.connect(self.action_confirm)
        self.cancel.clicked.connect(self.close_dialog)

    def action_confirm(self):
        for e in self.form:
            c: settings.Confs = e.property('origin')
            temp_val = e.text()
            if temp_val != c.values:
                app_root.ui_log.success(f'{c.depict_key}已更新为{temp_val}')
                c.values = temp_val
                if c.conf_type == 0:
                    setattr(settings.Files, c.keys, temp_val)
                elif c.conf_type == 1:
                    try:
                        import importlib
                        conf_lib = importlib.import_module(f'library.conf')
                        Config = getattr(conf_lib, 'Config')
                        setattr(Config, c.keys, temp_val)
                    except Exception as e:
                        app_root.ui_log.info(f'{e}')
                handler.update_instance(c)
        self.close_dialog()

    def part_conf_ui(self, title="配置项", conf_type=0):
        setting_layout = QVBoxLayout()

        label = TitleLabel(title)
        setting_layout.addWidget(label)
        setting_layout.setSpacing(0)

        group = QGroupBox()
        group.setStyleSheet("color: black")
        group_layout = QVBoxLayout()
        group.setLayout(group_layout)
        conf_settings = handler.search_type_conf(conf_type)

        for c in conf_settings:
            line = QHBoxLayout()
            t = TitleLabel(c.depict_key)
            e = CommonLineEdit(c.values)
            e.modified_stylesheet = "QLineEdit { background-color: #fcf3cf; }"
            e.setProperty('origin', c)
            self.form.append(e)
            e.textChanged.connect(self.on_line_edit_text_changed)
            line.addWidget(t)
            line.addWidget(e)
            line.setStretchFactor(t, 2)
            line.setStretchFactor(e, 8)
            group_layout.addLayout(line)

        setting_layout.addWidget(group)

        self.container_layout.addLayout(setting_layout)

    def part_conf_settings_ui(self):
        self.part_conf_ui(title='软件配置', conf_type=0)

    def part_conf_definsight_ui(self):
        self.part_conf_ui(title='统一平台配置', conf_type=1)

    def part_button_group_ui(self):
        # 创建按钮布局
        button_layout = QHBoxLayout()

        # 设置按钮样式
        button_confirm_style = """
            QPushButton {
                background-color: #3498db;
                border: none;
                padding: 5px;
                color: white;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #85c1e9;
            }
            QPushButton:pressed {
                background-color: #d6eaf8;
            }
            """

        button_reject_style = """
                    QPushButton {
                        background-color: #cacfd2;
                        border: none;
                        color: white;
                        text-align: center;
                        text-decoration: none;
                        font-size: 16px;
                        padding: 5px;
                        margin: 4px 2px;
                        border-radius: 8px;
                    }
                    QPushButton:hover {
                        background-color: #bdc3c7;
                    }
                    QPushButton:pressed {
                        background-color: #909497;
                    }
                    """

        # 将样式应用到按钮
        self.apply.setStyleSheet(button_confirm_style)
        self.cancel.setStyleSheet(button_reject_style)

        # 将按钮添加到布局中
        # frame_layout.addStretch()
        button_layout.addWidget(self.apply)
        button_layout.addWidget(self.cancel)

        # 设置按钮布局的间距
        button_layout.setContentsMargins(10, 0, 10, 10)
        # button_layout.setSpacing(10)

        # 添加弹簧到主布局，确保按钮在底部
        # spacer = QSpacerItem(20, 20, QSizePolicy.Maximum, QSizePolicy.Expanding)
        # self.out_layout.addSpacerItem(spacer)

        # 将按钮布局添加到主布局的底部
        self.out_layout.addLayout(button_layout)
        self.out_layout.setStretchFactor(button_layout, 1)

    def on_line_edit_text_changed(self):
        # 获取发送信号的 QLineEdit
        sender = self.sender()
        if sender:
            # 设置修改后的样式
            sender.setStyleSheet(sender.styleSheet() + sender.modified_stylesheet)
