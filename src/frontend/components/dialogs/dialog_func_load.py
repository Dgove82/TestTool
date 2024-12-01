from src.frontend.components.dialogs.dialog_base import BaseDialog
from src.frontend.components.control import CommonButton, TitleLabel, CommonInfoBox, CommonLineEdit
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
import settings
from src.frontend.public import app_root, control_func
from src.frontend.components.threads.thread_load import LoadThread
from src.intermediary.data_load import FuncUpdate


class LoadDialog(BaseDialog):
    def __init__(self, parent=None):
        self.out_layout = QVBoxLayout()

        self.info = CommonInfoBox()
        self.update_btn = CommonButton('检查更新/拉取方法库')
        self.confirm = CommonButton('加载')
        self.cancel = CommonButton('关闭')
        self.load_task = LoadThread()
        super().__init__(parent)
        self.setStyleSheet("""
                                QDialog {
                                    background-color: #E5EAF3; 
                                }
                            """ + self.styleSheet())

    def init_ui(self):
        self.setWindowTitle('方法加载')
        self.setGeometry(100, 100, 725, 300)
        self.center_on_parent()
        self.setLayout(self.out_layout)

        self.body_ui()
        self.param_ui()
        self.bottom_ui()

        self.load_action()

    def load_action(self):
        self.confirm.clicked.connect(self.action_load_func)
        self.cancel.clicked.connect(self.close_task)
        self.update_btn.clicked.connect(self.action_action_update)
        self.load_task.finished.connect(self.task_finished)

    def body_ui(self):
        msg = f'Tips:如果加载不到方法，请尝试"检查更新/拉取方法库"\n若需要修改以下配置请前往设置>程序设置'
        self.info.setText(msg)
        self.out_layout.addWidget(self.info)

    def param_ui(self):
        param_body_layout = QVBoxLayout()
        source_layout = QHBoxLayout()
        source_label = TitleLabel("方法库下载源")
        source_edit = CommonLineEdit(str(settings.Files.LIBRARY_ORIGIN))
        source_edit.setEnabled(False)
        source_layout.addWidget(source_label)
        source_layout.addWidget(source_edit)
        source_layout.setStretchFactor(source_label, 2)
        source_layout.setStretchFactor(source_edit, 8)

        lib_layout = QHBoxLayout()
        lib_label = TitleLabel("方法库文件")
        lib_edit = CommonLineEdit(str(settings.Files.LIBRARY_PATH))
        lib_edit.setEnabled(False)
        lib_layout.addWidget(lib_label)
        lib_layout.addWidget(lib_edit)
        lib_layout.setStretchFactor(lib_label, 2)
        lib_layout.setStretchFactor(lib_edit, 8)

        param_body_layout.addLayout(source_layout)
        param_body_layout.addLayout(lib_layout)
        self.out_layout.addLayout(param_body_layout)

    def bottom_ui(self):
        self.out_layout.addWidget(self.update_btn)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.confirm)
        button_layout.addWidget(self.cancel)
        self.out_layout.addLayout(button_layout)

    def action_load_func(self):
        app_root.ui_log.info('开始加载')
        self.info.setText('解析中')
        self.confirm.setDisabled(True)
        self.load_task.start()

    def action_action_update(self):
        handler = FuncUpdate()
        handler.update_handler()
        if handler.versions is not None:
            current = handler.versions.get("now", None)
            history = handler.versions.get("history")
            self.info.setText(f'当前版本{current}\n更新内容{history.get(current, None)}\n更新完成，请尝试加载')
        else:
            app_root.ui_log.warning('服务器异常')

    def task_finished(self):
        self.confirm.setDisabled(False)
        self.info.setText('加载完成')
        control_func.actions.action_search()
        app_root.ui_log.success('加载完毕')

    def close_task(self):
        app_root.dialog = None
        if self.load_task.isRunning():
            self.load_task.terminate()
            self.load_task.wait()
            app_root.ui_log.success('解析被中断')
        self.reject()

    def closeEvent(self, event):
        self.close_task()
