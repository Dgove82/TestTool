import json
import re
import traceback

import settings
from src.frontend.public import control_func, app_root
from common.tools import Singleton
from src.intermediary.center import ControlCenter, handler
from src.frontend.components import (ExecDialog, FuncParamDialog, DefineParamDialog, LoopParamDialog,
                                     EditParamDialog, LoadDialog, GeneratePyDialog, DialogTip, StepExportDialog,
                                     StepImportDialog)
from PyQt5.QtWidgets import *


class FuncAction(Singleton):
    def __init__(self):
        self.app = app_root
        self.control = control_func

    def load_action(self):
        self.control.common_result_list.itemSelectionChanged.connect(self.action_common_step_selected)
        self.control.common_result_list.itemDoubleClicked.connect(self.action_step_add)
        self.control.common_result_list.customContextMenuRequested.connect(self.action_open_common_menu)

        self.control.search_result_list.itemDoubleClicked.connect(self.action_step_add)
        self.control.search_result_list.itemSelectionChanged.connect(self.action_step_selected)
        self.control.process_list.itemDoubleClicked.connect(self.action_step_edit)
        self.control.search_result_list.customContextMenuRequested.connect(self.action_open_result_menu)
        self.control.process_list.customContextMenuRequested.connect(self.action_open_process_menu)
        self.control.arrow_btn.clicked.connect(self.action_step_add)
        self.control.exec_btn.clicked.connect(self.action_process_exec)
        self.control.data_load_btn.clicked.connect(self.action_load_func)
        self.control.generate_py_btn.clicked.connect(self.action_generate_py)
        self.control.search_btn.clicked.connect(lambda: self.action_search(1))
        # self.control.add_record_btn.clicked.connect(self.action_add_record)

        self.control.add_special_func_btn.menu.triggered.connect(self.special_step_handle_action)
        self.control.step_btn.menu.triggered.connect(self.step_handle_action)
        self.control.process_btn.menu.triggered.connect(self.process_handle_action)

        self.action_load_common_record()
        self.action_search()

    def action_common_step_selected(self):
        index = self.control.common_result_list.currentRow()
        if index != -1:
            self.control.search_result_list.setCurrentRow(-1)
        handler.common_step_click(index)
        func = ControlCenter.common_record[ControlCenter.common_checked]
        self.flash_or_load_preview(func)

    def action_step_selected(self):
        index = self.control.search_result_list.currentRow()
        if index != -1:
            self.control.common_result_list.setCurrentRow(-1)
        handler.step_click(index)
        func = ControlCenter.search_record[ControlCenter.record_checked]
        self.flash_or_load_preview(func)

    def flash_or_load_preview(self, func):
        params = "\n".join(
            [f"{index + 1}.{item}" for index, item in enumerate(json.loads(func.depict_params).values())])
        info = f'{func.depict_func}\n\n【参数】\n{params if params else "无"}\n\n【解释】\n{func.depict_return if func.depict_return else "无"}'

        self.control.pre_read_view.setText(info)

    def action_step_add(self, pos=None):
        t = None
        f = None
        index = self.control.search_result_list.currentRow()
        if index != -1:
            t = "noraml"
        else:
            index = self.control.common_result_list.currentRow()
            if index != -1:
                t = "common"
        if index == -1:
            self.app.dialog = DialogTip('请在搜索结果中选择对应方法后添加', parent=self.app.root)
            self.app.dialog.exec_()
            return

        if t == "common":
            handler.common_step_click(index)
            f = ControlCenter.common_record[ControlCenter.common_checked]
        elif t == "noraml":
            handler.step_click(index)
            f = ControlCenter.search_record[ControlCenter.record_checked]

        self.app.dialog = FuncParamDialog(f=f, pos=pos, parent=self.app.root)

        self.app.dialog.confirm.clicked.connect(self.action_step_insert)
        self.app.dialog.cancel.clicked.connect(self.app.dialog.close_dialog)

        self.app.dialog.exec_()

    def action_step_insert(self):
        """
        将搜索方法添加至流程中
        """
        if self.app.dialog:
            form_data = self.app.dialog.make_data()

            pos = self.check_edit_for_int(form_data.pop('self_process_index')) - 1

            handler.func_step_insert(pos, form_data.get('params', '{}'))
            # self.control.process_list.insertItem(pos, f'{ControlCenter.steps[pos].get("depict_func")}')
            self.action_flash_process()
            self.app.dialog.close_dialog()

        else:
            raise

    def action_step_update_order(self, f, t):
        handler.step_update_order(f, t)
        self.action_flash_process()

    def action_open_common_menu(self, position):
        """
        常用右键菜单
        """
        selected_index = control_func.common_result_list.currentRow()
        self.control.right_menu.clear()
        add_action = QAction('添加: 将步骤添加至流程中')
        self.control.right_menu.addAction(add_action)
        add_action.triggered.connect(lambda: self.handle_action('step_add'))
        unmark_action = QAction('移除: 将方法从常用中移除')
        self.control.right_menu.addAction(unmark_action)
        unmark_action.triggered.connect(lambda: self.handle_action('unmark_common'))
        self.control.right_menu.setEnabled(selected_index != -1)
        self.control.right_menu.exec_(self.control.common_result_list.mapToGlobal(position))

    def action_open_result_menu(self, position):
        """
        搜索结果右键菜单
        """
        selected_index = control_func.search_result_list.currentRow()
        self.control.right_menu.clear()
        add_action = QAction('添加: 将步骤添加至流程中')
        self.control.right_menu.addAction(add_action)
        add_action.triggered.connect(lambda: self.handle_action('step_add'))
        mark_action = QAction('常用: 将方法标记为常用')
        self.control.right_menu.addAction(mark_action)
        mark_action.triggered.connect(lambda: self.handle_action('mark_common'))
        self.control.right_menu.setEnabled(selected_index != -1)
        self.control.right_menu.exec_(self.control.search_result_list.mapToGlobal(position))

    def action_open_process_menu(self, position):
        """
        流程结果右键菜单
        """
        selected_index = control_func.process_list.currentRow()

        self.control.right_menu.clear()
        del_action = QAction('删除: 将步骤从流程中删除')
        self.control.right_menu.addAction(del_action)
        del_action.triggered.connect(lambda: self.handle_action('step_del'))
        edit_action = QAction('编辑: 重新编辑参数')
        self.control.right_menu.addAction(edit_action)
        edit_action.triggered.connect(lambda: self.handle_action('step_edit'))
        reset_action = QAction('重置: 将流程清空')
        self.control.right_menu.addAction(reset_action)
        reset_action.triggered.connect(lambda: self.handle_action('step_reset'))

        self.control.right_menu.setEnabled(selected_index != -1)
        self.control.right_menu.exec_(control_func.process_list.mapToGlobal(position))

    def handle_action(self, action):
        """
        处理右键菜单项
        """
        if action == 'step_add':
            self.action_step_add()
            self.control.right_menu.close()
        elif action == 'step_del':
            index = self.control.process_list.currentRow()
            handler.step_del(index)
            # self.control.process_list.takeItem(index)
            self.action_flash_process()
        elif action == 'step_reset':
            self.action_process_reset()
        elif action == 'step_edit':
            self.action_step_edit()
            self.control.right_menu.close()
        elif action == 'mark_common':
            handler.insert_func_into_common()
            self.action_flash_common_record()
        elif action == 'unmark_common':
            handler.cancel_func_into_common()
            self.action_flash_common_record()

    def action_step_edit(self):
        index = self.control.process_list.currentRow()
        ControlCenter.checked = index

        self.app.dialog = EditParamDialog(parent=self.app.root)

        self.app.dialog.confirm.clicked.connect(self.action_edit_step)
        self.app.dialog.cancel.clicked.connect(self.app.dialog.close_dialog)

        self.app.dialog.exec_()

    def action_edit_step(self):
        if self.app.dialog:
            means_dict = {"loop_count": "循环次数", "loop_steps": "循环步骤数", "name": "方法名"}
            form_data: dict = self.app.dialog.make_data()
            to_index = form_data.pop('self_process_update_index')

            func = ControlCenter.steps[ControlCenter.checked]
            temp = {}
            f_type = func.get('type')
            for key, value in form_data.items():
                if f_type == 'exist':
                    temp.update({key: value})
                elif f_type == 'define':
                    self.app.ui_log.info(f'录制方法名<{func.get("name")}>更新为<{value}>')
                    func[key] = value
                    self.control.process_list.currentItem().setText(f'{ControlCenter.checked + 1}.{value}')
                elif f_type == 'loop':
                    value = self.check_edit_for_int(value) if re.match(r'\d+', value) else value
                    if value != func[key]:
                        self.app.ui_log.info(f'循环方法<{func.get("name")}>{means_dict.get(key, None)}值更新为<{value}>')
                        func[key] = value
                        if key == "name":
                            self.control.process_list.currentItem().setText(f'{ControlCenter.checked + 1}.{value}')
            if func.get('type') == 'exist' and func["params"] != json.dumps(temp):
                func["params"] = json.dumps(temp)
                self.app.ui_log.info(f'<{func.get("depict_func")}>参数更新成功')

            if self.check_edit_for_int(to_index) - 1 != ControlCenter.checked:
                self.action_step_update_order(self.control.process_list.currentRow(), int(to_index) - 1)
            self.app.dialog.close_dialog()

    def action_flash_common_record(self):
        """
        刷新常用方法
        """
        self.control.common_result_list.clear()
        handler.load_common_record()
        for index, func in enumerate(ControlCenter.common_record):
            line = f'{index + 1}.{func.depict_func}'
            self.control.common_result_list.addItem(line)

    def action_load_common_record(self):
        """
        加载常用方法
        """
        self.action_flash_common_record()

    def action_search(self, way=0):
        """
        执行搜索
        """
        self.control.search_result_list.clear()
        search_key = self.control.search_line.text()
        handler.func_search(search_key)
        if way == 0:
            app_root.ui_log.info(f'共加载{len(ControlCenter.search_record)}个方法')
        else:
            app_root.ui_log.info(f'搜索到{len(ControlCenter.search_record)}个方法')
        for index, func in enumerate(ControlCenter.search_record):
            line = f'{index + 1}.{func.depict_func}'
            self.control.search_result_list.addItem(line)

    def action_flash_process(self):
        self.control.process_list.clear()
        for index, func in enumerate(ControlCenter.steps):
            if func.get('type') == 'exist':
                line = f'{index + 1}.{func.get("depict_func", None)}'
                self.control.process_list.addItem(line)
            elif func.get('type') == 'define' or func.get('type') == 'loop':
                line = f'{index + 1}.{func.get("name", None)}'
                self.control.process_list.addItem(line)
        ControlCenter.exec_step_end = len(ControlCenter.steps)

    def action_define_step_insert(self, events):
        if self.app.dialog is not None:
            data = self.app.dialog.make_data()
            pos = self.check_edit_for_int(data.get('self_process_index')) - 1
            name = data.get('name') if data.get('name') is not None else '自定义方法'
            handler.define_step_insert(events, pos, name)
            # self.control.process_list.insertItem(pos, name)
            self.action_flash_process()
            self.app.root.normal_window()
            self.app.dialog.close_dialog()
        else:
            raise

    def action_add_record(self):
        """
        添加录制方法
        """
        self.app.dialog = DefineParamDialog(self.app.root)
        # self.app.dialog.watch_thread.event_signal.connect(self.action_define_step_insert)
        if self.app.key_watch_task_insert is False:
            self.app.key_watch.event_signal.connect(self.action_define_step_insert)
            self.app.key_watch_task_insert = True
        self.app.dialog.exec_()

    def action_add_loop(self):
        """
        添加循环方法
        """
        self.app.dialog = LoopParamDialog(self.app.root)
        self.app.dialog.confirm_btn.clicked.connect(self.action_loop_step_insert)
        self.app.dialog.exec_()

    def action_loop_step_insert(self):
        if self.app.dialog is not None:
            data = self.app.dialog.make_data()
            name = data.get('name') if data.get('name') is not None else '自定义方法'
            pos = self.check_edit_for_int(data.get('self_process_index')) - 1
            loop_steps = self.check_edit_for_int(data.get('loop_steps')) if data.get('loop_steps') is not None else 0
            loop_count = self.check_edit_for_int(data.get('loop_count')) if data.get('loop_count') is not None else 1
            handler.loop_step_insert(loop_steps=loop_steps, loop_count=loop_count, pos=pos, name=name)
            self.action_flash_process()
            self.app.dialog.close_dialog()

    def action_process_exec(self):
        self.app.dialog = ExecDialog(self.app.root)
        self.app.dialog.exec_()

    def action_process_finish(self):
        self.app.root.normal_window()
        self.app.dialog.info_label.setText('执行完毕')

    def action_process_reset(self):
        handler.step_reset()
        if self.control.process_list.count() > 0:
            self.app.ui_log.info('流程已重置')
            self.control.process_list.clear()
        else:
            self.app.ui_log.info('流程为空，无需重置')

    def action_read_process(self):
        """
        读取流程,从自定义文件中读取
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self.app.root, "打开流程文件", str(settings.Files.PROCESS_DIR),
                                                   "JSON Files (*.json)", options=options)
        if file_path:
            handler.process_read(file_path)
            self.action_flash_process()

    def action_save_process(self):
        """
        将留存储存到自定义文件中
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self.app.root, "保存流程", str(settings.Files.PROCESS_DIR),
                                                   "JSON Files (*.json)", options=options)
        if file_path:
            handler.process_save(file_path)

    def action_load_func(self):
        self.app.dialog = LoadDialog(self.app.root)
        self.app.dialog.exec_()

    def action_generate_py(self):
        """
        生成py代码
        """
        self.app.dialog = GeneratePyDialog(self.app.root)
        self.app.dialog.exec_()

    def special_step_handle_action(self, action):
        if action.text() == "添加录制方法":
            self.action_add_record()
        elif action.text() == "添加循环方法":
            self.action_add_loop()

    def action_save_step(self):
        """
        将步骤储存到自定义文件中
        """
        if self.app.dialog is not None:
            data = self.app.dialog.make_data()
            f = self.check_edit_for_int(data.get("from"))
            t = self.check_edit_for_int(data.get("to"))

            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self.app.root, "保存步骤", str(settings.Files.PROCESS_DIR),
                                                       "JSON Files (*.json)", options=options)
            if file_path:
                handler.steps_save(f=f, t=t, file_path=file_path)
                self.app.dialog.close_dialog()

    def action_export_step(self):
        self.app.dialog = StepExportDialog(self.app.root)
        self.app.dialog.confirm_btn.clicked.connect(self.action_save_step)
        self.app.dialog.exec_()

    def action_insert_steps(self):
        if self.app.dialog is not None:
            data = self.app.dialog.make_data()
            t = self.check_edit_for_int(data.get("to"))

            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(self.app.root, "插入步骤", str(settings.Files.PROCESS_DIR),
                                                       "JSON Files (*.json)", options=options)
            if file_path:
                handler.steps_read(pos=t, file_path=file_path)
                self.action_flash_process()
                self.app.dialog.close_dialog()

    def action_import_step(self):
        self.app.dialog = StepImportDialog(self.app.root)
        self.app.dialog.confirm_btn.clicked.connect(self.action_insert_steps)
        self.app.dialog.exec_()

    def step_handle_action(self, action):
        if action.text() == '导入':
            self.action_import_step()
        elif action.text() == '导出':
            self.action_export_step()

    def process_handle_action(self, action):
        if action.text() == '重置':
            self.action_process_reset()
        elif action.text() == '导入':
            self.action_read_process()
        elif action.text() == '导出':
            self.action_save_process()

    def check_edit_for_int(self, val):
        try:
            return int(val)
        except Exception:
            self.app.ui_log.warning(f'{val}需要为整数')
            raise
