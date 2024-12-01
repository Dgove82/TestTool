import zipfile
import os
import winreg
import ctypes
import sys
import subprocess
import shutil

remote_zip = r'C:\Users\dgove\Desktop\Env.zip'


def recursion_decode_path(path: str):
    """
    路径遍历
    """
    root = path
    if os.path.isdir(path):
        for p in os.listdir(path):
            name = decode_name(p)
            os.rename(os.path.join(path, p), os.path.join(root, name))
            recursion_decode_path(os.path.join(root, name))
    else:
        p = os.path.basename(path)
        d = os.path.dirname(path)
        name = decode_name(p)
        os.rename(path, os.path.join(d, name))


def decode_name(name: str):
    try:
        name = name.encode('cp437').decode('utf-8')
    finally:
        return name


def unzip_with_progress(zip_path, extract_folder):
    os.makedirs(extract_folder, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # 获取 zip 文件中的所有文件
        list_of_files = zip_ref.namelist()
        # 计算文件总数
        total_files = len(list_of_files)
        # 用于跟踪已处理的文件数量
        processed_files = 0

        # 遍历 zip 文件中的每个文件
        for file in list_of_files:
            # 解压文件
            zip_ref.extract(file, extract_folder)
            # 更新进度
            processed_files += 1
            print(f"\rExtracting: {file} ({processed_files}/{total_files})")

    # 文件名乱码检查
    recursion_decode_path(extract_folder)


def zip_folder(in_folder, out_zip):
    # 创建一个zip文件
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历目录
        for root, dirs, files in os.walk(in_folder):
            for file in files:
                print(f'\r{file}压缩完成')
                # 构建完整的文件路径
                file_path = os.path.join(root, file)
                # 将文件添加到zip文件中，排除父目录
                zipf.write(str(file_path), str(os.path.relpath(str(file_path), os.path.dirname(in_folder))))


def update_path(new_path):
    # 请求管理员权限
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    # 打开环境变量注册表键
    registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                  'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment', 0,
                                  winreg.KEY_ALL_ACCESS)

    # 读取现有的 Path 环境变量值
    path_value, reg_type = winreg.QueryValueEx(registry_key, 'Path')

    if new_path not in path_value.split(';'):
        # 如果新路径不在 Path 中，则添加它
        path_value = new_path + ';' + path_value

        # 设置新的 Path 值
        winreg.SetValueEx(registry_key, 'Path', 0, winreg.REG_EXPAND_SZ, path_value)

        # 确保所有进程都能看到这个变量
        winreg.FlushKey(registry_key)

    # 关闭注册表键
    winreg.CloseKey(registry_key)
    print(f'{new_path} 环境变量配置完毕')


def add_variable(k, v):
    # 请求管理员权限
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    # 打开环境变量注册表键
    registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                  'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment', 0,
                                  winreg.KEY_ALL_ACCESS)

    try:
        # 设置新的 JAVA_HOME 值
        winreg.SetValueEx(registry_key, k, 0, winreg.REG_EXPAND_SZ, v)
        # 确保所有进程都能看到这个变量
        winreg.FlushKey(registry_key)
        print(f'{k} 环境变量配置完毕: {v}')
    except Exception as e:
        print(f'无法设置 {k} 环境变量: {e}')
    finally:
        # 关闭注册表键
        winreg.CloseKey(registry_key)


def handler_zip():
    folder_in = input('请输入需要打包的目录')
    folder_out = input('请输入输出的目录+zip包名')
    if not folder_in or not folder_out:
        print('请输入对应值')
        return
    zip_folder(folder_in, folder_out)


def handler_unzip():
    folder_in = input('请输入解包目录+zip包名')
    folder_out = input('请输入输出到的目录')
    if not folder_in or not folder_out:
        print('请输入对应值')
        return
    unzip_with_progress(folder_in, folder_out)


def install_for_python_package():
    packages = r'C:\Env\Installation_package\python'
    for package in os.listdir(packages):
        process = subprocess.run([r"C:\Env\Python\Scripts\pip.exe", "install", str(os.path.join(packages, package))])
        if process.returncode != 0:
            print(f'fail:{package}安装失败')
        else:
            print(f'success:{package}安装完毕')


def download_package_from_cloud(target=None, local=None):
    if os.path.exists(local):
        print('本地存在压缩包，跳过拉取')
    else:
        print(f'开始从{target}拉取压缩包, 请等待...')
        shutil.copy(target, local)
        print('压缩包拉取完毕')


def init_depends():
    try:
        cloud_net = remote_zip
        local_zip = r'C:\Env.zip'
        download_package_from_cloud(target=cloud_net, local=local_zip)
        lock_out = r'C:\Env'
        if os.path.exists(lock_out):
            cmd = input('依赖目录已经存在，是否继续安装请输入[y], 其他字符取消\n请输入')
            if cmd.lower() != 'y':
                print('已取消')
                return
            shutil.rmtree(lock_out)
            print('已经历史依赖目录移除')

        unzip_with_progress(local_zip, lock_out)

        update_path(r'C:\Env\Python')
        update_path(r'C:\Env\Python\Scripts')
        update_path(r'C:\Env\Git\cmd')
        update_path(r'C:\Env\Java\jdk-21\bin')
        update_path(r'C:\Env\Allure\bin')
        add_variable('Java_Home', r'C:\Env\Java\jdk-21')

        install_for_python_package()
        print('重启电脑后系统环境变量生效')
    except Exception as e:
        print(f'初始化失败: {e}')


def handler():
    while True:
        print("""
    请输入对应编号执行功能
    [1] 压缩文件
    [2] 解压文件
    [3] 初始化环境
        """)
        cmd = input()
        if cmd == '1':
            handler_zip()
        elif cmd == '2':
            handler_unzip()
        elif cmd == '3':
            init_depends()
        else:
            break


if __name__ == '__main__':
    handler()
