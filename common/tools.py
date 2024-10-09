import json
import os.path
import re
import time
import sys
import inspect
from loguru import logger

import settings


class File:
    def __init__(self, path):
        self.path = str(path)
        self.dir = None
        self.name = None

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

if __name__ == '__main__':
    print(log.info(msg="Hello World"))