from common.tools import Singleton


class AppRoot:
    """
    app 根控件
    """

    # app根
    root = None
    # 会话框
    dialog = None
    # 日志输出框
    ui_log = None


class FuncControl(Singleton):
    """
    公共控件存储
    """

    def __init__(self):
        # 根
        self.root = None
        # 系统参数配置按钮
        self.conf_btn = None
        # 方法搜索输入框
        self.search_line = None
        # 方法搜索按钮
        self.search_btn = None
        # 录制方法添加
        self.add_record_btn = None
        # 搜索结果展示列表
        self.search_result_list = None
        # 执行流程展示列表
        self.process_list = None
        # 执行流程按钮
        self.exec_btn = None
        # 重置流程按钮
        self.reset_btn = None
        # 读取流程按钮
        self.read_process_btn = None
        # 保存流程按钮
        self.save_process_btn = None
        # 生成py代码按钮
        self.generate_py_btn = None
        # 右键菜单
        self.right_menu = None
        # 临时会话窗口
        self.dialog = None
        # 执行线程
        self.run_task = None


control_func = FuncControl()
