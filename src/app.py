import os
import sys

from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QAction,
    QShortcut,
    QListView,
    QHBoxLayout,
    QWidget
)

from src.show_image import ShowImage
from utils.data_utils import use_collection, my_db
from utils.fetch_images_info import create_ssh_client


class FilterImagesMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_path = os.path.dirname(os.path.dirname(__file__)) + '/app_images/'
        self.db = my_db
        self.path = "default"
        self.collection = use_collection(self.path) if self.path != "" else use_collection("default")
        # self.ssh_client = create_ssh_client("192.168.13.201", "nb201", "22")
        self.ssh_client = create_ssh_client("119.23.33.220", "chris", "22")

        self.show_image = ShowImage(self.db, self.path, self.collection, self.ssh_client)
        self.collections_list_view = QListView(self)
        self.main_layout = QHBoxLayout(self)

        self.visitable_image_sc = QShortcut("v", self)
        self.unvisitable_image_sc = QShortcut("h", self)
        self.initUI()

    def initUI(self):
        self.addShortCutEvent()
        self.setUpLayout()
        self.initMenuBar()
        self.initToolBar()
        self.statusBar()

        main_window = QWidget()
        main_window.setLayout(self.main_layout)
        self.setCentralWidget(main_window)
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Filter Images')
        self.show()

    def setUpLayout(self):
        collections = self.db.list_collection_names()
        model = QStandardItemModel()
        for collection in sorted(collections):
            model.appendRow(QStandardItem(collection))
        self.collections_list_view.setModel(model)

        self.main_layout.addWidget(self.collections_list_view)
        self.main_layout.addWidget(self.show_image)

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
