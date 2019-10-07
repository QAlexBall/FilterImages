from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QInputDialog, QApplication, QVBoxLayout)
import sys
from utils.data_utils import use_collection
from utils.fetch_images_info import set_image


class SetImageIdDialog(QWidget):

    def __init__(self):
        super().__init__()
        self.set_image_id_button = QPushButton('set_id', self)
        self.main_layout = QVBoxLayout(self)
        self.collection = use_collection("nb201-leopaper301_s3")

        self.initUI()

    def initUI(self):
        self.setUpLayout()
        self.addButtonClick()
        # self.addShortCutEvent()

    def setUpLayout(self):
        self.main_layout.addWidget(self.set_image_id_button)

    def addButtonClick(self):
        self.set_image_id_button.clicked.connect(self.show_dialog)

    def show_dialog(self):
        text, ok = QInputDialog.getText(self, "Input Image Id", "Enter ID: ")
        print(text, ok)
        if ok:
            set_image(self.collection, int(str(text)))
