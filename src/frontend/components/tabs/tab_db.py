from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QButtonGroup, QRadioButton, QComboBox
from PyQt5.QtCore import Qt
from src.frontend.public import app_root
from src.frontend.components.control import TitleLabel, CommonButton, CommonLineEdit


class OptionType:
    # []代表radio
    # text代表edit
    support_high_frame_rate = {"desc": "xx", "type": "radio", "func": "update_frame_mode",
                               "options": ["1", "0"],
                               "option_range": [0, 1], "checked": 0}
    wireless_frame_rate = {"desc": "xx", "type": "text", "func": "update_wireless_frame", "val": "55"}


class DBTab(QWidget):
    def __init__(self, index, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = index
        self.name = "设备配置"

        self.out_layout = QVBoxLayout()

        self.setLayout(self.out_layout)

        self.device_options = QComboBox(self)
        self.load_button = CommonButton('加载设备')
        self.label = TitleLabel('请先加载设备')
        self.container_layout = QVBoxLayout()
        self.apply_button = CommonButton('应用')

        try:
            self.config_db = DBOperation()
        except Exception as e:
            self.label.setText(f'无法使用:{e}')
        self.confs = list(filter(lambda x: not x.startswith("__"), dir(OptionType)))
        self.db_confs = []
        self.form = []
        self.is_load = False
        self.init_ui()
        self.load_action()

    def init_ui(self):
        self.load_header_device_ui()
        self.load_body_container_ui()
        self.load_bottom_button_ui()

    def load_header_device_ui(self):
        header_layout = QHBoxLayout()
        label = TitleLabel('设备类型')

        self.out_layout.addLayout(header_layout)
        header_layout.addWidget(label)
        header_layout.addWidget(self.device_options)
        header_layout.addWidget(self.load_button)

    def load_body_container_ui(self):
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
                            QScrollArea {
                                background-color: transparent;
                            }
                            QScrollArea > QWidget > QWidget {
                                background-color: white;
                            }
                            QScrollBar:vertical {
                                background: #e7e8e9;
                                width: 12px;
                                margin: 0px 0px 0px 0px;
                            }
                            QScrollBar::handle:vertical {
                                background: #c2c3c4;
                                min-height: 20px;
                            }
                            QScrollBar::add-line:vertical {
                                background: #c2c3c4;
                                height: 0px;
                                subcontrol-position: bottom;
                                subcontrol-origin: margin;
                            }
                            QScrollBar::sub-line:vertical {
                                background: #c2c3c4;
                                height: 0px;
                                subcontrol-position: top;
                                subcontrol-origin: margin;
                            }
                            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                                background: none;
                            }
                            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                                background: none;
                            }
                        """)
        container_widget = QWidget()
        container_widget.setLayout(self.container_layout)
        scroll_area.setWidget(container_widget)
        self.out_layout.addWidget(scroll_area)

        self.label.setAlignment(Qt.AlignCenter)
        self.container_layout.addWidget(self.label)
        self.container_layout.setSpacing(2)

    def load_bottom_button_ui(self):
        self.out_layout.addWidget(self.apply_button)
        self.apply_button.setDisabled(True)

    def load_action(self):
        self.load_button.clicked.connect(self.action_load_device_options)
        self.device_options.currentIndexChanged.connect(self.action_load_config)
        self.apply_button.clicked.connect(self.action_update_config)

    def action_load_device_options(self):
        devices = self.config_db.fetch_devices()
        if devices is not None:
            for device in devices:
                self.device_options.addItem(device)
            self.apply_button.setDisabled(False)
            app_root.ui_log.info(f'共加载<{len(devices)}>设备')

    def action_load_config(self):
        device = self.device_options.currentText()
        record = self.config_db.get_device_frame_setting(device)
        self.load_container_config_ui(record)
        record = self.config_db.get_workflow_nodes_setting(device)
        self.load_container_config_ui(record)
        if self.is_load is False:
            self.label.setText('修改配置中')
            self.label.setFixedHeight(50)
            self.container_layout.addStretch()

    def load_container_config_ui(self, record: dict):
        for key, value in record.items():
            if hasattr(OptionType, key):
                if len(self.form) != len(self.confs):
                    self.db_confs.append(key)
                detail = getattr(OptionType, key)
                conf_type = detail.get('type')
                if conf_type == 'radio':
                    checked = detail["option_range"].index(value)
                    desc = detail['desc']
                    detail['checked'] = checked
                    self.create_or_update_buttongroup(desc, checked, options=detail['options'],
                                                      index=self.db_confs.index(key))
                elif conf_type == 'text':
                    detail['val'] = value
                    desc = detail['desc']
                    self.create_or_update_text(desc, value, index=self.db_confs.index(key))

    def create_or_update_text(self, desc, val, index=None):
        if len(self.form) != len(self.confs):
            line_layout = QHBoxLayout()
            label = TitleLabel(desc)
            label.setAlignment(Qt.AlignCenter)
            line_layout.addWidget(label)
            edit = CommonLineEdit()
            if val == "ban_for_no_val":
                edit.setDisabled(True)
                edit.setText("选中设备无该属性")
            else:
                edit.setText(str(val))
            line_layout.addWidget(edit)
            line_layout.setStretchFactor(label, 1)
            line_layout.setStretchFactor(edit, 2)
            self.form.append(edit)
            self.container_layout.addLayout(line_layout)
        else:
            edit = self.form[index]
            if val == "ban_for_no_val":
                edit.setDisabled(True)
                edit.setText("选中设备无该属性")
            else:
                edit.setDisabled(False)
                edit.setText(str(val))

    def create_or_update_buttongroup(self, desc, checked, options=None, index=None):
        if len(self.form) != len(self.confs):
            line_layout = QHBoxLayout()
            button_layout = QHBoxLayout()
            label = TitleLabel(desc)
            label.setAlignment(Qt.AlignCenter)
            line_layout.addWidget(label)
            line_layout.addLayout(button_layout)
            line_layout.setStretchFactor(label, 1)
            line_layout.setStretchFactor(button_layout, 2)
            button_group = QButtonGroup(self)
            radios = []
            for index, option in enumerate(options):
                radio = QRadioButton(option)
                radios.append(radio)
                button_layout.addWidget(radio)
                button_group.addButton(radio, index)
                if checked == index:
                    radio.setChecked(True)
            self.form.append(button_group)
            self.container_layout.addLayout(line_layout)
        else:
            button_group = self.form[index]
            button_group.button(checked).setChecked(True)

    def action_update_config(self):
        selected_item = self.device_options.currentText()
        for index, conf in enumerate(self.db_confs):
            control = self.form[index]
            origin = getattr(OptionType, conf)
            control_type = origin['type']
            if control_type == 'radio':
                selected_btn = control.checkedButton()
                checked = control.id(selected_btn)
                if checked != origin['checked']:
                    origin['checked'] = checked
                    try:
                        getattr(self.config_db, origin['func'])(origin['option_range'][checked], selected_item)
                        app_root.ui_log.success(
                            f'设备[{selected_item}]{origin["desc"]}更新为{origin["option_range"][checked]}')
                    except Exception as e:
                        app_root.ui_log.warning(f'设备[{selected_item}]{origin["desc"]}更新失败: {e}')
            elif control_type == 'text':
                value = control.text()
                if value != str(origin['val']):
                    try:
                        getattr(self.config_db, origin['func'])(value, selected_item)
                        app_root.ui_log.success(f'设备[{selected_item}]{origin["desc"]}更新为{value}')
                    except Exception as e:
                        app_root.ui_log.warning(f'设备[{selected_item}]{origin["desc"]}更新失败: {e}')


class DBOperation:
    pass


if __name__ == '__main__':
    pass
