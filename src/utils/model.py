import os.path
from typing import Union
from sqlalchemy import create_engine, Column, Integer, String, delete
from sqlalchemy.orm import sessionmaker, declarative_base
import settings
from common.tools import log

# 创建基类
Base = declarative_base()


class ModelBase(Base):
    __abstract__ = True

    @classmethod
    def to_dict(cls, instance):
        return {c.name: getattr(instance, c.name) for c in cls.__table__.columns}


# 定义模型
class Function(ModelBase):
    __tablename__ = 'functions'

    id = Column(Integer, primary_key=True)
    func = Column(String)
    params = Column(String)
    depict_func = Column(String)
    depict_params = Column(String)
    depict_return = Column(String)


class Hotkey(ModelBase):
    __tablename__ = 'hotkeys'
    id = Column(Integer, primary_key=True)
    hotkeys = Column(String)
    depict_hotkeys = Column(String)
    index_func = Column(String)
    index_params = Column(String)


class Record(ModelBase):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True)
    event = Column(String)
    image_name = Column(String)
    record_time = Column(String)


class Confs(ModelBase):
    __tablename__ = 'confs'

    id = Column(Integer, primary_key=True)
    keys = Column(String)
    values = Column(String)
    depict_key = Column(String)
    required = Column(Integer)


# 创建 SQLite 数据库引擎
engine = create_engine(f'sqlite:///{settings.DB_PATH}')

if not os.path.exists(settings.DB_PATH):
    log.warning(f'数据库不存在，开始创建数据库')
    try:
        # 创建所有表
        Base.metadata.create_all(engine)
    except Exception as e:
        log.warning('特性双启')
    finally:
        log.success(f'数据库初始化完毕 ==> {settings.DB_PATH}')


class SQLserver:
    SESSION = sessionmaker(autoflush=True, bind=engine)

    @staticmethod
    def load_conf():
        """
        获取Conf表所有数据
        :return:
        """
        db = SQLserver().get_db()
        confs = db.query(Confs).all()
        conf = dict()
        for c in confs:
            conf.update({c.keys: c.to_dict(c)})
        return conf

    @staticmethod
    def get_session():
        session = SQLserver.SESSION()
        try:
            yield session
        finally:
            session.close()

    def get_db(self):
        return next(self.get_session())

    def delete_model(self, model):
        """
        清空数据表
        :param model:
        :return:
        """
        delete_statement = delete(model)
        session = self.get_db()
        try:
            session.execute(delete_statement)
            session.commit()
            log.success(f'{model.__tablename__}数据表已清空')
        except Exception as err:
            session.rollback()
            log.error(f"清空{model.__tablename__}表时发生错误: {err}")
        finally:
            # 关闭session
            session.close()

    def insert(self, data: Union[list, Base]):
        session = self.get_db()
        try:
            if isinstance(data, list):
                session.add_all(data)
            elif isinstance(data, Base):
                session.add(data)
            else:
                raise TypeError
            session.commit()
            log.success(f'数据记录插入成功')
        except Exception as err:
            session.rollback()
            log.error(f'插入失败,原因:{err}')
        finally:
            session.close()
