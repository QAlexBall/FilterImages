import click
import functools
import paramiko
from logging import info, debug, error


def create_ssh_client(hostname="192.168.13.201", username="nb201", port=22):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh.connect(hostname=hostname, port=port, username=username)
    return ssh


def fetch_folder(ssh, parent_folder="/mnt/hdd/dataset/leopaper301_s3"):
    stdin, stdout, stderr = ssh.exec_command('ls {}'.format(parent_folder))
    result = stdout.read().decode()
    return result


def main():
    ssh = create_ssh_client()
    print(fetch_folder(ssh))
    ssh.close()


main()
