import uiautomation as auto
from pynput import keyboard, mouse
import pyautogui
import traceback


class FindE:
    def __init__(self, search_root=None, filter_control=None):
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.index = 1

        self.serch_root = search_root if search_root is not None else []
        self.filter_control = filter_control if filter_control is not None else []

        self.exist_element = None
        self.position = (0, 0)

    def on_click(self, x, y, button, pressed):
        if pressed:
            if button == mouse.Button.left:
                press_type = '左键'
            else:
                press_type = '右键'

            self.position = (x, y)
            print(f'<{self.index}> {press_type}按下<{self.position}>')
            self.out_result()

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.mouse_listener.stop()
            self.keyboard_listener.stop()
            print('程序安全退出')
        elif key == keyboard.Key.ctrl_l:
            pos = pyautogui.position()
            self.position = (pos.x, pos.y)
            self.out_result()

    def out_result(self):
        try:
            self.search()
            if self.exist_element is not None:
                print(f'<{self.index}> {self.exist_element.Name} {self.exist_element.ClassName}')
            else:
                print(f'<{self.index}> 未找到')
        except:
            # print(f'{traceback.format_exc()}')
            print(f'<{self.index}> 异常控件')
        self.index += 1

    def start(self):
        print('开始')
        self.mouse_listener.start()
        self.keyboard_listener.start()
        self.mouse_listener.join()
        self.keyboard_listener.join()

    def search(self):
        self.exist_element = None
        with auto.UIAutomationInitializerInThread():
            # 从根搜
            # root = auto.GetRootControl()
            # require_root = ['App']

            # 获取当前活动窗口
            focus_window = auto.GetForegroundControl()
            require_root = ['App', 'FuncParamDialog']
            for r in require_root:
                # cur_root = root.WindowControl(ClassName=r, searchDepth=1)
                # self.traverse_controls(cur_root)
                if focus_window.ClassName != r:
                    continue
                self.traverse_controls(focus_window)

    def traverse_controls(self, control: auto.Control):
        if not control.Exists(0.1, 1):
            raise
        children = control.GetChildren()

        for child in children:
            # 此处过滤
            if child.ClassName in self.filter_control:
                continue

            # 最小尺寸匹配定位
            cur_rect = child.BoundingRectangle
            if cur_rect.left < self.position[0] < cur_rect.right and cur_rect.top < self.position[1] < cur_rect.bottom:
                if self.exist_element is None:
                    self.exist_element = child
                out_rect = self.exist_element.BoundingRectangle
                if cur_rect.width() < out_rect.width() and cur_rect.height() < out_rect.height():
                    self.exist_element = child
            self.traverse_controls(child)


f = FindE()
# print(root_element.Exists(0.1))
f.start()
