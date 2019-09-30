import sys
import os
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel
)
from PyQt5.QtGui import QPixmap
import subprocess


def _getCurrentImagePath():
    dirs = subprocess.Popen('ls', shell=True)
    print(dirs)


class ShowImage(QWidget):

    def __init__(self):
        super().__init__()
        self.images_folder = None
        self.tmp_image = os.path.dirname(__file__) + '/app_images/tmp.png'
        self._remote_host = None
        self._remote_folder = None
        self._remote_uri = "{}:{}".format(self._remote_host, self._remote_folder)
        _getCurrentImagePath()
        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout(self)
        pixmap = QPixmap(self.tmp_image)
        lbl = QLabel(self)
        lbl.setPixmap(pixmap)
        hbox.addWidget(lbl)
        self.setLayout(hbox)

    def setHost(self, remote_host):
        self._remote_host = remote_host

    def setFolder(self, remote_folder_name):
        self._remote_folder = remote_folder_name

    def _loadTmpImage(self):
        pass

    @classmethod
    def _deleteTmpImage(cls):
        pass

    @classmethod
    def _saveRemoteImagesPath(cls):
        pass
