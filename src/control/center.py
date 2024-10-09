import settings
import json
from common.tools import log, JsonFile, File
from src.utils.model import Function, SQLserver
from src.utils.errors import RunError
from library.element import Element


class ControlCenter:
    """
    steps 存储需要添加的 Function
    search_record 存储查询匹配到的 Function
    record_checked 存储选中的 Function index
    """
    search_record = []
    record_checked = None
    steps = []

    @staticmethod
    def func_search(depict_func):
        ControlCenter.search_record = []
        session = SQLserver().get_db()
        funcs = session.query(Function).filter(Function.depict_func.like(f'%{depict_func}%')).all()
        for func in funcs:
            ControlCenter.search_record.append(func)

    @staticmethod
    def step_click(record_index=0):
        if record_index > len(ControlCenter.search_record):
            raise IndexError
        else:
            ControlCenter.record_checked = record_index

    @staticmethod
    def step_add(pos=None, kwargs: dict = None):
        """
        新增步骤, 根据位置插入步骤,并配置参数
        """
        func: Function = ControlCenter.search_record[ControlCenter.record_checked]
        if kwargs is not None:
            func.params = kwargs
        if pos is None or pos >= len(ControlCenter.search_record):
            ControlCenter.steps.append(func)
        else:
            ControlCenter.steps.insert(pos, func)
        log.info(f'<{func.depict_func}>方法以添加成功')

    @staticmethod
    def step_del(pos=None):
        """
        移除步骤，根据位置移除对应方法
        :param pos: 索引
        :return:
        """
        if pos is None or pos > len(ControlCenter.search_record):
            func: Function = ControlCenter.steps.pop()
        else:
            func: Function = ControlCenter.steps.pop(pos)

        log.info(f'<{func.depict_func}>方法已被移除')

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
            try:
                getattr(ele, f.func)(**json.loads(f.params))
            except Exception as e:
                log.error(f'执行{f.depict_func}遇到问题:{e}')
                raise RunError(str(e))

    @staticmethod
    def steps_save():
        """
        方法存储至process.json
        :return:
        """
        steps = []
        for f in ControlCenter.steps:
            steps.append(f.to_dict())
        JsonFile(settings.PROCESS_PATH).write(steps)
        log.info('流程步骤缓存完毕')

    @staticmethod
    def generate_py():
        """
        将steps反向生成py
        :return:
        """
        header = """from library.element import Element\n
ele = Element()\n\n
def case():\n"""
        content = ''
        for f in ControlCenter.steps:
            params = json.loads(f.params)
            temp_params = [f'{key}="{params[key]}"' for key in params]
            content += f'    ele.{f.func}({", ".join(temp_params)})\n'
        File(settings.CASE_PATH).write(header + content)
        log.success('函数方法生成完毕')
        return header + content


if __name__ == '__main__':
    ControlCenter.func_search('值')
    ControlCenter.step_click(1)
    ControlCenter.step_add()
    ControlCenter.step_add()
    ControlCenter.step_click(0)
    ControlCenter.step_add()
    ControlCenter.steps_exec()
    ControlCenter.steps_save()
    ControlCenter.generate_py()


