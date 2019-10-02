import os
import sys
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QAction,
    QShortcut,
)
from src.show_image import setUpShowImage


class FilterImagesMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.path = os.path.dirname(os.path.dirname(__file__))
        self.image_path = self.path + '/app_images/'

        self.show_image = setUpShowImage()
        self.visitable_image_sc = QShortcut("v", self)
        self.unvisitable_image_sc = QShortcut("h", self)
        self.initUI()

    def initUI(self):
        self.addShortCutEvent()

        self.initMenuBar()
        self.initToolBar()
        self.statusBar()
        self.setCentralWidget(self.show_image)
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Filter Images')
        self.show()

    def addShortCutEvent(self):
        self.visitable_image_sc.activated.connect(self.show_image_func)
        self.unvisitable_image_sc.activated.connect(self.hide_image_func)

    def hide_image_func(self):
        if self.show_image.isVisible():
            self.show_image.close()

    def show_image_func(self):
        if not self.show_image.isVisible():
            self.show_image.show()

    def initMenuBar(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('&File')
        menubar.addMenu('&Edit')
        menubar.addMenu('&View')

        openAction = QAction('open', self)
        fileMenu.addAction(openAction)

    def initToolBar(self):
        exitAct = QAction(QIcon(self.image_path + 'exit.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)
        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAct)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    filter_image = FilterImagesMainWindow()
    sys.exit(app.exec_())
