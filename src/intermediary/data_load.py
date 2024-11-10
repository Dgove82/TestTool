import json
import re

import settings
from settings import Function, Confs
from src.intermediary.center import SQLserver


class FuncModel:
    def __init__(self, func=None, params=None, depict_func=None, depict_params=None, depict_return=None):
        self.func = func
        self.params = params
        self.depict_func = depict_func
        self.depict_params = depict_params
        self.depict_return = depict_return

    def sysout(self):
        res = f"""func: {self.func}
params: {self.params}
depict_func: {self.depict_func}
depict_params: {self.depict_params}
depict_return: {self.depict_return}
"""
        print(res)

    def wrap_dict(self):
        return {'func': self.func, 'params': self.params, 'depict_func': self.depict_func,
                'depict_params': self.depict_params, 'depict_return': self.depict_return}


class FuncParse:
    PATTERN_FUNC = r'\sdef\s(?P<func>\w+)\((?P<params>.*)\):\s+["\']{3}\s*(?P<depict>[\s\S]*?)["\']{3}\s*'

    def __init__(self, file):
        self.file = file

    def load_file(self) -> str:
        with open(self.file, 'r', encoding='utf-8') as f:
            return f.read()

    def regex(self) -> dict:
        txt = self.load_file()
        matches = re.finditer(FuncParse.PATTERN_FUNC, txt)
        for m in matches:
            yield m.groupdict()

    def handler(self):
        """
        将值读取值数据库
        :return:
        """
        res = []

        for res_dict in self.regex():
            func = Function()
            func.func = res_dict.get('func', None)
            func.params = json.dumps(self.parse_params(res_dict.get('params', None)), ensure_ascii=False)
            depict = self.parse_depict(res_dict.get('depict', None))
            func.depict_func = depict[0]
            func.depict_params = json.dumps(depict[1], ensure_ascii=False)
            func.depict_return = depict[2]
            settings.log.info(f'方法<{func.depict_func if func.depict_func else func.func}>解析完成')
            res.append(func)

        server = SQLserver()
        server.delete_model(Function)
        server.insert(res)

    @staticmethod
    def parse_params(temp_param) -> dict:
        params = {}
        if temp_param is not None:
            param = temp_param.split(',')
            for val in param:
                real_val = val.strip()
                if real_val == 'self':
                    continue
                else:
                    valuth = real_val.split('=')
                    if len(valuth) > 1:
                        valuth[1] = valuth[1].strip('"').strip("'")
                        params.update({valuth[0]: valuth[1]})
                    else:
                        params.update({valuth[0]: None})
        # print(f'params: {params}')
        return params

    @staticmethod
    def parse_depict(temp_depict) -> tuple:
        depict_func = []
        depict_params = {}
        depict_return = []

        if temp_depict is not None:
            depicts = temp_depict.split('\n')
            for depict in depicts:
                real_depict = depict.strip()
                if real_depict.startswith(':param'):
                    res = re.findall(r':param\s(\w+):\s?(.*)', real_depict)
                    if len(res) > 0 and len(res[0]) > 1:
                        depict_params.update({res[0][0]: res[0][1]})
                    elif len(res) > 0 and len(res[0]) == 1:
                        depict_params.update({res[0]: res[0]})
                    else:
                        depict_params.update({'/': '/'})
                elif real_depict.startswith(':return'):
                    res = re.findall(r':return:\s?(.+)', real_depict)
                    if len(res) > 0:
                        depict_return.append(res[0])
                    else:
                        depict_return.append('/')
                else:
                    if re.findall(r'.+', real_depict):
                        depict_func.append(real_depict)

        depict_func = '\n'.join(depict_func)
        depict_return = '\n'.join(depict_return)

        # print(f'depict_func: {depict_func}')
        # print(f'depict_params: {depict_params}')
        # print(f'depict_return: {depict_return}')
        return depict_func, depict_params, depict_return


class ConfParse:

    @staticmethod
    def init_conf():
        SQLserver().delete_model(Confs)
        ConfParse.init_app_for_conf()

    @staticmethod
    def init_app_for_conf():
        configs = []
        conf_log = Confs(keys='LOG_DIR', values=str(settings.Files.LOG_DIR), depict_key='日志存放目录', conf_type=0)
        configs.append(conf_log)

        conf_image = Confs(keys='IMAGE_DIR', values=str(settings.Files.IMAGE_DIR), depict_key='图片存放目录',
                           conf_type=0)
        configs.append(conf_image)

        conf_video = Confs(keys='VIDEO_DIR', values=str(settings.Files.VIDEO_DIR), depict_key='视频存放目录',
                           conf_type=0)
        configs.append(conf_video)

        conf_process = Confs(keys='PROCESS_DIR', values=str(settings.Files.PROCESS_DIR), depict_key='用例流程目录',
                             conf_type=0)
        configs.append(conf_process)

        conf_case = Confs(keys='CASE_DIR', values=str(settings.Files.CASE_DIR), depict_key='用例脚本目录',
                          conf_type=0)
        configs.append(conf_case)

        conf_library = Confs(keys='LIBRARY_PATH', values=str(settings.Files.LIBRARY_PATH), depict_key='方法库文件',
                             conf_type=0)
        configs.append(conf_library)

        SQLserver().insert(configs)

    def init_definesight_for_conf(self):
        pass


def init_table():
    server = SQLserver()
    if not server.record_exist(Confs):
        ConfParse().init_conf()


if __name__ == '__main__':
    ConfParse().init_conf()
