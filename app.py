import sys
import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QTextEdit,
    QAction,
    QHBoxLayout,
    QGraphicsPixmapItem
)
from show_image import ShowImage


class FilterImagesMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.show_image = ShowImage()
        self.path = os.path.dirname(__file__)
        self.image_path = self.path + '/app_images/'

        self.initUI()

    def initUI(self):
        textEdit = QTextEdit()
        self.setCentralWidget(textEdit)
        exitAct = QAction(QIcon(self.image_path + 'exit.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileAction = QAction('New', self)
        fileMenu.addAction(fileAction)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAct)

        self.addMyWidgets()

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Filter Images')
        self.show()

    def addMyWidgets(self):
        self.setUpShowImage()

    def setUpShowImage(self):
        show_image = ShowImage()
        show_image.setHost("nb201@192.168.13.201")
        show_image.setFolder("/mnt/hdd/dataset/Images")
        self.setCentralWidget(show_image)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    filter_image = FilterImagesMainWindow()
    sys.exit(app.exec_())
