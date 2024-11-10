import time
import importlib
import settings
import json
import os
import traceback
from typing import Union
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete, and_
from sqlalchemy.sql import exists
# import uiautomation as auto
from common.tools import JsonFileTool, FileTool


class SQLserver:
    SESSION = sessionmaker(autoflush=True, bind=settings.engine)

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
            settings.log.success(f'{model.__tablename__}数据表已清空')
        except Exception as err:
            session.rollback()
            settings.log.error(f"清空{model.__tablename__}表时发生错误: {err}")
        finally:
            # 关闭session
            session.close()

    def insert(self, data: Union[list, settings.Base]):
        session = self.get_db()
        try:
            if isinstance(data, list):
                session.add_all(data)
            elif isinstance(data, settings.Base):
                session.add(data)
            else:
                raise TypeError
            session.commit()
            # settings.log.success(f'数据记录插入成功')
        except Exception as err:
            session.rollback()
            settings.log.error(f'插入失败,原因:{err}')
        finally:
            session.close()

    def record_exist(self, model):
        session = self.get_db()
        flag = session.query(model).first()
        return True if flag is not None else False

class ControlCenter:
    """
    steps 存储需要添加的 Function, 字典形式
    search_record 存储查询匹配到的 Function
    record_checked 存储选中的 Function index
    """
    search_record = []
    record_checked = None
    steps = []
    checked = None
    # 执行次数
    count = 1
    # 执行步骤
    exec_step_start = 1
    exec_step_end = 1

    def __init__(self):
        self.sql_server = SQLserver()

    def func_search(self, depict_func):
        """
        搜索方法
        """
        ControlCenter.search_record = []
        session = self.sql_server.get_db()

        keywords = depict_func.split(' ')
        condition = []
        for key in keywords:
            condition.append(settings.Function.depict_func.like(f'%{key}%'))

        # funcs = session.query(Function).filter(Function.depict_func.like(f'%{depict_func}%')).all()
        funcs = session.query(settings.Function).filter(and_(*condition)).all()
        for func in funcs:
            ControlCenter.search_record.append(func)

        session.close()

    @staticmethod
    def step_click(record_index=0):
        """
        选中搜索结果中的方法
        """
        if record_index > len(ControlCenter.search_record):
            raise IndexError
        else:
            ControlCenter.record_checked = record_index

    @staticmethod
    def func_step_insert(pos=None, kwargs: str = None):
        """
        新增存在方法步骤, 根据位置插入步骤,并配置参数
        """
        func: settings.Function = ControlCenter.search_record[ControlCenter.record_checked]
        func_step = {
            "type": "exist",
            "func": func.func,
            "params": kwargs if kwargs is not None else func.params,
            "depict_func": func.depict_func,
            "depict_params": func.depict_params,
            "depict_return": func.depict_return,
        }

        if pos is None or pos >= len(ControlCenter.steps) or pos == -1:
            ControlCenter.steps.append(func_step)
        else:
            ControlCenter.steps.insert(pos, func_step)
        settings.log.info(f'<{func_step.get("depict_func", None)}> 已添加成功')

    @staticmethod
    def define_step_insert(events, pos=None, name=None):
        """
        define_step为json字符串
        {"type": "define", "name": 自定义昵称, "events": [{}, {}]}
        """
        # watch.start()
        #
        # events = watch.events

        # define_step = json.loads(define_step)
        define_step = {"type": "define", "name": "自定义方法" if name is None else name, "events": events}

        if pos is None or pos >= len(ControlCenter.steps):
            ControlCenter.steps.append(define_step)
        else:
            ControlCenter.steps.insert(pos, define_step)
        settings.log.info(f'<{define_step.get("name", "自定义方法")}> 已添加成功')

    @staticmethod
    def step_del(pos=None):
        """
        移除步骤，根据位置移除对应方法
        :param pos: 索引
        :return:
        """
        if pos is None or pos > len(ControlCenter.search_record):
            func = ControlCenter.steps.pop()
        else:
            func = ControlCenter.steps.pop(pos)
        f_type = func.get('type', None)
        if f_type == 'exist':
            settings.log.info(f'<{func.get("depict_func", None)}>方法已被移除')
        elif f_type == 'define':
            settings.log.info(f'<{func.get("name", None)}>方法已被移除')

    @staticmethod
    def step_reset():
        """
        步骤重置
        :return:
        """
        ControlCenter.steps = []

    @staticmethod
    def steps_exec():
        """
        方法执行
        :return:
        """
        time.sleep(0.3)
        if len(ControlCenter.steps) == 0 or ControlCenter.exec_step_start > ControlCenter.exec_step_end:
            settings.log.warning(f'没有执行内容')
            return
        # with auto.UIAutomationInitializerInThread():
        element_lib = importlib.import_module(f'library.operation.element')
        ele = getattr(element_lib, 'Element')()
        for i in range(ControlCenter.count):
            if ControlCenter.count > 1:
                settings.log.info(f'开始执行{i+1}遍')
            for f in ControlCenter.steps[ControlCenter.exec_step_start - 1: ControlCenter.exec_step_end]:
                f_type = f['type']
                if f_type == 'exist':
                    try:
                        getattr(ele, f.get("func", None))(**json.loads(f.get("params", "{}")))
                        settings.log.success(f'执行<{f.get("depict_func", None)}>完毕')
                    except Exception as e:
                        settings.log.warning(f'{traceback.format_exc()}')
                        settings.log.error(f'执行<{f.get("depict_func", None)}>遇到问题:{e}')
                        break
                elif f_type == 'define':
                    settings.log.info(f'开始读取{f.get("name", None)}')
                    settings.watch.replay_events(f.get("events"))
                    settings.log.success(f'执行<{f.get("name", None)}>完毕')
            if ControlCenter.count > 1:
                settings.log.info(f'第{i + 1}遍执行完毕')
        settings.log.success('流程执行完毕')

    @staticmethod
    def steps_save(file_path=os.path.join(settings.Files.PROCESS_DIR, "process.json")):
        """
        方法存储至process.json
        :return:
        """
        JsonFileTool(file_path).write(ControlCenter.steps)
        settings.log.success(f'流程文件保存至<{file_path}>')

    @staticmethod
    def steps_read(file_path=os.path.join(settings.Files.PROCESS_DIR, "process.json")):
        """
        从process.json读取
        """
        ControlCenter.steps = JsonFileTool(file_path).read()
        settings.log.success(f'已从<{file_path}>读取流程')

    @staticmethod
    def generate_py(module_name="Case"):
        """
        将steps反向生成py
        :return:
        """
        header = f"""from library.operation.element import Element\n\n
class Test{module_name}(Element):
    def test_{module_name.lower()}_1(self):\n"""
        content = ''

        index = 1

        for f in ControlCenter.steps:
            f_type = f.get("type", None)
            if f_type == 'exist':
                params = json.loads(f.get("params", "{}"))
                func = f.get("func", None)
                depict = f.get("depict_func", None)
                temp_params = [f'{key}="{params[key]}"' for key in params]
                content += f'        # {depict}\n'
                content += f'        self.{func}({", ".join(temp_params)})\n'
            elif f_type == 'define':
                depict = f.get('name', None)
                content += f'        # 录制方法: {depict}\n'
                content += f'        event_{index} = {f.get("events", None)}\n'
                content += f'        self.replay_events(event_{index})\n'
                index += 1
            else:
                settings.log.warning(f'暂不支持{f}方法')
                continue
        if len(ControlCenter.steps) == 0:
            content += '        # 为什么要生成空用例？\n'
            content += '        pass\n'
        return header + content

    @staticmethod
    def script_save(content, file_path=os.path.join(settings.Files.CASE_DIR, "case.py")):
        FileTool(file_path).write( content)
        settings.log.success(f'py代码已保存于{file_path}')


    def load_conf(self):
        db = self.sql_server.get_db()
        res = db.query(settings.Confs).all()
        db.close()
        return res

    def load_conf_to_dict(self):
        """
        获取Conf表所有数据
        :return:
        """
        confs = self.load_conf()
        conf = dict()
        for c in confs:
            conf.update({c.keys: c.to_dict(c)})
        return conf

    def search_type_conf(self, rank=0):
        db = self.sql_server.get_db()
        conf = db.query(settings.Confs).filter_by(conf_type=rank).all()
        db.close()
        return conf

    def update_instance(self, instance):
        db = self.sql_server.get_db()
        db.add(instance)
        db.commit()
        db.close()


handler = ControlCenter()

if __name__ == '__main__':
    pass
    print(handler.search_type_conf(0))
