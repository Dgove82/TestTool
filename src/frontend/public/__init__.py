from common.tools import Singleton
import settings


class AppRoot(Singleton):
    """
    app 根控件
    """

    def __init__(self):
        # app根
        self.root = None
        # 菜单栏
        # 设置
        self.conf_act = None
        # 更新日志
        self.update_info_act = None
        # 会话框
        self.__dialog = None
        # 日志输出框 线程
        self.__ui_log = None
        # 键鼠监控 线程
        self.key_watch = None
        # 键鼠子任务添加标识1
        self.key_watch_task_insert = False
        self.key_watch_task_start = False

    @property
    def ui_log(self):
        if self.__ui_log is None:
            return settings.log
        return self.__ui_log

    @ui_log.setter
    def ui_log(self, value):
        self.__ui_log = value

    @property
    def dialog(self):
        return self.__dialog

    @dialog.setter
    def dialog(self, value):
        if value is None:
            self.__dialog = value
            return
        if self.__dialog is not None:
            raise
        self.__dialog = value


class FuncControl(Singleton):
    """
    公共控件存储
    """

    def __init__(self):
        # 根
        self.root = None
        # 方法搜索输入框
        self.search_line = None
        # 方法搜索按钮
        self.search_btn = None
        # 录制方法添加
        self.add_record_btn = None
        # 特殊方法添加
        self.add_special_func_btn = None
        # 常用方法栏
        self.common_result_list = None
        # 搜索结果展示列表
        self.search_result_list = None
        # 预览窗口
        self.pre_read_view = None
        # 箭头添加
        self.arrow_btn = None
        # 执行流程展示列表
        self.process_list = None
        # 执行流程按钮
        self.exec_btn = None
        # 步骤操作项
        self.step_btn = None
        # 流程操作项
        self.process_btn = None
        # 加载方法库按钮
        self.data_load_btn = None
        # 生成py代码按钮
        self.generate_py_btn = None
        # 右键菜单
        self.right_menu = None
        # 临时会话窗口
        self.dialog = None

        # actions
        self.actions = None


app_root = AppRoot()
control_func = FuncControl()
