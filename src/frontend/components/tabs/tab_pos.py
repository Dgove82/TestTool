from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import *
from pynput import keyboard
import pyautogui
from src.frontend.public import app_root
from src.frontend.components import TitleLabel, NoAutoScrollTreeWidget, CssTableView
import settings
import traceback


class CustomTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, text, custom_data, parent=None):
        super().__init__(parent)
        self.setText(0, text)
        self.custom_data = custom_data

    def get_custom_data(self):
        return self.custom_data


class PosTab(QWidget):
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index

        self.out_layout = QHBoxLayout()

        self.tree_widget = NoAutoScrollTreeWidget()
        self.table_view = CssTableView()
        self.table_model = QStandardItemModel()

        self.init_ui()

        self.searching = False
        # 查询控件
        self.control = None
        self.position = (0, 0)
        self.parents = []

    def init_ui(self):
        self.setLayout(self.out_layout)
        self.out_layout.setContentsMargins(0, 0, 0, 0)

        self.load_body_left_ui()
        self.load_body_right_ui()

        self.load_action()

    def load_body_left_ui(self):
        left_layout = QVBoxLayout()
        label = TitleLabel('控件信息 释放Ctrl定位聚焦窗口控件')

        left_layout.addWidget(label)
        left_layout.addWidget(self.tree_widget)
        left_layout.setSpacing(0)
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setColumnCount(1)

        self.out_layout.addLayout(left_layout)
        self.out_layout.setStretchFactor(left_layout, 5)

    def load_body_right_ui(self):
        right_layout = QVBoxLayout()
        # 设置列宽，第一列固定宽度，第二列自动填充
        self.table_model.setHorizontalHeaderLabels(['属性名', '属性值'])

        self.table_view.setModel(self.table_model)

        right_layout.addWidget(self.table_view)
        right_layout.setSpacing(0)

        self.out_layout.addLayout(right_layout)
        self.out_layout.setStretchFactor(right_layout, 5)

        self.table_view.setColumnWidth(0, 150)  # 设置第一列的宽度
        # 设置第二列自动填充
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

    def load_action(self):
        app_root.key_watch.release_signal.connect(self.action_out_result)
        self.tree_widget.itemSelectionChanged.connect(self.action_selection_changed)

    def action_selection_changed(self):
        self.flash_right_part_ui()

    def flash_right_part_ui(self):
        self.table_model.clear()
        self.table_model.setHorizontalHeaderLabels(['属性名', '属性值'])
        selected_item = self.tree_widget.currentItem()
        control = selected_item.get_custom_data()
        show_items = ["auto_id", "AutomationId", "Name", "ClassName", "ControlTypeName", "BoundingRectangle",
                      "LocalizedControlType"]
        for attr in show_items:
            try:
                item = [QStandardItem(str(field)) for field in [attr, getattr(control, attr)]]
            except Exception:
                item = [QStandardItem(field) for field in [attr, ""]]
            self.table_model.appendRow(item)

        self.table_view.setColumnWidth(0, 150)  # 设置第一列的宽度
        # 设置第二列自动填充
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

    def action_out_result(self, key):
        if self.parent().currentIndex() == self.index:
            if key.key == keyboard.Key.ctrl_l:
                if settings.RUN_ENV == 'Darwin':
                    settings.log.warning('mac不支持')
                    return
                self.action_flash_table()

    def action_flash_table(self):
        self.tree_widget.clear()
        self.parents = []

        pos = pyautogui.position()
        self.position = (pos.x, pos.y)
        self.out_result()
        self.load_parents(self.control)
        self.create_tree_item(self.tree_widget, len(self.parents) - 1)
        self.tree_widget.expandAll()
        self.tree_widget.resizeColumnToContents(0)  # 每次更新后调整列宽

    def create_tree_item(self, parent, level):
        if level >= 0:
            item = CustomTreeWidgetItem(text=f'{self.parents[level].LocalizedControlType}"{self.parents[level].Name}"',
                                        custom_data=self.parents[level], parent=parent)
            self.create_tree_item(item, level - 1)
            if level == 0:
                self.tree_widget.setCurrentItem(item)

    def load_parents(self, bottom=None):
        if bottom is not None:
            self.parents.append(bottom)
            child = bottom.GetParentControl()
            self.load_parents(child)

    def out_result(self):
        try:
            self.search()
            if self.control is not None:
                settings.log.success(f'找到:{self.control.LocalizedControlType}"{self.control.Name}"')
            else:
                settings.log.warning(f'未找到')
        except:
            print(f'{traceback.format_exc()}')
            settings.log.warning(f'异常控件')

    def search(self):
        self.control = None

        import uiautomation as auto
        with auto.UIAutomationInitializerInThread():
            # 获取当前活动窗口
            focus_window = auto.GetForegroundControl()
            self.traverse_controls(focus_window)

    def traverse_controls(self, control):
        if not control.Exists(0.1, 1):
            raise
        children = control.GetChildren()

        for child in children:
            # 最小尺寸匹配定位
            cur_rect = child.BoundingRectangle
            if cur_rect.left < self.position[0] < cur_rect.right and cur_rect.top < self.position[1] < cur_rect.bottom:
                if self.control is None:
                    self.control = child
                out_rect = self.control.BoundingRectangle
                if cur_rect.width() <= out_rect.width() and cur_rect.height() <= out_rect.height():
                    self.control = child
            self.traverse_controls(child)
