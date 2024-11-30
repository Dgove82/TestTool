import shutil
from pathlib import Path
import os
import sys
import platform
from common.tools import FileTool, LogTool, TimeTool, RecordTool, WatchTool
import atexit
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String

DEBUG = True

if getattr(sys, 'frozen', False):
    # 如果是打包的可执行文件
    BASE_PATH = Path(os.path.dirname(sys.executable))
else:
    BASE_PATH = Path(__file__).resolve(strict=True).parent

# 依赖程序目录
RUN_ENV = platform.system()
DEPS_PROGRAM = BASE_PATH.joinpath('deps')

# FFMPEG, 不考虑linux及其他系统
TOOL_FFMPEG = None
if RUN_ENV == 'Windows':
    TOOL_FFMPEG = BASE_PATH.joinpath('deps/win/ffmpeg.exe')
elif RUN_ENV == 'Darwin':
    TOOL_FFMPEG = BASE_PATH.joinpath('deps/mac/ffmpeg')


class Files:
    # 文件存放目录
    FILES_PATH = BASE_PATH.joinpath('files')

    # sqlite数据库文件
    DB_PATH = FILES_PATH.joinpath('tool.db')

    # 执行日志记录目录
    LOG_DIR = FILES_PATH.joinpath('logs')

    # 存图目录
    IMAGE_DIR = FILES_PATH.joinpath('images')

    # 存视频目录
    VIDEO_DIR = FILES_PATH.joinpath('videos')

    # 录制事件记录
    EVENTS_PATH = FILES_PATH.joinpath('events.log')

    # 记录流程
    PROCESS_DIR = FILES_PATH.joinpath('process')

    # 方法库目录
    LIBRARY_DIR = os.path.join(BASE_PATH, 'library')

    # 生成的py文件
    CASE_DIR = BASE_PATH.joinpath('library').joinpath('case')

    # 方法库
    LIBRARY_PATH = os.path.join(BASE_PATH, 'library/operation/element.py')


FileTool.check_path(Files.FILES_PATH)
FileTool.check_path(Files.LOG_DIR)
FileTool.check_path(Files.IMAGE_DIR)
FileTool.check_path(Files.VIDEO_DIR)
FileTool.check_path(Files.PROCESS_DIR)
FileTool.check_path(Files.CASE_DIR)

LOG_FILE = f'{os.path.join(Files.LOG_DIR, TimeTool.get_format_day())}.log'


class Log(LogTool):
    def __init__(self, log_level="DEBUG", log_file=LOG_FILE, project_root=BASE_PATH, is_debug=DEBUG):
        super().__init__(log_level, log_file, project_root, is_debug)


# 实例化工具
log = Log()
record = RecordTool(TOOL_FFMPEG)
watch = WatchTool()

# 创建基类
Base = declarative_base()


class ModelBase(Base):
    __abstract__ = True

    @classmethod
    def to_dict(cls, instance):
        return {c: getattr(instance, c) for c in cls.__table__.columns.keys()}


# 定义模型
class Function(ModelBase):
    __tablename__ = 'functions'

    id = Column(Integer, primary_key=True)
    func = Column(String)
    params = Column(String)
    depict_func = Column(String)
    depict_params = Column(String)
    depict_return = Column(String)


class UsageRate(ModelBase):
    __tablename__ = 'usage_rate'

    id = Column(Integer, primary_key=True)
    func = Column(String, index=True)
    use_count = Column(Integer)
    is_top = Column(Integer)


class Record(ModelBase):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True)
    event = Column(String)
    image_name = Column(String)
    record_time = Column(String)


class Confs(ModelBase):
    __tablename__ = 'confs'

    id = Column(Integer, primary_key=True)
    keys = Column(String, index=True)
    values = Column(String)
    depict_key = Column(String)
    conf_type = Column(Integer)


# 创建 SQLite 数据库引擎
engine = create_engine(f'sqlite:///{Files.DB_PATH}')

if not os.path.exists(Files.DB_PATH):
    log.warning(f'数据库不存在，开始创建数据库')
    try:
        # 创建所有表
        Base.metadata.create_all(engine)
    except Exception as e:
        log.warning(f'特性双启,{e}')
    finally:
        log.success(f'数据库初始化完毕 ==> {Files.DB_PATH}')

Session = sessionmaker(bind=engine)
session = Session()

try:
    # 查询 Confs 表的所有记录
    settings_conf = session.query(Confs).filter_by(conf_type=0).all()
    for conf in settings_conf:
        setattr(Files, str(conf.keys), conf.values)


except Exception as e:
    log.warning(f"查询数据库时发生错误: {e}")
finally:
    # 关闭会话
    session.close()

# 注册结束事件
atexit.register(record.stop_record_video)
