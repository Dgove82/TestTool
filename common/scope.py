import os


def encode_bin(root, target: str):
    if not os.path.exists(target):
        os.mkdir(target)

    for dirpath, dirnames, filenames in os.walk(root):

        target_path = os.path.join(target, str(os.path.relpath(dirpath, root)))

        for file in filenames:
            try:
                with open(os.path.join(dirpath, file), 'rb') as f:
                    txt = f.read()
                with open(os.path.join(target_path, file) + ".bin", 'wb') as f:
                    f.write(txt)
            except Exception as e:
                print(f'{file}转写失败: {e}')

        for dirname in dirnames:
            os.makedirs(os.path.join(target_path, dirname), exist_ok=True)


def decode_bin(target: str):
    if not os.path.exists(target):
        raise FileNotFoundError(f'{target}不存在')

    for dirpath, dirnames, filenames in os.walk(target):
        for file in filenames:
            if file.endswith('.bin'):
                os.rename(os.path.join(dirpath, file), os.path.join(dirpath, file.replace('.bin', '')))


def file_pull(target: str, local: str):
    import shutil
    if os.path.exists(local):
        return
    if os.path.isdir(target):
        shutil.copytree(target, local)
    else:
        extension_name = target.split('.')[-1]
        if extension_name in ['zip', 'tar', 'gz', 'bz2']:
            shutil.unpack_archive(target, local)
        else:
            shutil.copyfile(target, local)
    print('文件预处理完毕')


if __name__ == '__main__':
    # encode_bin('/Volumes/A-Dgove/Code/Python-Projects/WorkSpace/temp', '../target')
    # decode_bin('../target')
    file_pull(r'/Volumes/A-Dgove/Code/Python-Projects/WorkSpace/target/ss.py',
              r'/Volumes/A-Dgove/Code/Python-Projects/WorkSpace/qq.py')
