import hashlib
import json
import os.path
import re
import subprocess
import time
import sys
import inspect
import platform
import pyautogui
from loguru import logger
from pynput import keyboard, mouse
from PIL import ImageDraw, Image
from src.utils.errors import FileExistError

pyautogui.FAILSAFE = False


class Singleton:
    """
    仅允许单次实例化
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class RecordTool(Singleton):
    def __init__(self, record_exe=None):
        # 录制视频工具
        self.record_exe: str = record_exe

        # 视频录制进程
        self.ffmpeg = None

    @property
    def is_recording(self):
        if self.ffmpeg is None:
            return False
        return self.ffmpeg.poll() is None

    def start_record_video(self, save_path: str, video_name='temp.mp4', timeout: int = None):
        if not os.path.exists(self.record_exe) or self.record_exe is None:
            raise FileExistError(f'缺少依赖程序:<{self.record_exe}> 不存在>')

        env = platform.system()
        cmd = None
        if env == 'Darwin':
            cmd = [
                str(self.record_exe),
                '-y',  # 直接覆盖保存
                '-f', 'avfoundation',
                '-i', '1',  # 请确保这是正确的设备索引
                '-r', '20',
            ]
        elif env == 'Windows':
            cmd = [
                str(self.record_exe),
                '-y',  # 直接覆盖保存
                '-f', 'gdigrab',
                '-i', 'desktop',  # 请确保这是正确的设备索引
                '-b:v', '500k',
                '-vcodec', 'mpeg4',
                '-r', '20',
                '-preset', 'veryfast'
            ]

        if timeout is not None:
            cmd.extend(['-t', str(timeout)])

        cmd.append(str(os.path.join(save_path, video_name)))

        self.ffmpeg = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop_record_video(self):
        if self.is_recording:
            self.ffmpeg.stdin.write(b'q')
            self.ffmpeg.stdin.flush()
            self.ffmpeg.communicate()
            self.ffmpeg = None
        else:
            if self.ffmpeg is not None:
                stdout, stderr = self.ffmpeg.communicate()
                self.ffmpeg = None
                raise ValueError(f'{stdout.decode(), stderr.decode()}')

    @staticmethod
    def add_label_in_image(image: Image, center_x, center_y, radius=10):
        color = 'red'
        thickness = 2
        draw = ImageDraw.Draw(image)
        draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius),
                     outline=color, width=thickness)
        draw.ellipse((center_x - 2, center_y - 2, center_x + 2, center_y + 2),
                     outline=color, width=4)

    def img_record(self, save_path: str, save_name: str, rectangle: int = 50, full: bool = False):
        mouse_position = pyautogui.position()
        center_x = int(mouse_position.x)
        center_y = int(mouse_position.y)
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

        # file_name = ContentTool(screenshot.tobytes()).byte_decode_md5()

        # 将截图保存为图片文件
        screenshot.save(os.path.join(save_path, f'{save_name}.png'))


class WatchTool:
    def __init__(self, monitor=False):
        self.mouse_listener = None
        self.keyboard_listener = None

        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()

        # 是否监听鼠标点击事件
        self.monitor: bool = monitor

        # 事件录制
        self.__events = []

    @property
    def events(self):
        return self.__events
        # return json.dumps(self.__events)

    def events_clear(self):
        self.__events = []

    @property
    def is_listening(self):
        """
        判断是否处理监听中
        :return:
        """
        return self.mouse_listener.is_alive()

    def append_event(self, event):
        self.__events.append({"run_time": time.time(), "event": event})

    def on_click(self, x, y, button, pressed):
        self.append_event(['click', button.name, pressed, x, y])
        if self.monitor and pressed:
            print(f"按下<{x}, {y}>处")
            RecordTool().img_record(save_path='./', save_name=f'{time.time()}.mp4')

    def on_move(self, x, y):
        self.append_event(['move', x, y])

    def on_scroll(self, x, y, dx, dy):
        self.append_event(['scroll', x, y, dx, dy])

    def on_press(self, key):
        if self.is_listening:
            self.append_event(['press', str(key)])

    def on_release(self, key):
        if key == keyboard.Key.down and not self.is_listening:
            self.mouse_listener.start()
        elif key == keyboard.Key.esc:
            self.stop()
        else:
            self.append_event(['release', str(key)])

    def stop(self):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def start(self):
        self.mouse_listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move, on_scroll=self.on_scroll)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        print('按下 ⬇ 键开始录制')
        self.keyboard_listener.start()
        self.keyboard_listener.join()
        self.mouse_listener.join()

    def replay_events(self, events: list = None):
        if events is None:
            events = self.__events if self.__events is not None else []

        print('事件开始读取')

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
                    self.mouse_controller.press(button)
                else:  # 如果是释放
                    self.mouse_controller.release(button)
            elif event_type == 'move':
                self.mouse_controller.position = (event[1], event[2])
            elif event_type == 'scroll':
                self.mouse_controller.scroll(event[3], event[4])
            elif event_type == 'press':
                key = event[1].replace('\'', '')
                try:
                    sub_key = ''.join(key.split('.')[1:])
                    key_attr = getattr(keyboard.Key, sub_key)
                except AttributeError:
                    key_attr = key
                self.keyboard_controller.press(key_attr)
            elif event_type == 'release':
                key = event[1].replace('\'', '')
                try:
                    # 尝试将字符串转换为 keyboard.Key 的属性
                    sub_key = ''.join(key.split('.')[1:])
                    key_attr = getattr(keyboard.Key, sub_key)
                except AttributeError:
                    # 如果不是特殊按键，则直接使用字符串
                    key_attr = key
                self.keyboard_controller.release(key_attr)

        print('录制事件读取结束')


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


class FileTool:
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

    def is_exists(self):
        return os.path.exists(self.path)

    def exists(self):
        """
        确保文件/目录存在
        :return:
        """
        self.parse_path()
        if os.path.exists(self.path):
            return True
        else:
            os.makedirs(self.dir, exist_ok=True)
            self.create_file()
            return True

    def write(self, data):
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(data)


class JsonFileTool(FileTool):
    def __init__(self, path):
        super().__init__(path)

    def create_file(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump({}, f)

    def read(self) -> dict:
        self.exists()
        with open(self.path, "r", encoding='utf-8') as f:
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
    def __init__(self, log_level="DEBUG", log_file="temp.log", project_root='', is_debug=False):
        self.log_level = log_level
        self.log_file = log_file
        self.is_debug = is_debug
        # 项目根目录
        self.project_root = project_root
        self.logger = logger
        self.configure_logging()
        self.last_info = None

    def capture_msg(self, message):
        self.last_info = message.format()

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

    def prefix_info(self):
        frame = inspect.stack()[3]
        file_path = os.path.splitext(os.path.relpath(frame.filename, self.project_root))[0]
        prefix = f"{file_path}{'.' + frame.function if frame.function != '<module>' else ''}:{frame.lineno} "
        return prefix

    def msg_struct(self, level: str, msg: str):
        prefix = self.prefix_info()
        msg = msg.replace('{', '【').replace('}', '】')
        log_method = getattr(self.logger, level.lower())
        log_method(msg, prefix=prefix)
        return self.last_info

    def info(self, msg):
        return self.msg_struct(level="INFO", msg=msg)

    def debug(self, msg):
        return self.msg_struct(level="DEBUG", msg=msg)

    def warning(self, msg):
        return self.msg_struct(level="WARNING", msg=msg)

    def error(self, msg):
        return self.msg_struct(level="ERROR", msg=msg)

    def success(self, msg):
        return self.msg_struct(level="SUCCESS", msg=msg)

    def critical(self, msg):
        return self.msg_struct(level="CRITICAL", msg=msg)

    def exception(self, msg):
        return self.msg_struct(level="EXCEPTION", msg=msg)


if __name__ == '__main__':
    pass
