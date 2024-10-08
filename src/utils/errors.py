class DbError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class FileExistError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class RunError(Exception):
    def __init__(self, msg):
        super().__init__(msg)