from src import frontend
import sys
from src.intermediary.data_load import init_table

init_table()

if __name__ == '__main__':
    app = frontend.QApplication(sys.argv)
    ex = frontend.App()
    ex.show()
    sys.exit(app.exec_())

