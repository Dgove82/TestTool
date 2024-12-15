import json
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea
)
from PyQt5.QtCore import Qt, QDateTime, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from pynput import keyboard

import settings
import os
from src.frontend.public import app_root
from src.frontend.components import ClickLabel, TitleLabel, CommonTimeEdit, CommonButton, CommonLabel
from src.frontend.components import ImageViewerDialog
from src.intermediary.center import SQLserver
from common.tools import TimeTool
from sqlalchemy import or_, and_


class RecordHandler(SQLserver):

    def get_records(self, count=10):
        session = self.get_db()
        records = session.query(settings.Record).order_by(settings.Record.record_time.desc()).limit(count).all()
        session.close()
        return list(reversed(records))

    def select_time_range(self, start, end):
        session = self.get_db()
        records = session.query(settings.Record).order_by(settings.Record.record_time.desc()).filter(
            settings.Record.record_time.between(start, end)).all()
        session.close()
        return list(reversed(records))

    def select_time_operation_range(self, start, end):
        session = self.get_db()
        operations = session.query(settings.EventOperation).filter(
            and_(
                settings.EventOperation.start_time <= end,
                settings.EventOperation.end_time >= start,
            )
        ).order_by(settings.EventOperation.id.asc()).all()
        session.close()
        return operations

    def append_record(self, event: dict, image_name: str):
        # 仅处理点击, 添加记录
        click_type = {"left": '左键', 'right': '右键', 'middle': '中键'}
        new_record = settings.Record()
        new_record.record_time = event.get("run_time")
        action = event.get("event")
        new_record.event = f"在({int(action[3])}, {int(action[4])})处按下{click_type.get(action[1])}"
        new_record.image_name = image_name
        self.insert(new_record)
        records = self.get_last_data(settings.Record, 1)
        if len(records) == 1:
            return records[0]
        raise

    def add_events(self, events: list):
        if len(events) != 0:
            new_record = settings.EventOperation()
            new_record.start_time = events[0].get('run_time')
            new_record.end_time = events[-1].get('run_time')
            new_record.events = json.dumps(events)
            self.insert(new_record)
        else:
            app_root.ui_log.warning('并无事件需要被记录')


class WatchTab(QWidget):
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.name = '操作回溯'
        self.sql = RecordHandler()

        self.layout = QHBoxLayout()
        self.control_bar = QVBoxLayout()
        self.scroll_area_layout = QVBoxLayout()

        self.start_time_edit = CommonTimeEdit()
        self.end_time_edit = CommonTimeEdit()

        self.is_current = False
        self.is_record = False
        self.trace_task = None
        self.record_btn = CommonButton('开始录制')
        self.preview_btn = CommonButton('片段预览')
        self.reback_btn = CommonButton('片段回溯')
        self.delete_btn = CommonButton('片段删除')
        self.delete_btn.setDisabled(True)

        self.init_ui()

    def init_ui(self):
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.load_control_bar()
        self.scroll_records_show_ui()

        self.load_action()

    def load_control_bar(self):
        self.layout.addLayout(self.control_bar)
        self.layout.setStretchFactor(self.control_bar, 3)
        self.control_bar.setContentsMargins(5, 5, 5, 5)

        title = TitleLabel('片段操作：各项操作仅在该界面有效')
        self.control_bar.addWidget(title)
        self.control_bar.setStretchFactor(self.control_bar, 1)

        # self.start_time_edit.setDateTime(QDateTime.currentDateTime())  # 设置当前日期和时间
        # print(self.start_time_edit.dateTime().toSecsSinceEpoch())

        self.time_info_ui()
        self.button_group_ui()

        self.control_bar.addStretch()

    def time_info_ui(self):
        start_layout = QHBoxLayout()
        start_label = TitleLabel('开始时间')
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_time_edit)
        start_layout.setStretchFactor(start_label, 3)
        start_layout.setStretchFactor(self.start_time_edit, 7)

        end_layout = QHBoxLayout()
        end_label = TitleLabel('结束时间')
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.end_time_edit)
        end_layout.setStretchFactor(end_label, 3)
        end_layout.setStretchFactor(self.end_time_edit, 7)

        self.control_bar.addLayout(start_layout)
        self.control_bar.addLayout(end_layout)

    def button_group_ui(self):
        button_group = QVBoxLayout()
        # 写入
        button_group.addWidget(self.record_btn)
        self.record_btn.setIcon(QIcon(os.path.join(settings.DEPS_PROGRAM, 'assets/start_record.png')))

        # 预览
        button_group.addWidget(self.preview_btn)

        # 回溯
        button_group.addWidget(self.reback_btn)
        # 删除
        button_group.addWidget(self.delete_btn)

        self.control_bar.addLayout(button_group)

    def load_action(self):
        self.record_btn.clicked.connect(self.action_record_handler)
        self.preview_btn.clicked.connect(self.action_preview_clips)
        self.reback_btn.clicked.connect(self.action_reback_clips)
        self.delete_btn.clicked.connect(self.action_delete_clips)
        app_root.mult_tab.currentChanged.connect(self.action_tab_changed)
        app_root.key_watch.event_signal.connect(self.action_end_record)
        app_root.key_watch.mouse_signal.connect(self.action_add_step_in_pre)
        app_root.key_watch.press_signal.connect(self.action_press_key)

    def action_tab_changed(self):
        if self.parent().currentIndex() == self.index:
            self.is_current = True
        elif self.is_current:
            self.is_current = False
            if self.is_record:
                self.action_record_handler()
                app_root.ui_log.warning('切换页面，自动结束录制')

    def action_record_handler(self):
        self.is_record = not self.is_record
        if self.is_record:
            self.action_start_record()
        else:
            events = app_root.key_watch.record_events
            self.action_end_record(events)

    def action_start_record(self):
        app_root.ui_log.info('开始录制')
        self.record_btn.setText('录制中,按<Esc>快捷结束')
        self.record_btn.setIcon(QIcon(os.path.join(settings.DEPS_PROGRAM, 'assets/recording.png')))
        app_root.key_watch.clear_events()
        app_root.key_watch.update_status(11)

    def action_add_step_in_pre(self, event):
        if self.is_record:
            image_name = settings.record.img_record(save_path=settings.Files.IMAGE_EVENT_DIR)
            record = self.sql.append_record(event=event.detail, image_name=image_name)
            if self.scroll_area_layout.count() == 0:
                self.insert_record_into_pre_top(record, arrow=False)
            else:
                self.insert_record_into_pre_top(record, arrow=True)

    def action_end_record(self, events):
        if self.is_record and self.is_current:
            if app_root.key_watch.status != 1:
                app_root.key_watch.update_status(1)
            self.is_record = False
            self.sql.add_events(events)
            self.record_btn.setText('开始录制')
            self.record_btn.setIcon(QIcon(os.path.join(settings.DEPS_PROGRAM, 'assets/start_record.png')))
            app_root.ui_log.info('录制结束')

    def action_preview_clips(self):
        form_data = self.get_time_clip()
        records = self.sql.select_time_range(start=form_data["start_time"], end=form_data["end_time"])
        self.load_records_in_pre(records)
        app_root.ui_log.info(f'共加载{len(records)}条记录')

    def action_divide_clips_by_time(self):
        form_data = self.get_time_clip()
        records = self.sql.select_time_operation_range(start=form_data["start_time"], end=form_data["end_time"])
        if records:
            start = 0
            start_events = json.loads(records[0].events)
            for e in start_events:
                if e['run_time'] < form_data["start_time"] - 0.2:
                    start += 1

            end = len(records[-1])
            end_events = json.loads(records[-1].events)
            for item in end_events:
                if item['run_time'] > form_data["end_time"] + 0.2:
                    end -= 1
            pass

    def action_reback_clips(self):
        form_data = self.get_time_clip()
        records = self.sql.select_time_operation_range(start=form_data["start_time"], end=form_data["end_time"])
        operations = [json.loads(r.events) for r in records]
        if self.trace_task is None:
            self.reback_btn.setDisabled(True)
            self.reback_btn.setText('回溯中')
            self.trace_task = TraceThread(form_data, operations)
            self.trace_task.finish_signal.connect(self.action_trace_finish)
            self.trace_task.start()
        else:
            app_root.ui_log.warning('正在回溯中')

    def action_trace_finish(self):
        self.trace_task = None
        self.reback_btn.setText('片段回溯')
        self.reback_btn.setDisabled(False)

    def action_press_key(self, key):
        if self.is_current and key.key == keyboard.Key.esc:
            if self.trace_task is not None:
                self.trace_task.terminate()
                self.trace_task.wait()
                app_root.ui_log.warning('回溯被中断')
                self.action_trace_finish()

    def action_delete_clips(self):
        form_data = self.get_time_clip()
        print(form_data)

    def get_time_clip(self):
        form_data = {}
        form_data.update({"start_time": self.start_time_edit.dateTime().toSecsSinceEpoch()})
        form_data.update({"end_time": self.end_time_edit.dateTime().toSecsSinceEpoch()})
        return form_data

    def scroll_records_show_ui(self):
        scroll_area = QScrollArea(self)
        scroll_area_content = QWidget()
        scroll_area_content.setObjectName('scroll_area_content')
        scroll_area_content.setStyleSheet("""
            #scroll_area_content{
                background-color: #ececec;
            }
        """)

        scroll_area.setWidgetResizable(True)
        self.scroll_area_layout.setContentsMargins(5, 10, 5, 10)
        scroll_area_content.setLayout(self.scroll_area_layout)
        scroll_area.setWidget(scroll_area_content)
        self.scroll_area_layout.setSpacing(10)
        self.layout.addWidget(scroll_area)
        self.layout.setStretchFactor(scroll_area, 4)

        self.action_init_pre()

    def insert_record_into_pre_top(self, record, arrow=True):
        if arrow:
            guide_step_arrow = CommonLabel("⬆")
            guide_step_arrow.setAlignment(Qt.AlignCenter)
            self.scroll_area_layout.insertWidget(0, guide_step_arrow)
        step_widget = self.create_step_widget(record)
        self.scroll_area_layout.insertWidget(0, step_widget)

    def action_clear_pre(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.action_clear_pre(item.layout())

    def action_init_pre(self):
        records = self.sql.get_records()
        self.load_records_in_pre(records)

    def load_records_in_pre(self, records):
        self.action_clear_pre(self.scroll_area_layout)
        if len(records) > 0:
            start_time = QDateTime.fromSecsSinceEpoch(records[0].record_time - 1)
            self.start_time_edit.setDateTime(start_time)
            end_time = QDateTime.fromSecsSinceEpoch(records[-1].record_time + 1)
            self.end_time_edit.setDateTime(end_time)

            for index, record in enumerate(records):
                if index != 0:
                    self.insert_record_into_pre_top(record, arrow=True)
                else:
                    self.insert_record_into_pre_top(record, arrow=False)
        else:
            self.start_time_edit.setDateTime(QDateTime.currentDateTime())
            self.end_time_edit.setDateTime(QDateTime.currentDateTime())

        # print(self.start_time_edit.dateTime().toSecsSinceEpoch())

    def create_step_widget(self, record):
        step_widget = QWidget()
        # 设置边框样式
        step_widget.setObjectName("StepWidget")
        step_widget.setStyleSheet("""
                    #StepWidget {
                        border: 1px solid #DCDFE6; 
                        border-radius: 4px;
                        background-color: #ececec;
                    }
                """)

        # 创建步骤内容布局
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(5, 5, 5, 5)
        step_widget.setLayout(content_layout)

        # 创建步骤顺序
        step_label = QLabel(f"◉ Step:{record.id}")
        step_label.setStyleSheet("color: #409EFF; border: none")
        step_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(step_label)
        content_layout.setStretchFactor(step_label, 1)

        # 创建步骤图片
        image_label = ClickLabel()
        image_label.setFixedHeight(100)
        image_label.setMinimumWidth(100)
        image_label.setAlignment(Qt.AlignCenter)
        image_path = os.path.join(settings.Files.IMAGE_EVENT_DIR, f'{record.image_name}.png')
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
                # 设置鼠标点击事件
                image_label.mousePressEvent = lambda event: self.show_image_dialog(pixmap)
        else:
            image_label.setText("图片消失了")
        image_label.setStyleSheet("border: 1px solid #DCDFE6; border-radius: 4px;")
        content_layout.addWidget(image_label)
        content_layout.setStretchFactor(image_label, 1)

        desc_widget = QWidget()
        desc_widget.setObjectName("DescWidget")
        desc_widget.setStyleSheet("""
                    #DescWidget {
                        border: 1px solid #DCDFE6; 
                        border-radius: 4px;
                    }
                """)
        desc_layout = QVBoxLayout()
        desc_widget.setLayout(desc_layout)
        desc_widget.setFixedHeight(100)

        # 创建步骤时间
        time_label = QLabel(f"{TimeTool.strftime_for_format(record.record_time)}")
        time_label.setStyleSheet("color: #909399; border: none")
        desc_layout.addWidget(time_label)
        desc_layout.setStretchFactor(time_label, 1)

        # 创建步骤标题和描述
        step_title = CommonLabel(record.event)
        step_title.setStyleSheet("color: #909399; border: none")
        desc_layout.addWidget(step_title)
        desc_layout.setStretchFactor(step_title, 1)

        content_layout.addWidget(desc_widget)
        content_layout.setStretchFactor(desc_widget, 8)

        return step_widget

    def show_image_dialog(self, pixmap):
        app_root.dialog = ImageViewerDialog(pixmap, app_root.root)
        app_root.dialog.exec_()


class TraceThread(QThread):
    finish_signal = pyqtSignal()

    def __init__(self, border, operations, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border = border
        self.operations = operations

    def run(self):
        self.trace_task()
        self.finish_signal.emit()

    def trace_task(self):
        if self.operations:
            start = 0
            for item in self.operations[0]:
                if item['run_time'] < self.border["start_time"] - 0.2:
                    start += 1
            end = len(self.operations[-1])
            for item in self.operations[-1]:
                if item['run_time'] > self.border["end_time"] + 0.2:
                    end -= 1

            if len(self.operations) == 1:
                self.operations[0] = self.operations[0][start:end]
            else:
                self.operations[0] = self.operations[0][start:]
                self.operations[-1] = self.operations[-1][:end]

            app_root.ui_log.info('开始回溯')
            for op in self.operations:
                settings.watch.replay_events(op)
            app_root.ui_log.success('回溯结束')
        else:
            app_root.ui_log.warning('没有内容可以回溯')