import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from common.tools import LogTool, watch
from src.frontend.public import control_func, app_root
from src.control.center import ControlCenter
from pynput import keyboard, mouse


class TaskThread(QThread):
    finish_signal = pyqtSignal()

    def run(self):
        ControlCenter.steps_exec()
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
        self.info_label = QLabel('执行中，若是关闭窗口会结束流程')

        super().__init__(parent)

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle('流程')
        self.setGeometry(100, 100, 200, 100)
        self.center_on_parent()

        dialog_layout = QVBoxLayout()
        self.info_label = QLabel('执行中，若是关闭窗口会结束流程')
        self.info_label.setAlignment(Qt.AlignCenter)
        dialog_layout.addWidget(self.info_label)
        self.setLayout(dialog_layout)

    def closeEvent(self, event):
        super().closeEvent(event)
        if control_func.run_task.isRunning():
            control_func.run_task.terminate()
            app_root.ui_log.warning('流程强行中断中')
            control_func.run_task.wait()
            app_root.ui_log.success('流程已被中断')
        event.accept()


class FuncParamDialog(BaseDialog):
    """
    方法参数设置会话框
    """

    def __init__(self, parent=None):
        self.out_layout = QVBoxLayout()
        self.form_data = {}

        self.confirm = CommonButton('确定')
        super().__init__(parent)

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle('配置')
        self.setGeometry(100, 100, 300, 300)
        self.center_on_parent()

        self.setLayout(self.out_layout)
        # self.param_config_header_ui()
        self.param_config_body_ui()
        self.param_config_bottom_ui()

    def param_config_header_ui(self):
        header_layout = QVBoxLayout()
        label_info = QLabel()
        label_info.setText('方法参数配置')
        label_info.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(label_info)
        self.out_layout.addLayout(header_layout)

    def param_config_body_ui(self):
        body_layout = QVBoxLayout()
        line_layout = QHBoxLayout()
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

        if ControlCenter.record_checked is not None:
            func = ControlCenter.search_record[ControlCenter.record_checked]
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
        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(self.confirm)
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

    def close_dialog(self):
        app_root.dialog = None
        self.accept()


class WatchThread(QThread):
    start_signal = pyqtSignal(str)
    event_signal = pyqtSignal(list)

    def run(self):
        watch.mouse_listener = mouse.Listener(on_click=watch.on_click, on_move=watch.on_move, on_scroll=watch.on_scroll)
        watch.keyboard_listener = keyboard.Listener(on_press=watch.on_press, on_release=watch.on_release)

        watch.keyboard_listener.start()
        while True:
            if watch.is_listening:
                self.start_signal.emit('录制中')
                break
        watch.mouse_listener.join()
        watch.keyboard_listener.join()
        self.event_signal.emit(watch.events)


class DefineParamDialog(BaseDialog):
    def __init__(self, parent):
        self.running = False
        self.form_data = {}

        self.dialog_layout = QVBoxLayout()
        self.watch_thread = WatchThread()
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
        self.watch_thread.start_signal.connect(self.start_record)

    def action_recoding(self):
        watch.events_clear()
        self.running = True
        self.watch_thread.start()
        self.update_tip('按下 ⬇️ 键开始录制')
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

    def close_dialog(self):
        app_root.dialog = None
        self.accept()

    def closeEvent(self, event):
        if self.running:
            event.ignore()
            app_root.dialog = None
            self.update_tip('录制中，无法关闭，请通过按<esc>退出')
        else:
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

    def __init__(self):
        super().__init__()
        self.key_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.meta_hotkey = True

    def on_press(self, key):
        self.press_signal.emit(KeyRecord(key))

    def on_release(self, key):
        self.release_signal.emit(KeyRecord(key))

    def run(self):
        self.key_listener.start()


class LogThread(QThread, LogTool):
    log_signal = pyqtSignal(str)

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
        color = QColor('white')
        if len(info) > 3:
            log_type = info[2].lower()
            if 'warning' in log_type:
                color = QColor('#a58813')
            elif 'error' in log_type:
                color = QColor('#dc3d2d')
            elif 'success' in log_type:
                color = QColor('#56902a')
            msg = f'{info[0]}|{info[2]:<9}|{"".join(info[3:])}'
        document = self.document()
        cursor = QTextCursor(document)
        cursor.movePosition(QTextCursor.End)
        char_format = QTextCharFormat()
        char_format.setForeground(color)
        cursor.setCharFormat(char_format)
        cursor.insertText(msg)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
