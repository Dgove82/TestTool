from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QPushButton, QSpacerItem, QSizePolicy, QFrame, QDialog,
    QGraphicsView, QGraphicsScene
)
from PyQt5.QtCore import Qt, QDateTime, QRectF
from PyQt5.QtGui import QPixmap, QFont
import settings
import os
from src.frontend.components import ClickLabel


def get_records():
    # 这里应该是从数据库获取记录的逻辑
    # 下面是示例数据
    return [
        settings.Record(id=1, event='Click', image_name='img.png', record_time='2024-11-17 10:00:00'),
        settings.Record(id=2, event='Click', image_name='img_1.png', record_time='2024-11-17 10:00:00'),
        settings.Record(id=3, event='Click', image_name='img_1.png', record_time='2024-11-17 10:00:00'),
        settings.Record(id=4, event='Click', image_name='img_1.png', record_time='2024-11-17 10:00:00'),
        settings.Record(id=5, event='Click', image_name='img_1.png', record_time='2024-11-17 10:00:00'),
        settings.Record(id=6, event='Click', image_name='img_1.png', record_time='2024-11-17 10:00:00'),
        # 更多记录...
    ]


class ImageViewer(QDialog):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("查看图片")
        self.setModal(True)
        self.pixmap_item = None
        self.setGeometry(100, 100, 300, 300)
        self.init_ui(pixmap)

    def init_ui(self, pixmap):
        self.graphics_view = QGraphicsView(self)
        self.graphics_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.graphics_view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.graphics_view.wheelEvent = self.zoom

        self.scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.scene)

        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.fitInView()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.graphics_view)
        self.setLayout(self.layout)

    def fitInView(self):
        rect = QRectF(self.pixmap_item.pixmap().rect())
        if not rect.isNull():
            unity = self.graphics_view.transform().mapRect(QRectF(0, 0, 1, 1))
            self.graphics_view.scale(1 / unity.width(), 1 / unity.height())
            view_rect = self.graphics_view.viewport().rect()
            scene_rect = self.graphics_view.transform().mapRect(rect)
            factor = min(view_rect.width() / scene_rect.width(),
                         view_rect.height() / scene_rect.height())
            self.graphics_view.scale(factor, factor)
            self.graphics_view.centerOn(rect.center())

    def zoom(self, event):
        if event.angleDelta().y() > 0:
            self.graphics_view.scale(1.1, 1.1)
        else:
            self.graphics_view.scale(0.9, 0.9)


class WatchTab(QWidget):
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.name = '操作回溯'

        self.init_ui()

    # def init_ui(self):
    #     watch_layout = QVBoxLayout()
    #     self.setLayout(watch_layout)
    #     tip_label = QLabel('敬请期待')
    #     tip_label.setStyleSheet('font-size: 60pt')
    #     tip_label.setAlignment(Qt.AlignCenter)
    #     watch_layout.addWidget(tip_label)
    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_content = QWidget()
        self.scroll_area_layout = QHBoxLayout()
        self.scroll_area_layout.setContentsMargins(0, 10, 0, 10)
        self.scroll_area_content.setLayout(self.scroll_area_layout)
        self.scroll_area.setWidget(self.scroll_area_content)
        self.layout.addWidget(self.scroll_area)
        self.layout.setStretchFactor(self.scroll_area, 7)

        self.load_records()
        self.scroll_area_layout.setSpacing(10)

        self.load_control_bar()

    def load_records(self):
        records = get_records()
        for i, record in enumerate(reversed(records)):
            step_widget = self.create_step_widget(record)
            self.scroll_area_layout.addWidget(step_widget)

    def create_step_widget(self, record):
        step_widget = QWidget()
        # 设置边框样式
        step_widget.setObjectName("StepWidget")
        step_widget.setStyleSheet('''
                    #StepWidget {
                        border: 1px solid #DCDFE6; 
                        border-radius: 4px;
                    }
                ''')

        # 创建步骤内容布局
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(5, 5, 5, 5)
        step_widget.setLayout(content_layout)

        # 创建步骤时间
        step_label = QLabel(f"◉ Step:{record.id}")
        step_label.setStyleSheet("color: #409EFF; border: none")
        step_label.setFixedHeight(30)
        step_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(step_label)
        content_layout.setStretchFactor(step_label, 1)

        # 创建步骤图片
        image_label = ClickLabel()
        image_label.setFixedHeight(100)
        image_label.setMinimumWidth(100)
        image_label.setAlignment(Qt.AlignCenter)
        image_path = os.path.join(r'/Users/dgove/Downloads/image', record.image_name)
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
                # 设置鼠标点击事件
                image_label.mousePressEvent = lambda event: self.show_image_dialog(pixmap)
        else:
            image_label.setText("No Image")
        image_label.setStyleSheet("border: 1px solid #DCDFE6; border-radius: 4px;")
        content_layout.addWidget(image_label)

        # 创建步骤时间
        time_label = QLabel(f"{record.record_time}")
        time_label.setStyleSheet("color: #909399; border: none")
        content_layout.addWidget(time_label)
        content_layout.setStretchFactor(time_label, 1)

        # 创建步骤标题和描述
        step_title = QLabel("点击")
        step_title.setStyleSheet("color: #909399; border: none")
        content_layout.addWidget(step_title)
        content_layout.setStretchFactor(step_title, 1)
        content_layout.setSpacing(0)

        # # 创建步骤连接线
        # line_label = QLabel()
        # line_label.setFixedHeight(5)
        # line_label.setStyleSheet("""
        #     background-color: #DCDFE6;
        #     width: 2px;
        # """)
        # step_widget_layout.addWidget(line_label)

        return step_widget

    def show_image_dialog(self, pixmap):
        dialog = ImageViewer(pixmap)
        dialog.exec_()

    def load_control_bar(self):
        bar = QHBoxLayout()
        self.layout.addLayout(bar)
        self.layout.setStretchFactor(bar, 3)

        title = QLabel('控制栏')
        bar.addWidget(title)
