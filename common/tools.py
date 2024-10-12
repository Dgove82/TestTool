import hashlib
import json
import os.path
import re
import time
import sys
import inspect
import pyautogui
from loguru import logger
from pynput import keyboard, mouse
from PIL import ImageDraw, Image

import settings


class WatchTool:
    def __init__(self, watch=False):
        self.__events = []
        self.mouse_listener = None
        self.keyboard_listener = None
        self.watch = watch

    @property
    def events(self):
        return self.__events
        # return json.dumps(self.__events)

    @staticmethod
    def add_label_in_image(image: Image, center_x, center_y, radius=10):
        color = 'red'
        thickness = 2
        draw = ImageDraw.Draw(image)
        draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius),
                     outline=color, width=thickness)
        draw.ellipse((center_x - 2, center_y - 2, center_x + 2, center_y + 2),
                     outline=color, width=4)

    def img_record(self, center_x: float = 0, center_y: float = 0, rectangle: int = 50, full: bool = True):
        center_x = int(center_x)
        center_y = int(center_y)
        if full:
            screenshot = pyautogui.screenshot()
            size = pyautogui.size()
            screenshot = screenshot.resize((size.width, size.height))
            self.add_label_in_image(screenshot, center_x, center_y)
        else:
            width, height = rectangle * 2, rectangle * 2
            left = center_x - width // 2
            top = center_y - height // 2
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            self.add_label_in_image(screenshot, rectangle, rectangle)

        file_name = ContentTool(screenshot.tobytes()).byte_decode_md5()

        # 将截图保存为图片文件
        screenshot.save(os.path.join(settings.IMAGE_DIR, f'{file_name}.png'))

    def append_event(self, event):
        self.__events.append({"run_time": time.time(), "event": event})

    def on_click(self, x, y, button, pressed):
        self.append_event(['click', button.name, pressed, x, y])
        if self.watch and pressed:
            log.info(f"按下<{x}, {y}>处")
            self.img_record(x, y)

    def on_move(self, x, y):
        self.append_event(['move', x, y])

    def on_scroll(self, x, y, dx, dy):
        self.append_event(['scroll', x, y, dx, dy])

    def on_press(self, key):
        self.append_event(['press', str(key)])

    def on_release(self, key):
        if key == keyboard.Key.esc:
            self.stop()
            log.info('录制结束')
        else:
            self.append_event(['release', str(key)])

    def stop(self):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def start(self):
        log.info('开始录制')
        self.mouse_listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move, on_scroll=self.on_scroll)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.mouse_listener.start()
        self.keyboard_listener.start()
        self.keyboard_listener.join()
        self.mouse_listener.join()

    def replay_events(self, events: list = None):
        if events is None:
            events = self.__events if self.__events is not None else []

        log.info('事件开始读取')

        mouse_controller = mouse.Controller()
        keyboard_controller = keyboard.Controller()
        last_time = None

        for e in events:
            timestamp = e['run_time']
            event = e['event']

            if last_time is not None:
                time.sleep(max(0, timestamp - last_time))
            last_time = timestamp

            event_type = event[0]

            if event_type == 'click':
                button = getattr(mouse.Button, event[1])
                if event[2]:  # 如果是按下
                    mouse_controller.press(button)
                else:  # 如果是释放
                    mouse_controller.release(button)
            elif event_type == 'move':
                mouse_controller.position = (event[1], event[2])
            elif event_type == 'scroll':
                mouse_controller.scroll(event[3], event[4])
            elif event_type == 'press':
                key = event[1].replace('\'', '')
                try:
                    sub_key = ''.join(key.split('.')[1:])
                    key_attr = getattr(keyboard.Key, sub_key)
                except AttributeError:
                    key_attr = key
                keyboard_controller.press(key_attr)
            elif event_type == 'release':
                key = event[1].replace('\'', '')
                try:
                    # 尝试将字符串转换为 keyboard.Key 的属性
                    sub_key = ''.join(key.split('.')[1:])
                    key_attr = getattr(keyboard.Key, sub_key)
                except AttributeError:
                    # 如果不是特殊按键，则直接使用字符串
                    key_attr = key
                keyboard_controller.release(key_attr)

        log.success('录制事件读取结束')


class ContentTool:
    def __init__(self, content):
        self.content = content

    def json_parse(self):
        """
        json字符串转python对象
        """
        try:
            res = json.loads(self.content)
        except json.decoder.JSONDecodeError:
            res = self.content
        return res

    def byte_decode_md5(self):
        """
        字节流转md5
        """
        return hashlib.md5(self.content).hexdigest()


class File:
    def __init__(self, path):
        self.path = str(path)
        self.dir = None
        self.name = None

    @staticmethod
    def check_path(path):
        if not os.path.exists(path):
            os.makedirs(path)

    def parse_path(self):
        eles = self.path.split('/')
        if re.match(r'.*?\.\w+', eles[-1]):
            self.name = eles[-1]
            self.dir = '/'.join(eles[:-1])
        else:
            self.dir = self.path

    def create_file(self):
        with open(self.path, 'w'):
            pass

    def exists(self):
        # try:
        self.parse_path()
        if os.path.exists(self.path):
            return True
        else:
            os.makedirs(self.dir, exist_ok=True)
            self.create_file()
            return True
        # except Exception as e:
        #     print(f'不存在，且遇到问题:{e}')
        #     return False

    def write(self, data):
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(data)


class JsonFile(File):
    def __init__(self, path):
        super().__init__(path)

    def create_file(self):
        with open(self.path, 'w') as f:
            json.dump({}, f)

    def read(self) -> dict:
        self.exists()
        with open(self.path, "r") as f:
            return json.load(f)

    def write(self, data):
        with open(self.path, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def update(self, data: dict):
        res = self.read()
        res.update(data)
        with open(self.path, "w", encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=2)


class TimeTool:
    @staticmethod
    def now():
        return time.localtime()

    @staticmethod
    def nowstamp():
        return int(time.time())

    @staticmethod
    def get_format_time():
        return time.strftime("%Y-%m-%d_%H:%M:%S", TimeTool.now())

    @staticmethod
    def get_format_day():
        return time.strftime("%Y-%m-%d", TimeTool.now())


class LogTool:
    def __init__(self, log_level="DEBUG", log_file='log.log'):
        self.log_level = log_level
        self.log_file = log_file
        self.logger = logger
        self.configure_logging()
        self.last_info = None

    def capture_msg(self, messgae):
        self.last_info = messgae.format()

    def configure_logging(self):
        # 配置日志格式和输出
        self.logger.remove()  # 清除默认的日志处理器
        color_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " \
                       "<cyan>{extra[prefix]}</cyan> | " \
                       "<level>{level}</level> | " \
                       "<level>{message}</level>"
        self.logger.add(
            sink=self.log_file,
            level=self.log_level,
            format=color_format,
            rotation="500 MB",  # 日志文件轮转，每个文件最大500MB
            retention="1 days",  # 保留最近10天的日志
            enqueue=True,  # 异步写入日志
            backtrace=True,  # 记录堆栈跟踪
            diagnose=True,  # 记录异常诊断信息
        )
        self.logger.add(sys.stdout, level=self.log_level, backtrace=True, format=color_format)
        self.logger.add(self.capture_msg, format=color_format)

    @staticmethod
    def prefix_info():
        frame = inspect.stack()[3]
        file_path = os.path.splitext(os.path.relpath(frame.filename, settings.BASE_PATH))[0]
        prefix = f"{file_path}{'.' + frame.function if frame.function != '<module>' else ''}:{frame.lineno} "
        return prefix

    def __log(self, level: str, msg: str):
        prefix = self.prefix_info()
        log_method = getattr(self.logger, level.lower())
        log_method(msg, prefix=prefix)
        return self.last_info

    def info(self, msg):
        return self.__log(level="INFO", msg=msg)

    def debug(self, msg):
        return self.__log(level="DEBUG", msg=msg)

    def warning(self, msg):
        return self.__log(level="WARNING", msg=msg)

    def error(self, msg):
        return self.__log(level="ERROR", msg=msg)

    def success(self, msg):
        return self.__log(level="SUCCESS", msg=msg)

    def critical(self, msg):
        return self.__log(level="CRITICAL", msg=msg)

    def exception(self, msg):
        return self.__log(level="EXCEPTION", msg=msg)


log = LogTool(log_file=f'{settings.LOG_DIR.joinpath(TimeTool.get_format_day())}.log')
watch = WatchTool()
if __name__ == '__main__':
    print(log.info(msg="Hello World"))
