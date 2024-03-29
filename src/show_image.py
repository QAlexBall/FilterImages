import logging
import os

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QShortcut,
    QVBoxLayout,
    QInputDialog,
    QMessageBox)

from utils.data_utils import use_collection, my_db, read_config, update_collection_config
from utils.fetch_images_info import (
    previous_image,
    next_image,
    set_image,
    get_all_image,
    update_current_image_id)

logging.basicConfig(level=logging.INFO)


class ShowImage(QWidget):

    def __init__(self, db, path, collection, ssh_client):
        super().__init__()
        self.images_folder = None
        self.tmp_image = os.path.dirname(os.path.dirname(__file__)) + '/app_images/tmp.png'
        self.db = db
        self.path = path
        self.collection = collection
        # self.ssh_client = create_ssh_client("192.168.13.201", "nb201", "22")
        self.ssh_client = ssh_client
        self.ftp_client = self.ssh_client.open_sftp()

        # widget
        self.pixmap = QPixmap(self.tmp_image).scaled(800, 600, Qt.KeepAspectRatio)
        self.pixmap_label = QLabel(self)
        self.image_info_label = QLabel(self)
        self.image_path_label = QLabel(self)

        self.previous_button = QPushButton("Previous(D)", self)
        self.next_button = QPushButton("Next(F)", self)
        self.delete_button = QPushButton("Delete", self)
        self.set_image_id_button = QPushButton("SetImageID", self)
        self.load_path_button = QPushButton("LoadPath", self)
        self.reload_path_button = QPushButton("ReloadPath", self)

        self.previous_shortcut = QShortcut("d", self)
        self.next_shortcut = QShortcut("f", self)

        # layout
        self.main_layout = QHBoxLayout()
        self.image_info_layout = QVBoxLayout()
        self.button_layout = QVBoxLayout()

        # init
        self.reload_tmp_image()
        self.initUI()

    def reload_tmp_image(self):
        # load current collection from config.json
        if self.path == "default":
            config = read_config()
            self.path = config.get('current_collection', 'default')
            self.collection = use_collection(self.path) if self.path != "" else use_collection("default")
        else:
            # reload layout for images.
            print("start reload")
            current_image_id = self.collection.find_one({"class": "app"})["current_image_id"]
            remote_image_record = self.collection.find_one({"id": current_image_id})
            if remote_image_record:
                remote_image_path = remote_image_record['path']
                try:
                    self.ftp_client.get(remote_image_path, self.tmp_image) # get image from remote
                    self.pixmap = QPixmap(self.tmp_image).scaled(800, 600, Qt.KeepAspectRatio)
                    self.pixmap_label.setPixmap(self.pixmap)
                    self.image_info_label.setText("current_image_id: {}".format(current_image_id))
                    self.image_path_label.setText("path: {}".format(remote_image_path))
                    print("end reload")
                except FileNotFoundError as e:
                    raise e
            else:
                self.image_path_label.setText("no such image path.")
                self.image_info_label.setText("current_image_id: {} not exist.".format(current_image_id))

    def initUI(self):
        self.setUpLayout()
        self.addButtonClick()
        self.addShortCutEvent()

    def setUpLayout(self):
        # TODO => why can't show remote images with pixmap?
        self.pixmap_label.setPixmap(self.pixmap)
        print(self.path, self.collection)
        current_image_app = self.collection.find_one({"class": "app"})
        current_image_id = current_image_app['current_image_id'] \
            if self.path != "default" and current_image_app is not None \
            else "-1 \n please load remote path"

        self.image_info_label.setText("current_image_id: {}".format(current_image_id))
        self.image_path_label.setText("please enter next.")

        # add widget
        self.button_layout.addWidget(self.image_info_label)
        self.button_layout.addWidget(self.load_path_button)
        self.button_layout.addWidget(self.reload_path_button)
        self.button_layout.addWidget(self.set_image_id_button)
        self.button_layout.addWidget(self.previous_button)
        self.button_layout.addWidget(self.next_button)
        self.button_layout.addWidget(self.delete_button)
        self.image_info_layout.addWidget(self.image_path_label)
        self.image_info_layout.addWidget(self.pixmap_label)

        # add layout
        self.main_layout.addLayout(self.image_info_layout)
        self.main_layout.addLayout(self.button_layout)
        self.setLayout(self.main_layout)

    def addShortCutEvent(self):
        self.previous_shortcut.activated.connect(self.on_previous_button_click)
        self.next_shortcut.activated.connect(self.on_next_button_click)

    def addButtonClick(self):
        self.previous_button.clicked.connect(self.on_previous_button_click)
        self.next_button.clicked.connect(self.on_next_button_click)
        self.delete_button.clicked.connect(self.on_delete_button_click)
        self.set_image_id_button.clicked.connect(self.show_dialog)
        self.load_path_button.clicked.connect(self.load_remote_path)
        self.reload_path_button.clicked.connect(self.reload_remote_path)

    @pyqtSlot()
    def load_remote_path(self):
        path, ok = QInputDialog.getText(self, "Input Remote Path", "Enter Path: ")
        collection = self.db[path] if path != "" else use_collection("default")
        data_info = collection.find_one({'class': 'app'})

        stdin, stdout, stderr = self.ssh_client.exec_command("ls {}".format(path))
        path_exist = True if stdout.read().decode() != "" else False
        if not path_exist:
            my_db.drop_collection(path)
            self.load_remote_path()
        elif ok and data_info is None:
            get_all_image(self.ssh_client, collection, folder_name=path)
            update_current_image_id(collection, 'init')
            # update config.json
            update_collection_config(path)
            print("load finished.")
        elif ok and data_info is not None:
            self.collection = collection

    @pyqtSlot()
    def reload_remote_path(self):
        self.db.drop_collection(self.path)
        self.load_remote_path()

    @pyqtSlot()
    def on_previous_button_click(self):
        message = previous_image(self.collection)
        if message is None:
            self.reload_tmp_image()
        else:
            QMessageBox.about(self, "previous_button", message)
        print("on previous button clicked")

    @pyqtSlot()
    def on_next_button_click(self):
        message = next_image(self.collection)
        print(message)
        if message is None:
            self.reload_tmp_image()
        else:
            QMessageBox.about(self, "next_button", message)
        print("on next button clicked")

    @pyqtSlot()
    def show_dialog(self):
        text, ok = QInputDialog.getText(self, "Input Image Id", "Enter ID: ")
        print(text, ok)
        if ok:
            image_exist = set_image(self.collection, int(str(text)))
            print("==>", image_exist)
            if image_exist:
                self.reload_tmp_image()
            else:
                QMessageBox.about(self, "no_image", "No such Images Id.")

    @pyqtSlot()
    def on_delete_button_click(self):
        # TODO => prepare to delete remote image?
        current_image_id = self.collection.find_one({"class": "app"})["current_image_id"]
        remote_image_record = self.collection.find_one({"id": current_image_id})
        remote_image_path = remote_image_record['path']
        print("delete =>", remote_image_path)
        next_image(self.collection)
        self.reload_tmp_image()
