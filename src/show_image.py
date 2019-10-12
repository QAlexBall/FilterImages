import os
import json
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QShortcut,
    QVBoxLayout,
    QInputDialog,
    QListView)
from utils.data_utils import use_collection, my_db
from utils.fetch_images_info import previous_image, next_image, create_ssh_client
from utils.fetch_images_info import set_image, get_all_image, update_current_image_id


class ShowImage(QWidget):

    def __init__(self):
        super().__init__()
        self.images_folder = None
        self.tmp_image = os.path.dirname(os.path.dirname(__file__)) + '/app_images/tmp.jpg'
        self.db = my_db
        self.path = "default"
        self.collection = use_collection(self.path)
        self.ssh_client = create_ssh_client("192.168.13.201", "nb201", "22")
        self.ftp_client = self.ssh_client.open_sftp()

        # widget
        self.pixmap = QPixmap(self.tmp_image).scaled(800, 600, Qt.KeepAspectRatio)
        self.pixmap_label = QLabel(self)
        self.image_info_label = QLabel(self)
        self.image_path_label = QLabel(self)

        self.collections_list_view = QListView(self)

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
        self.button_layout = QVBoxLayout()
        self.image_info_layout = QVBoxLayout()

        # init
        self.reload_tmp_image()
        self.initUI()

    def reload_tmp_image(self):
        # load current collection from config.json
        if self.path == "default":
            config_file = open('../config.json', 'r')
            config = json.load(config_file)
            self.path = config.get('current_collection', 'default')
            self.collection = use_collection(self.path)
            config_file.close()

        # reload layout for images.
        print("start reload")
        current_image_id = self.collection.find_one({"class": "app"})["current_image_id"]
        remote_image_record = self.collection.find_one({"id": current_image_id})
        if remote_image_record:
            remote_image_path = remote_image_record['path']
            self.ftp_client.get(remote_image_path, self.tmp_image)  # get image from remote
            self.pixmap = QPixmap(self.tmp_image).scaled(800, 600, Qt.KeepAspectRatio)
            self.pixmap_label.setPixmap(self.pixmap)
            self.image_info_label.setText("current_image_id: {}".format(current_image_id))
            self.image_path_label.setText("path: {}".format(remote_image_path))
            print("end reload")
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
        current_image_id = self.collection.find_one({"class": "app"})["current_image_id"] \
            if self.path != "default" else "-1 \n please load remote path"

        self.image_info_label.setText("current_image_id: {}".format(current_image_id))
        self.image_path_label.setText("please enter next.")

        collections = self.db.list_collection_names()
        model = QStandardItemModel()
        for collection in sorted(collections):
            model.appendRow(QStandardItem(collection))
        self.collections_list_view.setModel(model)

        # add widget
        self.button_layout.addWidget(self.image_info_label)
        self.button_layout.addWidget(self.load_path_button)
        self.button_layout.addWidget(self.reload_path_button)
        self.button_layout.addWidget(self.set_image_id_button)
        self.button_layout.addWidget(self.previous_button)
        self.button_layout.addWidget(self.next_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.collections_list_view)
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
        stdin, stdout, stderr = self.ssh_client.exec_command("ls {}".format(path))
        path_exist = True if stdout.read().decode() != "" else False
        self.collection = self.db[path]
        data_info = self.collection.find_one({'class': 'app'})
        print(data_info)
        if not path_exist:
            my_db.drop_collection(path)
            self.load_remote_path()
        if ok and data_info is None:
            self.path = path
            get_all_image(self.ssh_client, self.collection, folder_name=path)
            update_current_image_id(self.collection, 'init')
        else:
            self.path = path
            self.collection = self.db[path]

        # update config.json
        config_file = open('../config.json', 'r')
        config = json.load(config_file)
        config_file.close()

        config_file = open('../config.json', 'w')
        config['current_collection'] = path
        json.dump(config, config_file, indent=4)
        config_file.close()
        print("load finished.")

    @pyqtSlot()
    def reload_remote_path(self):
        self.db.drop_collection(self.path)
        self.load_remote_path()

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

    @pyqtSlot()
    def show_dialog(self):
        text, ok = QInputDialog.getText(self, "Input Image Id", "Enter ID: ")
        print(text, ok)
        if ok:
            set_image(self.collection, int(str(text)))
            self.reload_tmp_image()

    @pyqtSlot()
    def on_delete_button_click(self):
        # TODO => prepare to delete remote image?
        current_image_id = self.collection.find_one({"class": "app"})["current_image_id"]
        remote_image_record = self.collection.find_one({"id": current_image_id})
        remote_image_path = remote_image_record['path']
        print("delete =>", remote_image_path)
        next_image(self.collection)
        self.reload_tmp_image()
