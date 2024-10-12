from pathlib import Path
import os
import sys

if getattr(sys, 'frozen', False):
    # 如果是打包的可执行文件
    BASE_PATH = Path(os.path.dirname(sys.executable))
else:
    BASE_PATH = Path(__file__).resolve(strict=True).parent

# 文件存放目录
FILES_PATH = BASE_PATH.joinpath('files')

if not os.path.exists(FILES_PATH):
    os.mkdir(FILES_PATH)

# sqlite数据库文件
DB_PATH = FILES_PATH.joinpath('tool.db')

# 执行日志记录目录
LOG_DIR = FILES_PATH.joinpath('logs')

if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

# 存图目录
IMAGE_DIR = FILES_PATH.joinpath('images')

if not os.path.exists(IMAGE_DIR):
    os.mkdir(IMAGE_DIR)

# 录制事件记录
EVENTS_PATH = FILES_PATH.joinpath('events.log')

# 记录流程
PROCESS_PATH = FILES_PATH.joinpath('process.json')

# 生成的py文件
CASE_PATH = FILES_PATH.joinpath('case.py')

# 控件相关操作文件目录
LIBRARY_PATH = BASE_PATH.joinpath('library')

# 需要收录方法至数据库的方法库文件
LIB_ELEMENT = LIBRARY_PATH.joinpath('element.py')
