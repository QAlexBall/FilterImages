import json

import pymongo


def create_client(host='localhost', port=27017):
    client = pymongo.MongoClient('mongodb://{}:{}/'.format(host, port))
    return client


def create_collection(db, collection_name):
    if collection_name not in db.list_collection_names():
        collection = db.create_collection(collection_name)
    else:
        collection = db[collection_name]
    return collection


my_client = create_client()
my_db = my_client['mydb']


# my_collection = create_collection(my_db, 'my_collection')


def use_collection(collection_name):
    return my_db[collection_name]


def read_collection_from_config():
    config_file = open('./config.json', 'r')
    config = json.load(config_file)
    config_file.close()
    return config


def update_collection_config(path):
    config_file = open('./config.json', 'r')
    config = json.load(config_file)
    config_file.close()

    config_file = open('./config.json', 'w')
    config['current_collection'] = path
    json.dump(config, config_file, indent=4)
    config_file.close()


if __name__ == '__main__':
    my_client = create_client()
    my_db = my_client['mydb']

    # my_db.drop_collection('my_collection')
    # test_collection = create_collection(my_db, 'test_collection')
    # print(my_db.list_collection_names())
    # dic = {"test", "test_collection"}
    # test_collection.insert_one(dic)
    my_db.drop_collection('/home')
    collection_show = use_collection("/mnt/hdd/dataset/Images/CuttingBed6/local/Images/cutting1/0")
    for record in collection_show.find():
        print(record)
    print(my_db.list_collection_names())
    print(my_client.list_database_names())
