import json
import os
import re
import shutil
import traceback

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


class FuncUpdate:
    VERSIONS = 'versions.json'

    def __init__(self):
        self.versions = None

    def get_current_version(self):
        import importlib
        try:
            element_lib = importlib.import_module(f'library.operation')
        except ModuleNotFoundError:
            return 0.0
        return element_lib.version

    def get_net_versions(self):
        net_path = os.path.join(settings.Files.LIBRARY_ORIGIN, FuncUpdate.VERSIONS)
        if not os.path.exists(net_path):
            raise FileNotFoundError('路径不存在:{}'.format(net_path))
        with open(os.path.join(settings.Files.LIBRARY_ORIGIN, FuncUpdate.VERSIONS), 'r', encoding='utf-8') as f:
            self.versions = json.load(f)

    def clear_directory(self, directory):
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                settings.log.error(f'删除{file_path}出现错误:{e}')

    def update_library(self):
        file = f'{self.versions.get("zip")}{self.versions.get("now")}.zip'
        current_library = settings.Files.LIBRARY_DIR
        if not os.path.exists(current_library):
            os.makedirs(current_library)

        settings.log.info('清理当前方法库')
        self.clear_directory(current_library)
        settings.log.info('开始拉取最新方法库')
        shutil.unpack_archive(os.path.join(settings.Files.LIBRARY_ORIGIN, file), current_library)
        settings.log.success('方法库拉取完毕')

    def update_handler(self):
        try:
            self.get_net_versions()
            now = float(self.versions.get('now', 0.0))
            if now > self.get_current_version():
                self.update_library()
            else:
                settings.log.info('当前已是最新版本')
        except Exception as e:
            if settings.DEBUG:
                settings.log.debug(f'{traceback.format_exc()}')
            settings.log.warning(f'更新失败:{e}')


class ConfParse:

    @staticmethod
    def init_conf():
        SQLserver().delete_model(Confs)
        ConfParse.init_app_for_conf()
        ConfParse.init_definesight_for_conf()

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

        conf_download = Confs(keys='LIBRARY_ORIGIN', values=str(settings.Files.LIBRARY_ORIGIN), depict_key='方法库下载源',
                              conf_type=0)
        configs.append(conf_download)

        conf_library = Confs(keys='LIBRARY_PATH', values=str(settings.Files.LIBRARY_PATH), depict_key='方法库文件',
                             conf_type=0)
        configs.append(conf_library)

        SQLserver().insert(configs)

    @staticmethod
    def init_definesight_for_conf():
        configs = []

        class Config:
            SOFTWARE_PATH = ""
            APP_NAME = "App.exe"
            LOG_PATH = r"C:\Users\Public\Documents\Scanner\App\Log"
            CALIBRATE_FILE = ""
            MARKERS_FILE = ""
            DATA_FILE = ""
            LANG = "简体中文"

        try:
            import importlib
            conf_lib = importlib.import_module(f'library.conf')
            Config = getattr(conf_lib, 'Config')
        except Exception as e:
            settings.log.warning(f'library模块不存在采用默认加载: {e}')

        conf_soft_path = Confs(keys='SOFTWARE_PATH', values=str(Config.SOFTWARE_PATH), depict_key='软件目录',
                               conf_type=1)
        configs.append(conf_soft_path)

        conf_soft_name = Confs(keys='APP_NAME', values=str(Config.APP_NAME), depict_key='应用程序名字',
                               conf_type=1)
        configs.append(conf_soft_name)

        conf_soft_log = Confs(keys='LOG_PATH', values=str(Config.LOG_PATH), depict_key='软件日志目录',
                              conf_type=1)
        configs.append(conf_soft_log)

        conf_soft_cal = Confs(keys='CALIBRATE_FILE', values=str(Config.CALIBRATE_FILE), depict_key='校准数据目录',
                              conf_type=1)
        configs.append(conf_soft_cal)

        conf_soft_marker = Confs(keys='MARKERS_FILE', values=str(Config.MARKERS_FILE), depict_key='标记数据目录',
                                 conf_type=1)
        configs.append(conf_soft_marker)

        conf_soft_data = Confs(keys='DATA_FILE', values=str(Config.DATA_FILE), depict_key='激光数据目录',
                               conf_type=1)
        configs.append(conf_soft_data)

        conf_soft_lang = Confs(keys='LANG', values=str(Config.LANG), depict_key='语言环境',
                               conf_type=1)
        configs.append(conf_soft_lang)

        SQLserver().insert(configs)


def init_table():
    server = SQLserver()
    if not server.record_exist(Confs):
        ConfParse().init_conf()


if __name__ == '__main__':
    # ConfParse().init_conf()
    FuncUpdate().update_handler()
