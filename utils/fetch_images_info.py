import os
import json
import paramiko
import logging
import subprocess
from utils.data_utils import my_db, create_collection

logging.basicConfig(level=logging.INFO)


def create_ssh_client(hostname="192.168.13.201", username="nb201", port=22):
    logging.info("connect to {}@{}:{}".format(username, hostname, port))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh.connect(hostname=hostname, port=port, username=username)
    return ssh


def fetch_folder(ssh, parent_folder="/mnt/hdd/dataset/leopaper301_s3/"):
    stdin, stdout, stderr = ssh.exec_command('ls {}'.format(parent_folder))
    result = stdout.read().decode()
    return result


def is_image(file_name):
    result = False
    if file_name.split('.')[-1] == 'jpg':
        result = True
    return result


def _update_current_image_id(collection, op_type='next'):
    # TODO => add parent folder for update
    value = 1
    condition = {"class": "app"}
    class_app = collection.find_one({"class": "app"})
    images_count = collection.count_documents({"class": "image"})
    if class_app is None:
        print("init class_app")
        collection.insert_one({"class": "app", "current_image_id": 1})
    elif (class_app['current_image_id'] == 0 and op_type != 'next') or \
            (class_app['current_image_id'] == images_count and op_type == 'next'):
        value = 0
    else:
        value = 1 if op_type == 'next' else -1
    collection.update_one(condition, {'$inc': {'current_image_id': value}})
    print(class_app)


def previous_image(collection):
    _update_current_image_id(collection, "previous")


def next_image(collection):
    _update_current_image_id(collection, 'next')


def set_image(collection, image_id):
    condition = {'class': "app"}
    collection.update_one(condition, {'$set': {'current_image_id': image_id}})


def get_all_image(ssh, collection, folder_name="/mnt/hdd/dataset/leopaper301_s3"):
    # TODO => add parent folder for records
    if folder_name[-1] == '/':
        folder_name = folder_name[:-1]
    files = fetch_folder(ssh, parent_folder=folder_name)
    if files != "":
        for file in files.strip().split('\n'):
            file_name = folder_name + '/' + file
            if not file_name.__contains__('.'):
                logging.info("[*folder*] {}".format(file_name))
                get_all_image(ssh, collection, file_name)
            else:
                if is_image(file_name):
                    records = collection.count_documents({"class": "image"})
                    image_id = records if collection.find_one({"class": "app"}) else records + 1
                    logging.info("[image_id] => {}".format(image_id))
                    remote_image_info = {"class": "image", "id": image_id, "path": file_name}
                    logging.info("[file] {}".format(file_name))
                    if collection.find_one({"path": file_name}) is None:
                        logging.info("[insert] {}".format(file_name))
                        collection.insert_one(remote_image_info)
                    else:
                        logging.info("[exist] {}".format(file_name))


def show_records(collection, filter_dict):
    print("[counts] => {}".format(collection.count_documents(filter_dict)))
    for record in collection.find():
        print(record)


def main():
    hostname = os.environ.get('HOSTNAME', None)
    username = os.environ.get('USERNAME', None)
    port = os.environ.get('PORT', None)
    ssh = create_ssh_client(hostname, username, port)
    folder_name = "/mnt/hdd/dataset/leopaper301_s3"
    collection_name = "nb201-leopaper301_s3"
    collection = create_collection(my_db, collection_name)
    # get_all_image(ssh, collection, folder_name)
    set_image(collection, 100)
    show_records(collection, {"class": "image"})
    # my_db.drop_collection(collection)
    # next_image(collection)
    ssh.close()


def test_connection(client):
    stdin, stdout, stderr = client.exec_command("ls")
    print(stdout)


if __name__ == '__main__':
    main()
