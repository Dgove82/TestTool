from PyQt5.QtWidgets import QVBoxLayout, QGraphicsView, QGraphicsScene
from src.frontend.components.dialogs.dialog_base import BaseDialog
from PyQt5.QtCore import Qt, QRectF


class ImageViewerDialog(BaseDialog):
    def __init__(self, pixmap, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.graphics_view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.layout = QVBoxLayout(self)
        self.pixmap_item = None

        self.init_image_ui(pixmap)

    def init_ui(self):
        self.setWindowTitle("查看图片")
        self.setModal(True)
        self.setGeometry(100, 100, 300, 300)
        self.center_on_parent()

    def init_image_ui(self, pixmap):
        self.graphics_view.setStyleSheet("""
                                    QGraphicsView {
                                        background-color: #E5EAF3; 
                                    }
                                """ + self.styleSheet())
        self.graphics_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.graphics_view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.graphics_view.wheelEvent = self.zoom

        self.graphics_view.setScene(self.scene)

        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.fit_in_view()

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.graphics_view)
        self.setLayout(self.layout)

    def fit_in_view(self):
        rect = QRectF(self.pixmap_item.pixmap().rect())
        if not rect.isNull():
            unity = self.graphics_view.transform().mapRect(QRectF(0, 0, 1, 1))
            self.graphics_view.scale(1 / unity.width(), 1 / unity.height())
            view_rect = self.graphics_view.viewport().rect()
            scene_rect = self.graphics_view.transform().mapRect(rect)
            factor = min(scene_rect.width() / view_rect.width(),
                         scene_rect.height() / view_rect.height())
            self.graphics_view.scale(factor, factor)
            self.graphics_view.centerOn(rect.center())

    def zoom(self, event):
        if event.angleDelta().y() > 0:
            self.graphics_view.scale(1.1, 1.1)
        else:
            self.graphics_view.scale(0.9, 0.9)
