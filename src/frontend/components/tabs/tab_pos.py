from PyQt5.QtWidgets import *
from pynput import keyboard
import pyautogui
from src.frontend.public import app_root
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

        self.tree = QTreeWidget()

        self.init_ui()

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
        left_layout.addWidget(self.tree)
        self.tree.setHeaderHidden(True)
        self.tree.setColumnCount(1)

        self.out_layout.addLayout(left_layout)
        self.out_layout.setStretchFactor(left_layout, 5)

    def load_body_right_ui(self):
        right_layout = QVBoxLayout()

        self.out_layout.addLayout(right_layout)
        self.out_layout.setStretchFactor(right_layout, 5)

    def load_action(self):
        app_root.key_watch.press_signal.connect(self.action_out_result)
        self.tree.itemSelectionChanged.connect(self.action_selection_changed)

    def action_selection_changed(self):
        selected_item = self.tree.currentItem()
        settings.log.info(f'{selected_item.get_custom_data()}')

    def action_out_result(self, key):
        if self.parent().currentIndex() == self.index:
            if key.key == keyboard.Key.ctrl_l:
                self.tree.clear()
                pos = pyautogui.position()
                self.position = (pos.x, pos.y)
                self.out_result()
                self.load_parents(self.control)
                self.create_tree_item(self.tree, len(self.parents) - 1)
                self.tree.expandAll()
                self.tree.resizeColumnToContents(0)  # 每次更新后调整列宽

    def create_tree_item(self, parent, level):
        if level >= 0:
            item = CustomTreeWidgetItem(text=f'{self.parents[level].LocalizedControlType}',
                                        custom_data=self.parents[level], parent=parent)
            self.create_tree_item(item, level - 1)
        else:
            item = CustomTreeWidgetItem(text=f'{self.control.LocalizedControlType}', custom_data=self.control,
                                        parent=parent)

    def load_parents(self, bottom=None):

        if bottom is not None:
            self.parents.append(bottom)
            child = bottom.GetParentControl()
            self.load_parents(child)

    def out_result(self):
        try:
            self.search()
            if self.control is not None:
                settings.log.success(f'{self.control.Name} {self.control.ClassName}')
            else:
                settings.log.warning(f'未找到')
        except:
            print(f'{traceback.format_exc()}')
            settings.log.warning(f'异常控件')

    def search(self):
        self.control = None

        try:
            import uiautomation as auto
            with auto.UIAutomationInitializerInThread():
                # 获取当前活动窗口
                focus_window = auto.GetForegroundControl()
                self.traverse_controls(focus_window)
        except:
            settings.log.warning('mac 不支持')

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
                if cur_rect.width() < out_rect.width() and cur_rect.height() < out_rect.height():
                    self.control = child
            self.traverse_controls(child)
