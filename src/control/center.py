import settings
import json
import traceback
from common.tools import log, JsonFile, File, watch
from src.utils.model import Function, SQLserver
from src.utils.errors import RunError
from library.element import Element


class ControlCenter:
    """
    steps 存储需要添加的 Function, 字典形式
    search_record 存储查询匹配到的 Function
    record_checked 存储选中的 Function index
    """
    search_record = []
    record_checked = None
    steps = []

    @staticmethod
    def func_search(depict_func):
        """
        搜索方法
        """
        ControlCenter.search_record = []
        session = SQLserver().get_db()
        funcs = session.query(Function).filter(Function.depict_func.like(f'%{depict_func}%')).all()
        for func in funcs:
            ControlCenter.search_record.append(func)

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
        func: Function = ControlCenter.search_record[ControlCenter.record_checked]
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
        log.info(f'<{func_step.get("depict_func", None)}> 已添加成功')

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
        log.info(f'<{define_step.get("name", "自定义方法")}> 已添加成功')

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
            log.info(f'<{func.get("depict_func", None)}>方法已被移除')
        elif f_type == 'define':
            log.info(f'<{func.get("name", None)}>方法已被移除')

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
        ele = Element()
        for f in ControlCenter.steps:
            f_type = f['type']
            if f_type == 'exist':
                try:
                    getattr(ele, f.get("func", None))(**json.loads(f.get("params", "{}")))
                    log.success(f'执行<{f.get("depict_func", None)}>完毕')
                except Exception as e:
                    log.warning(f'{traceback.format_exc()}')
                    log.error(f'执行<{f.get("depict_func", None)}>遇到问题:{e}')
                    break
            elif f_type == 'define':
                watch.replay_events(f.get("events"))
                log.success(f'执行<{f.get("name", None)}>完毕')

    @staticmethod
    def steps_save():
        """
        方法存储至process.json
        :return:
        """
        JsonFile(settings.PROCESS_PATH).write(ControlCenter.steps)
        log.success(f'流程文件保存至<{settings.PROCESS_PATH}>')

    @staticmethod
    def steps_read():
        """
        从process.json读取
        """
        ControlCenter.steps = JsonFile(settings.PROCESS_PATH).read()

    @staticmethod
    def generate_py():
        """
        将steps反向生成py
        :return:
        """
        header = """from library.element import Element
from common.tools import watch\n
ele = Element()\n\n
def case():\n"""
        content = ''

        index = 1

        for f in ControlCenter.steps:
            f_type = f.get("type", None)
            if f_type == 'exist':
                params = json.loads(f.get("params", "{}"))
                func = f.get("func", None)
                temp_params = [f'{key}="{params[key]}"' for key in params]
                content += f'    ele.{func}({", ".join(temp_params)})\n'
            elif f_type == 'define':
                content += f'    event_{index} = {f.get("events", None)}\n'
                content += f'    watch.replay_events(event_{index})\n'
                index += 1
            else:
                log.warning(f'暂不支持{f}方法')
                continue
        if len(ControlCenter.steps) == 0:
            content += '    pass\n'
        File(settings.CASE_PATH).write(header + content)
        log.success(f'py代码已保存于{settings.CASE_PATH}')
        return header + content

    @staticmethod
    def define_func_record():
        watch.start()
        return watch.events


if __name__ == '__main__':
    ControlCenter.func_search('值')
    ControlCenter.step_click(1)
    ControlCenter.func_step_insert()
    ControlCenter.define_step_insert()
    ControlCenter.func_step_insert()
    ControlCenter.step_click(0)
    ControlCenter.func_step_insert()
    ControlCenter.steps_exec()
    ControlCenter.steps_save()
    ControlCenter.generate_py()
