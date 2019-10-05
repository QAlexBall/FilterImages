import os
import subprocess

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QShortcut,
    QVBoxLayout)
from utils.data_utils import use_collection
from utils.fetch_images_info import previous_image, next_image


def _getCurrentImagePath():
    dirs = subprocess.Popen('ls', shell=True)
    print(dirs)


class ShowImage(QWidget):

    def __init__(self):
        super().__init__()
        self.images_folder = None
        self.tmp_image = os.path.dirname(os.path.dirname(__file__)) + '/app_images/tmp.jpg'
        self.collection = use_collection("nb201-leopaper301_s3")

        self.pixmap = QPixmap(self.tmp_image).scaled(800, 600, Qt.KeepAspectRatio)
        self.pixmap_label = QLabel(self)
        self.image_info_label = QLabel(self)
        self.image_path_label = QLabel(self)
        self.previous_button = QPushButton("Previous", self)
        self.next_button = QPushButton("Next", self)
        self.delete_button = QPushButton("Delete", self)
        self.previous_shortcut = QShortcut("d", self)
        self.next_shortcut = QShortcut("f", self)
        self.main_layout = QHBoxLayout()
        self.button_layout = QVBoxLayout()

        self.reload_tmp_image()
        # _getCurrentImagePath()
        self.initUI()

    def reload_tmp_image(self):
        current_image_id = self.collection.find_one({"class": "app"})["current_image_id"]
        remote_image_record = self.collection.find_one({"id": current_image_id})
        remote_image_path = remote_image_record['path']
        cmd = "scp -P 9201 nb201@119.23.33.220:{} {}".format(remote_image_path, self.tmp_image)
        print(cmd)
        subprocess.getoutput(cmd)
        self.pixmap = QPixmap(self.tmp_image).scaled(800, 600, Qt.KeepAspectRatio)
        self.pixmap_label.setPixmap(self.pixmap)
        self.image_info_label.setText("current_image_id: {}".format(current_image_id))
        self.image_path_label.setText("path: {}".format(remote_image_path))
        self.main_layout.update()

    def initUI(self):
        self.setUpLayout()
        self.addButtonClick()
        self.addShortCutEvent()

    def setUpLayout(self):
        # TODO => why can't show remote images with pixmap?
        self.pixmap_label.setPixmap(self.pixmap)
        current_image_id = self.collection.find_one({"class": "app"})["current_image_id"]
        self.image_info_label.setText("current_image_id: {}".format(current_image_id))
        self.image_path_label.setText("please enter next.")

        self.button_layout.addWidget(self.image_info_label)
        self.button_layout.addWidget(self.image_path_label)
        self.button_layout.addWidget(self.previous_button)
        self.button_layout.addWidget(self.next_button)
        self.button_layout.addWidget(self.delete_button)
        self.main_layout.addWidget(self.pixmap_label)
        self.main_layout.addLayout(self.button_layout)
        self.setLayout(self.main_layout)

    def addShortCutEvent(self):
        self.previous_shortcut.activated.connect(self.on_previous_button_click)
        self.next_shortcut.activated.connect(self.on_next_button_click)

    def addButtonClick(self):
        self.previous_button.clicked.connect(self.on_previous_button_click)
        self.next_button.clicked.connect(self.on_next_button_click)

    @pyqtSlot()
    def on_previous_button_click(self):
        previous_image(self.collection)
        self.reload_tmp_image()
        print("on previous button clicked")

    @pyqtSlot()
    def on_next_button_click(self):
        next_image(self.collection)
        self.reload_tmp_image()
        print("on next button clicked")


def setUpShowImage():
    show_image = ShowImage()
    return show_image
