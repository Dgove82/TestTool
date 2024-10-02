import settings
from src.utils.tools import JsonFile
from library.element import Element


class Ctrl:
    def __init__(self, steps: list):
        """

        :param steps: [depict_func1, depict_func2, depict_func3]
        progress: [(func, param), (func, parma)...]
        """
        self.steps = steps
        self.progress = []

        self.load_func()

    def load_func(self):
        res = JsonFile(settings.FILES_PATH.joinpath('temps.json')).read()
        for step in self.steps:
            for func in res:
                temp = func.get('depict_func', '')
                if step in temp:
                    self.progress.append((func.get('func'), func.get('params')))

    def exec(self):
        assert len(self.progress) > 1, '无对应方法'

        e = Element()
        for f in self.progress:
            getattr(e, f[0])(**f[1])
