# FilterImages
filter no-needed images

### Usage

```shell
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
