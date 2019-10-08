# FilterImages
filter no-needed images

### Usage

```shell script
$ python remove_folder.py --help
Usage: remove_folder.py [OPTIONS]

remove folder by provided name under the parent_folder TODO: add to delete
files like [*.xml, *.py, hello* ...]

Options:
--user TEXT           username for operator cli
--parent_folder TEXT
--folder_name TEXT    Name of need_remove_folder
--help                Show this message and exit.

# remove annotated folder
python remove_folder.py --parent_folder path/to/folder --folder_name annotated
```

### FilterImage Usage
```shell script
$ mongod --dbpath=./db/data
$ =>  # initial collection => `use _update_current_image_id(collection, op_type='')` from fetch_image_info.py
$ =>  # `get_all_image(ssh, collection, folder_name)`
$ =>  # and can show records with `show_records(collection, {"class": "image"})`
```

### TODO
```
open remote folder
traverse image_name
for image_name in list(traverse(image_folder)):
  scp example@remote_host:path/to/image_name ./image_name
=> if need_delete => add image_name to need_delete_list
=> check need_delete_images
=> delete remote images which in need_delete_list
=> category images with image_name
```




