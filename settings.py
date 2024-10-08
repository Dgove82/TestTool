from pathlib import Path
import os
import sys

if getattr(sys, 'frozen', False):
    # 如果是打包的可执行文件
    BASE_PATH = Path(os.path.dirname(sys.executable))
else:
    BASE_PATH = Path(__file__).resolve(strict=True).parent

FILES_PATH = BASE_PATH.joinpath('files')

if not os.path.exists(FILES_PATH):
    os.mkdir(FILES_PATH)

DB_PATH = FILES_PATH.joinpath('tool.db')

LOG_DIR = FILES_PATH.joinpath('logs')

IMAGE_DIR = FILES_PATH.joinpath('images')

EVENTS_PATH = FILES_PATH.joinpath('events.log')

PROCESS_PATH = FILES_PATH.joinpath('process.json')

CASE_PATH = FILES_PATH.joinpath('case.py')

