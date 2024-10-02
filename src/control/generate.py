import json
import re
import settings
from src.utils.model import SQLserver, Function
from src.utils.tools import JsonFile, log

LIBRARY_PATH = settings.BASE_PATH.joinpath('library')
LIB_ELEMENT = LIBRARY_PATH.joinpath('element.py')


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
        with open(self.file, 'r') as f:
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
        server = SQLserver()
        server.delete_model(Function)

        db = server.get_db()

        for res_dict in self.regex():
            log.info(f'方法{res_dict.items()}')
            func = Function()
            func.func = res_dict.get('func', None)
            func.params = json.dumps(self.parse_params(res_dict.get('params', None)), ensure_ascii=False)
            depict = self.parse_depict(res_dict.get('depict', None))
            func.depict_func = depict[0]
            func.depict_params = json.dumps(depict[1], ensure_ascii=False)
            func.depict_return = depict[2]

            res.append(func)
        try:
            db.add_all(res)
            db.commit()
            log.success(f'{Function.__tablename__}数据初始化完毕')
        except Exception as e:
            db.rollback()
            log.error(f'{Function.__tablename__}初始化异常: {e}')

    def hanlder_test(self):
        """
        json数据调试
        :return:
        """
        res = []

        for res_dict in self.regex():
            func = FuncModel()
            func.func = res_dict.get('func', None)
            func.params = self.parse_params(res_dict.get('params', None))
            func.depict_func, func.depict_params, func.depict_return = self.parse_depict(res_dict.get('depict', None))

            func.sysout()
            res.append(func.wrap_dict())

        JsonFile(settings.FILES_PATH.joinpath('temps.json')).write(res)

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


def handle():
    pass


if __name__ == '__main__':
    # log.info(f'{"a"}?')
    FuncParse(LIB_ELEMENT).handler()
