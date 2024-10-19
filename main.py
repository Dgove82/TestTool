from src.frontend.ui import QApplication, App
import sys
import os


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())

