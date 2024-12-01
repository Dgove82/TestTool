import time
import importlib
import settings
import json
import os
import traceback
from typing import Union
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete, and_
from common.tools import JsonFileTool, FileTool
from src.utils.errors import ExecError


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
    common_record = []
    common_checked = -1
    search_record = []
    record_checked = -1
    steps = []
    checked = -1
    # 执行次数
    count = 1
    # 从x步开始执行 - 非索引值
    exec_step_start = 1
    # 执行到x步 - 非索引值
    exec_step_end = 1
    # # 执行标志位 - 索引值
    exec_step = 0

    def __init__(self):
        self.sql_server = SQLserver()
        self.loop_index = 0

    def load_common_record(self):
        ControlCenter.common_record = []
        session = self.sql_server.get_db()
        funcs = (session.query(settings.Function)
                 .join(settings.UsageRate,
                       settings.Function.func == settings.UsageRate.func).filter(
            settings.UsageRate.is_top == 1).order_by(settings.UsageRate.use_count.desc())
                 .all())
        for func in funcs:
            ControlCenter.common_record.append(func)

        session.close()

    def insert_func_into_common(self):
        session = self.sql_server.get_db()
        if ControlCenter.record_checked != -1:
            f = ControlCenter.search_record[ControlCenter.record_checked]
            exist_func = session.query(settings.UsageRate).filter(settings.UsageRate.func == f.func).first()
            session.close()
            if exist_func:
                exist_func.is_top = 1
                self.update_instance(exist_func)
            else:
                new_func = settings.UsageRate(func=f.func, use_count=0, is_top=1)
                self.sql_server.insert(new_func)
            settings.log.info(f'已将<{f.depict_func}设为常用>')
        else:
            raise ExecError("常用设置异常")

    def cancel_func_into_common(self):
        if ControlCenter.common_checked != -1:
            session = self.sql_server.get_db()
            f = ControlCenter.common_record[ControlCenter.common_checked]
            exist_func = session.query(settings.UsageRate).filter(settings.UsageRate.func == f.func).first()
            session.close()
            exist_func.is_top = 0
            self.update_instance(exist_func)
            settings.log.info(f'已将<{f.depict_func}从常用中移除>')
        else:
            raise ExecError("取消常用设置异常")

    def add_func_use_count(self, t=1):
        session = self.sql_server.get_db()
        if t == 0:
            f = ControlCenter.common_record[ControlCenter.common_checked]
            exist_func = session.query(settings.UsageRate).filter(settings.UsageRate.func == f.func).first()
            session.close()
            exist_func.use_count += 1
            self.update_instance(exist_func)
        elif t == 1:
            f = ControlCenter.search_record[ControlCenter.record_checked]
            exist_func = session.query(settings.UsageRate).filter(settings.UsageRate.func == f.func).first()
            session.close()
            if exist_func:
                exist_func.use_count += 1
                self.update_instance(exist_func)
            else:
                new_func = settings.UsageRate(func=f.func, use_count=1, is_top=0)
                self.sql_server.insert(new_func)
        else:
            session.close()
            raise ExecError("添加使用次数设置异常")

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
        # funcs = session.query(settings.Function).filter(and_(*condition)).all()
        funcs = (session.query(settings.Function)
                 .join(settings.UsageRate, settings.Function.func == settings.UsageRate.func, isouter=True)
                 .filter(and_(*condition))
                 .order_by(settings.UsageRate.use_count.desc().nullslast())
                 .all())

        for func in funcs:
            ControlCenter.search_record.append(func)

        session.close()

    @staticmethod
    def common_step_click(record_index=0):
        """
        选中常用中的方法
        """
        if record_index > len(ControlCenter.common_record):
            raise ExecError("常用方法确定异常")
        else:
            ControlCenter.common_checked = record_index

    @staticmethod
    def step_click(record_index=0):
        """
        选中搜索结果中的方法
        """
        if record_index > len(ControlCenter.search_record):
            raise ExecError("搜索方法确定异常")
        else:
            ControlCenter.record_checked = record_index

    def func_step_insert(self, pos=None, kwargs: str = None):
        """
        新增存在方法步骤, 根据位置插入步骤,并配置参数
        """
        if ControlCenter.record_checked != -1:
            func: settings.Function = ControlCenter.search_record[ControlCenter.record_checked]
            t = "normal"
        elif ControlCenter.common_checked != -1:
            func: settings.Function = ControlCenter.common_record[ControlCenter.common_checked]
            t = "common"
        else:
            raise ExecError("搜索方法确定异常")
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
        if t == 'normal':
            self.add_func_use_count(1)
        elif t == 'common':
            self.add_func_use_count(0)

    @staticmethod
    def define_step_insert(events: list, pos: int = None, name: str = None):
        """
        define_step为json字符串
        {"type": "define", "name": 自定义昵称, "events": [{}, {}]}
        """
        define_step = {"type": "define", "name": "自定义方法" if name is None else name, "events": events}

        if pos is None or pos >= len(ControlCenter.steps):
            ControlCenter.steps.append(define_step)
        else:
            ControlCenter.steps.insert(pos, define_step)
        settings.log.info(f'录制方法<{define_step.get("name", "自定义方法")}> 已添加成功')

    @staticmethod
    def loop_step_insert(loop_steps: int, loop_count: int, pos: int = None, name: str = None):
        """
        define_step为json字符串
        {"type": "loop", "name": 自定义昵称, 'loop_steps': 1, 'loop_count': 1}
        """
        loop_step = {"type": "loop", "name": "自定义方法" if name is None else name, "loop_steps": loop_steps,
                     "loop_count": loop_count}
        if pos is None or pos >= len(ControlCenter.steps):
            ControlCenter.steps.append(loop_step)
        else:
            ControlCenter.steps.insert(pos, loop_step)
        settings.log.info(f'循环方法<{loop_step.get("name", "自定义方法")}> 已添加成功')

    @staticmethod
    def step_del(pos=None):
        """
        移除步骤，根据位置移除对应方法
        :param pos: 索引
        :return:
        """
        if pos is None or pos >= len(ControlCenter.steps) or len(ControlCenter.steps) <= 0:
            # func = ControlCenter.steps.pop()
            settings.log.warning(f'异常删除')
        else:
            func = ControlCenter.steps.pop(pos)
            f_type = func.get('type', None)
            if f_type == 'exist':
                settings.log.info(f'<{func.get("depict_func", None)}>方法已被移除')
            elif f_type == 'define':
                settings.log.info(f'<{func.get("name", None)}>方法已被移除')

    @staticmethod
    def step_update_order(f, t):
        """
        更改方法次序, 先插入后删除
        """
        if -1 < t < len(ControlCenter.steps):
            element_to_move = ControlCenter.steps.pop(f)
            ControlCenter.steps.insert(t, element_to_move)
            f_type = element_to_move.get('type', None)
            if f_type == 'exist':
                settings.log.info(f'将<{element_to_move.get("depict_func")}>从<{f + 1}>拖动至<{t + 1}>')
            elif f_type == 'define':
                settings.log.info(f'将<{element_to_move.get("name", None)}>从<{f + 1}>拖动至<{t + 1}>')
        else:
            settings.log.warning(f'异常移动')

    @staticmethod
    def step_reset():
        """
        步骤重置
        :return:
        """
        ControlCenter.steps = []

    def exec_exist_step(self, f):
        element_lib = importlib.import_module(f'library.operation')
        ele = getattr(element_lib, 'Element')()
        params = json.loads(f.get("params", "{}"))
        temp_params = {}
        for key in params:
            temp_params.update({key: params[key].replace("$i", str(self.loop_index))})

        getattr(ele, f.get("func", None))(**temp_params)
        settings.log.success(f'执行<{f.get("depict_func", None)}>完毕')

    @staticmethod
    def exec_define_step(f):
        settings.log.info(f'开始读取{f.get("name", None)}')
        settings.watch.replay_events(f.get("events"))
        settings.log.success(f'执行<{f.get("name", None)}>完毕')

    def exec_loop_step(self, f):
        """
        循环方法
        """
        mark_entrance = ControlCenter.exec_step + 1
        steps = f.get("loop_steps", None)
        count = f.get("loop_count", None)
        name = f.get("name", None)
        if len(ControlCenter.steps[mark_entrance: ControlCenter.exec_step_end]) < steps:
            raise ExecError('循环步骤范围错误')
        for i in range(count):
            self.loop_index = i
            if count > 1:
                settings.log.info(f'开始执行循环<{name}>第{i + 1}次')
            else:
                settings.log.info(f'开始执行循环<{name}>')

            ControlCenter.exec_step = mark_entrance
            limit = steps
            while limit > 0:
                f = ControlCenter.steps[ControlCenter.exec_step]
                f_type = f['type']
                if f_type == 'exist':
                    self.exec_exist_step(f)
                elif f_type == 'define':
                    self.exec_define_step(f)
                elif f_type == 'loop':
                    self.exec_loop_step(f)
                ControlCenter.exec_step += 1
                limit -= 1

            if count > 1:
                settings.log.success(f'执行循环<{name}>第{i + 1}次结束')
            else:
                settings.log.success(f'执行循环<{name}>结束')

        ControlCenter.exec_step -= 1
        self.loop_index = 0

    def steps_exec(self):
        """
        方法执行
        :return:
        """
        time.sleep(0.3)
        step_count = len(ControlCenter.steps)
        if (step_count == 0 or ControlCenter.exec_step_start > ControlCenter.exec_step_end or
                ControlCenter.exec_step_start > step_count or ControlCenter.exec_step_end > step_count):
            settings.log.warning(f'异常执行')
            return

        # 运行方法
        if settings.RUN_ENV == 'Windows':
            import uiautomation as auto
            with auto.UIAutomationInitializerInThread():
                self.steps_run()
        else:
            self.steps_run()
        settings.record.stop_record_video()
        settings.log.success('流程执行完毕')

    def steps_run(self):
        flag = True
        # 执行次数
        for i in range(ControlCenter.count):
            ControlCenter.exec_step = ControlCenter.exec_step_start - 1
            if not flag:
                settings.log.error('遇到异常，终止重复运行')
                break
            if ControlCenter.count > 1:
                settings.log.info(f'开始执行{i + 1}遍')

            while ControlCenter.exec_step < ControlCenter.exec_step_end:
                f = ControlCenter.steps[ControlCenter.exec_step]
                try:
                    f_type = f['type']
                    if f_type == 'exist':
                        self.exec_exist_step(f)
                    elif f_type == 'define':
                        self.exec_define_step(f)
                    elif f_type == 'loop':
                        self.exec_loop_step(f)
                    ControlCenter.exec_step += 1
                except Exception as e:
                    settings.log.debug(f'{traceback.format_exc()}')
                    settings.log.error(f'执行<{f.get("depict_func", "空步骤")}>遇到问题:{e}')
                    flag = False
                    break

            # for f in ControlCenter.steps[ControlCenter.exec_step_start - 1: ControlCenter.exec_step_end]:
            #     try:
            #         f_type = f['type']
            #         if f_type == 'exist':
            #             self.exec_exist_step(f)
            #         elif f_type == 'define':
            #             self.exec_define_step(f)
            #
            #     except Exception as e:
            #         settings.log.warning(f'{traceback.format_exc()}')
            #         settings.log.error(f'执行<{f.get("depict_func", None)}>遇到问题:{e}')
            #         flag = False
            #         break

            if ControlCenter.count > 1:
                settings.log.info(f'第{i + 1}遍执行完毕')

    @staticmethod
    def steps_save(f: int, t: int, file_path=os.path.join(settings.Files.PROCESS_DIR, "steps.json")):
        """
        方法存储至steps.json
        """
        try:
            steps = ControlCenter.steps[f - 1: t]
        except Exception:
            raise ExecError('导出步骤参数异常')
        JsonFileTool(file_path).write(steps)
        settings.log.success(f'流程文件保存至<{file_path}>')

    @staticmethod
    def steps_read(pos: int, file_path=os.path.join(settings.Files.PROCESS_DIR, "steps.json")):
        if pos - 1 > len(ControlCenter.steps):
            raise ExecError('插入位置超过预期位置')
        steps = JsonFileTool(file_path).read()
        ControlCenter.steps = ControlCenter.steps[:pos - 1] + steps + ControlCenter.steps[pos - 1:]
        settings.log.success(f'步骤已插入至流程中')

    @staticmethod
    def process_save(file_path=os.path.join(settings.Files.PROCESS_DIR, "process.json")):
        """
        方法存储至process.json
        :return:
        """
        JsonFileTool(file_path).write(ControlCenter.steps)
        settings.log.success(f'流程文件保存至<{file_path}>')

    @staticmethod
    def process_read(file_path=os.path.join(settings.Files.PROCESS_DIR, "process.json")):
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
        generation = GenerateScript(ControlCenter.steps)
        generation.generate_py(module_name)
        return generation.content

    @staticmethod
    def script_save(content, file_path=os.path.join(settings.Files.CASE_DIR, "test_case.py")):
        FileTool(file_path).write(content)
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


class GenerateScript:
    def __init__(self, steps):
        self.steps = steps
        self.record_count = 1
        self.loop_count = 1
        self.mark = 0
        self.content = ""

    def generate_py(self, module_name="Case"):
        """
        将steps反向生成py
        :return:
        """
        header = f"""from library.operation.element import Element
from library.conf import watch\n
e = Element()\n\n
class Test{module_name}:
    def test_{module_name.lower()}_1(self):\n"""
        content = ''

        while self.mark < len(self.steps):
            f = self.steps[self.mark]
            f_type = f.get("type", None)
            if f_type == 'exist':
                content += self.generate_exist_func(f)
            elif f_type == 'define':
                content += self.generate_define_func(f, self.record_count)
                self.record_count += 1
            elif f_type == 'loop':
                self.loop_count = 1
                content += self.generate_loop_func(f)
            else:
                settings.log.warning(f'暂不支持{f}方法')

            self.mark += 1

        if len(ControlCenter.steps) == 0:
            content += '        # 为什么要生成空用例？\n'
            content += '        pass\n'
        self.content = header + content

    def generate_exist_func(self, f):
        content = ""
        params = json.loads(f.get("params", "{}"))
        func = f.get("func", None)
        depict = f.get("depict_func", None)
        temp_params = []
        for key in params:
            if "$i" in params[key]:
                line = f'{key}=r"{params[key].replace("$i", "{}")}".format(i_{self.loop_count - 1})'
            else:
                line = f'{key}=r"{params[key]}"'
            temp_params.append(line)

        content += f'        # {depict}\n'
        content += f'        e.{func}({", ".join(temp_params)})\n'
        return content

    @staticmethod
    def generate_define_func(f, index):
        content = ""
        depict = f.get('name', None)
        content += f'        # 录制方法: {depict}\n'
        content += f'        event_{index} = {f.get("events", None)}\n'
        content += f'        watch.replay_events(event_{index})\n'
        return content

    def generate_loop_func(self, f):
        content = ""
        depict = f.get('name', None)
        steps = f.get('loop_steps', None)
        count = f.get('loop_count', None)
        content += f'        # 循环方法: {depict}\n'
        content += f'        for i_{self.loop_count} in range({count}):\n'
        self.loop_count += 1
        while steps > 0:
            self.mark += 1
            f = self.steps[self.mark]
            f_type = f.get("type", None)
            temp_content = ""
            if f_type == 'exist':
                temp_content = self.generate_exist_func(f)
            elif f_type == 'define':
                temp_content = self.generate_define_func(f, self.record_count)
                self.record_count += 1
            elif f_type == 'loop':
                temp_content = self.generate_loop_func(f)
            else:
                settings.log.warning(f'暂不支持{f}方法')
            content += "\n".join([f"    {line}" for line in temp_content.split('\n')])
            steps -= 1
        return content

    @staticmethod
    def script_save(content, file_path=os.path.join(settings.Files.CASE_DIR, "test_case.py")):
        FileTool(file_path).write(content)
        settings.log.success(f'py代码已保存于{file_path}')


handler = ControlCenter()

if __name__ == '__main__':
    pass
    print(handler.search_type_conf(0))
