import json
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat
from PyQt5.QtCore import Qt, QThread, pyqtSignal

import settings
from src.frontend.public import control_func, app_root
from src.intermediary.center import handler, ControlCenter
from pynput import keyboard, mouse


class TaskThread(QThread):
    finish_signal = pyqtSignal()

    def run(self):
        handler.steps_exec()
        self.finish_signal.emit()


class BaseDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        pass

    def center_on_parent(self):
        if self.parent():
            parent = self.parent().frameGeometry()
            child = self.frameGeometry()
            top = parent.top() + (parent.height() - child.height()) / 2
            left = parent.left() + (parent.width() - child.width()) / 2
            self.move(left, top)

    def close_dialog(self):
        app_root.dialog = None
        self.accept()

    def closeEvent(self, event):
        app_root.dialog = None

    def keyPressEvent(self, event):
        if event.key() != Qt.Key_Escape:
            super().keyPressEvent(event)


class ExecDialog(BaseDialog):
    """
    执行会话框
    """

    def __init__(self, parent=None):
        self.info_label = TitleLabel('执行流程')
        self.dialog_layout = QVBoxLayout()
        self.confirm = CommonButton('执行')
        self.cancel = CommonButton('取消')

        self.form = []
        super().__init__(parent)

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle('流程')
        self.setGeometry(100, 100, 200, 100)
        self.center_on_parent()

        self.setLayout(self.dialog_layout)
        self.param_body_ui()
        self.param_bottom_ui()

        self.load_action()

    def param_body_ui(self):
        self.info_label.setAlignment(Qt.AlignCenter)
        self.dialog_layout.addWidget(self.info_label)

        self.add_item('从第几步开始', str(ControlCenter.exec_step_start))
        self.add_item('执行到第几步', str(ControlCenter.exec_step_end))
        self.add_item('执行次数', str(ControlCenter.count))

    def param_bottom_ui(self):
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.confirm)
        bottom_layout.addWidget(self.cancel)
        self.dialog_layout.addLayout(bottom_layout)

    def add_item(self, label, val):
        line = QHBoxLayout()
        param = QLabel(label)
        edit = QLineEdit(val)
        line.addWidget(param)
        line.addWidget(edit)
        self.form.append(edit)
        line.setStretchFactor(param, 1)
        line.setStretchFactor(edit, 1)
        self.dialog_layout.addLayout(line)

    def load_action(self):
        self.confirm.clicked.connect(self.start_task)
        self.cancel.clicked.connect(self.close_task)

    def start_task(self):
        try:
            vals = self.make_data()
        except ValueError:
            self.info_label.setText('参数仅可为整数')
            return
        ControlCenter.exec_step_start = vals[0]
        ControlCenter.exec_step_end = vals[1]
        ControlCenter.count = vals[2]

        app_root.ui_log.info('开始执行流程')
        self.info_label.setText('执行中')
        app_root.root.mini_window()
        control_func.run_task.start()
        control_func.run_task.finished.connect(self.task_finished)

    def task_finished(self):
        app_root.root.normal_window()
        self.info_label.setText('执行完毕')

    def make_data(self):
        res = []
        for obj in self.form:
            res.append(int(obj.text()))
        return res

    def close_task(self):
        app_root.dialog = None
        if control_func.run_task.isRunning():
            control_func.run_task.terminate()
            app_root.ui_log.warning('流程强行中断中')
            control_func.run_task.wait()
            app_root.ui_log.success('流程已被中断')
            app_root.root.normal_window()
        self.reject()

    def closeEvent(self, event):
        self.close_task()


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
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
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


class EditParamDialog(BaseDialog):
    def __init__(self, parent=None):
        self.out_layout = QVBoxLayout()
        self.form_data = {}

        self.confirm = CommonButton('确定')
        self.cancel = CommonButton('取消')
        super().__init__(parent)

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
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
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
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


class CommonButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)

    def leaveEvent(self, event):
        self.unsetCursor()


class KeyRecord:
    def __init__(self, key):
        self.key = key


class KeyWatchThread(QThread):
    press_signal = pyqtSignal(KeyRecord)
    release_signal = pyqtSignal(KeyRecord)

    start_run_signal = pyqtSignal(str)
    event_signal = pyqtSignal(list)
    update_status_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.mouse_listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move, on_scroll=self.on_scroll)
        self.key_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)

        # 监听状态：1+ - 静默监听， 10 - 待录制监听, 11 - 录制中
        self._status = 1

        # 录制事件
        self._events = []

        self.update_status_signal.connect(self.update_status)

        self.sig = 0

    def update_status(self, s):
        self._status = s

    def append_event(self, event):
        self._events.append({"run_time": time.time(), "event": event})

    def clear_events(self):
        self._events = []

    def on_click(self, x, y, button, pressed):
        if self._status == 11:
            self.append_event(['click', button.name, pressed, x, y])

    def on_move(self, x, y):
        if self._status == 11:
            self.append_event(['move', x, y])

    def on_scroll(self, x, y, dx, dy):
        if self._status == 11:
            self.append_event(['scroll', x, y, dx, dy])

    def on_press(self, key):
        if self._status == 11:
            if key == keyboard.Key.esc:
                self.update_status(1)
                app_root.ui_log.info('录制结束')
                self.event_signal.emit(self._events)
            else:
                self.append_event(['press', str(key)])

        self.press_signal.emit(KeyRecord(key))

    def on_release(self, key):
        # app_root.ui_log.info('ok')
        # 录制中
        if self._status == 11:
            self.append_event(['release', str(key)])

        # 就绪 转 执行
        if self._status == 10 and key == keyboard.Key.down:
            app_root.ui_log.info('开始录制')
            self.clear_events()
            self.update_status(11)
            self.start_run_signal.emit('录制中')

        self.release_signal.emit(KeyRecord(key))

    def run(self):
        self.key_listener.start()
        self.mouse_listener.start()
        while True:
            if settings.RUN_ENV == 'Windows':
                break
            app_root.ui_log.info('校验中')
            time.sleep(2)
            app_root.ui_log.info(f'key {self.key_listener.is_alive()}')
            if not self.key_listener.is_alive():
                self.key_listener.stop()
                self.key_listener.join()
                self.key_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
                self.key_listener.start()
                continue

            app_root.ui_log.info(f'mouse {self.mouse_listener.is_alive()}')
            if not self.mouse_listener.is_alive():
                self.mouse_listener.stop()
                self.mouse_listener.join()
                self.mouse_listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move,
                                                     on_scroll=self.on_scroll)
                self.mouse_listener.start()
                continue
            break
        self.sig = 1
        # app_root.ui_log.warning('success')
        # app_root.ui_log.info(f'{self.key_listener.is_alive()}, {self.mouse_listener.is_alive()}')
        self.key_listener.join()
        self.mouse_listener.join()


class LogThread(QThread, settings.Log):
    log_signal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def capture_msg(self, message):
        super().capture_msg(message)
        self.log_signal.emit(message)


class LogEditBox(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
        QTextEdit{
            background: #1e1f22;
            font-weight: bold;
            color: white;
            font-size: 13px;
        }
        """)

    def append_color_info(self, msg: str):
        info = msg.split('|')
        time_color = QColor('#00CC99')
        # msg = f'{info[0]:^23}|{info[2]:^11}|{"".join(info[3:])}'
        document = self.document()
        cursor = QTextCursor(document)
        cursor.movePosition(QTextCursor.End)

        # 插入时间
        time_format = QTextCharFormat()
        time_format.setForeground(time_color)
        cursor.setCharFormat(time_format)
        cursor.insertText(f'{info[0]:^23}')

        # 插入线条
        line_format = QTextCharFormat()
        line_format.setForeground(QColor('white'))
        cursor.setCharFormat(line_format)
        cursor.insertText('| ')

        # 插入log
        color = QColor('#CCCCCC')
        if len(info) > 3:
            log_type = info[2].lower()
            if 'warning' in log_type:
                color = QColor('#FFFF33')
            elif 'error' in log_type:
                color = QColor('#FF0000')
            elif 'success' in log_type:
                color = QColor('#33FF33')
            elif 'debug' in log_type:
                color = QColor('#66FFFF')
            elif 'critical' in log_type:
                color = QColor('#990000')

        log_format = QTextCharFormat()
        log_format.setForeground(color)
        cursor.setCharFormat(log_format)
        cursor.insertText(f'{info[2]:^11}|{"".join(info[3:])}')

        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())


class ConfDialog(BaseDialog):
    def __init__(self, parent=None):
        self.out_layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)

        self.form = []
        self.apply = CommonButton('应用')
        self.cancel = CommonButton('关闭')
        super().__init__(parent)

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle('系统变量设置')
        self.setGeometry(100, 100, 700, 400)
        self.center_on_parent()
        self.setStyleSheet("background-color: white;")

        # 创建滚动区域
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
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

        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(10)

        self.scroll_area.setWidget(self.container_widget)

        self.out_layout.setContentsMargins(0, 0, 0, 0)
        self.out_layout.addWidget(self.scroll_area)
        self.container_layout.setSpacing(10)
        self.container_layout.addStretch()
        self.setLayout(self.out_layout)

        self.part_settings_ui()
        self.part_software_conf_ui()
        self.part_button_group_ui()

        self.load_action()

    def load_action(self):
        self.apply.clicked.connect(self.action_confirm)
        self.cancel.clicked.connect(self.close_dialog)

    def action_confirm(self):
        for e in self.form:
            c = e.property('origin')
            temp_val = e.text()
            if temp_val != c.values:
                app_root.ui_log.success(f'{c.depict_key}已更新为{temp_val}')
                c.values = temp_val
                handler.update_instance(c)
        self.close_dialog()

    def part_settings_ui(self):
        setting_layout = QVBoxLayout()

        label = TitleLabel('软件设置')
        setting_layout.addWidget(label)
        setting_layout.setSpacing(0)

        group = QGroupBox()
        group.setStyleSheet("color: black")
        group_layout = QVBoxLayout()
        group.setLayout(group_layout)
        conf_settings = handler.search_type_conf(0)

        for c in conf_settings:
            line = QHBoxLayout()
            t = QLabel(c.depict_key)
            t.setStyleSheet("background-color: transparent;")
            e = QLineEdit(c.values)

            e.setProperty('origin', c)
            self.form.append(e)
            e.modified_stylesheet = "QLineEdit { background-color: #fcf3cf; }"
            e.textChanged.connect(self.on_line_edit_text_changed)
            line.addWidget(t)
            line.addWidget(e)
            line.setStretchFactor(t, 1)
            line.setStretchFactor(e, 5)
            group_layout.addLayout(line)

        setting_layout.addWidget(group)

        self.container_layout.addLayout(setting_layout)

    def part_software_conf_ui(self):
        software_conf_layout = QVBoxLayout()

        label = TitleLabel('统一平台设置')
        software_conf_layout.addWidget(label)
        software_conf_layout.setSpacing(0)

        group = QGroupBox()
        group.setStyleSheet("color: black")
        group_layout = QVBoxLayout()
        group.setLayout(group_layout)
        conf_software = handler.search_type_conf(0)

        for c in conf_software:
            line = QHBoxLayout()
            t = QLabel(c.depict_key)
            t.setStyleSheet("background-color: transparent;")
            e = QLineEdit(c.values)
            e.modified_stylesheet = "QLineEdit { background-color: #fcf3cf; }"
            e.textChanged.connect(self.on_line_edit_text_changed)
            line.addWidget(t)
            line.addWidget(e)
            line.setStretchFactor(t, 1)
            line.setStretchFactor(e, 5)
            group_layout.addLayout(line)

        software_conf_layout.addWidget(group)

        self.container_layout.addLayout(software_conf_layout)

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
        button_layout.addWidget(self.apply)
        button_layout.addWidget(self.cancel)

        # 设置按钮布局的间距
        button_layout.setContentsMargins(10, 10, 10, 10)
        button_layout.setSpacing(10)

        # 添加弹簧到主布局，确保按钮在底部
        self.out_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 将按钮布局添加到主布局的底部
        self.out_layout.addLayout(button_layout)

    def on_line_edit_text_changed(self):
        # 获取发送信号的 QLineEdit
        sender = self.sender()
        if sender:
            # 设置修改后的样式
            sender.setStyleSheet(sender.modified_stylesheet)


class TitleLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
                        QLabel {
                              color: black;
                              background-color: #cccccc;
                              font: bold 14px;
                              padding: 5px;
                           }
                        """)
