from PyQt5.QtWidgets import QMainWindow, QApplication, QMenu, QMenuBar, QWidget, QVBoxLayout, QLabel
import sys
from src.ui.dashboard import MainFrame


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_frame = MainFrame()
    main_frame.show()
    sys.exit(app.exec_())