from src import frontend
import sys


if __name__ == '__main__':
    app = frontend.QApplication(sys.argv)
    ex = frontend.App()
    ex.show()
    sys.exit(app.exec_())

