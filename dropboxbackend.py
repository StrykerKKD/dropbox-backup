import os
import uuid
import json
import shutil
import fnmatch
import tempfile
from simplecrypt import encrypt, decrypt
import dropbox
from dropbox.files import WriteMode


TOKEN = 'Insert Your Secret Token Here'
CONFIGURATION_FILE_NAME = 'configuration.json'


def get_file_paths(directory: str) -> list:
    file_paths = []
    directory_iterator = os.walk(directory)
    root, directories, files = next(directory_iterator)
    for file in files:
        file_paths.append(os.path.join(root, file))
    return file_paths


def delete_temp_storage(temp_directory: tempfile.TemporaryDirectory):
    temp_directory.cleanup()


def encrypt_file(file_path: str, password: str) -> bytes:
    file = open(file_path, mode="rb")
    encrypted_contents = encrypt(password, file.read())
    file.close()
    return encrypted_contents


def decrypt_file(file_path: str, password: str) -> bytes:
    file = open(file_path, mode="rb")
    decrypted_contents = decrypt(password, file.read())
    file.close()
    return decrypted_contents


def create_file_uuids_with_paths(file_paths: list) -> dict:
    file_uuids = {}
    for file_path in file_paths:
        file_uuids[str(uuid.uuid4())] = file_path
    return file_uuids


def read_file_with_bytes(file_path: str) -> bytes:
    with open(file_path, "rb") as file:
        contents = file.readall()
    return contents


def write_file_with_bytes(file_path: str, contents: bytes):
    with open(file_path, "wb") as file:
        file.write(contents)


def make_configuration_file(backup_directory: str, file_uuids_with_paths: dict, password: str):
    configuration_file_path = os.path.join(backup_directory, CONFIGURATION_FILE_NAME)
    configuration_contents = json.dumps(file_uuids_with_paths)
    encrypted_contents = encrypt(password, configuration_contents)
    write_file_with_bytes(configuration_file_path, encrypted_contents)


def read_configuration_file(configuration_file_path: str, password: str) -> dict:
    configuration_contents = decrypt_file(configuration_file_path, password)
    json_dict = json.loads(configuration_contents.decode())
    return json_dict


def make_backup_files(backup_directory: str, file_uuids_with_paths: dict, password: str):
    for file_uuid, file_path in file_uuids_with_paths.items():
        suffix = '__' + file_uuid + '__'
        backup_file = tempfile.NamedTemporaryFile(suffix=suffix, dir=backup_directory, delete=False)
        encrypted_contents = encrypt_file(file_path, password)
        write_file_with_bytes(backup_file.name, encrypted_contents)


def make_backup_directory(file_uuids_with_paths: dict, password: str) -> tempfile.TemporaryDirectory:
    backup_directory = tempfile.TemporaryDirectory()
    backup_directory_path = backup_directory.name
    make_backup_files(backup_directory_path, file_uuids_with_paths, password)
    make_configuration_file(backup_directory_path, file_uuids_with_paths, password)
    return backup_directory


def archive_directory(project_dir: str, temp_dir: str) -> str:
    zip_name = os.path.basename(project_dir)
    zip_path = os.path.join(tempfile.gettempdir(), zip_name)
    return shutil.make_archive(zip_path, "zip", temp_dir)


def unpack_archive(archive_file: str, extract_dir: str):
    shutil.unpack_archive(archive_file, extract_dir, "zip")


def get_configuration_file(temp_dir_path: str, password: str) -> dict:
    configuration_file_path = os.path.join(temp_dir_path, CONFIGURATION_FILE_NAME)
    configuration_file = read_configuration_file(configuration_file_path, password)
    return configuration_file


def get_backup_file_with_regex(temporary_directory_path: str, file_regex: str) -> str:
    for file in os.listdir(temporary_directory_path):
        if fnmatch.fnmatch(file, file_regex):
            return file


def restore_file(backup_file: str, file_to_restore: str, password: str):
    backup_contents = decrypt_file(backup_file, password)
    write_file_with_bytes(file_to_restore, backup_contents)


def restore_files(configuration_file: dict, temporary_directory_path: str, password: str):
    for file_uuid, file_path in configuration_file.items():
        file_regex = '*__' + file_uuid + '__'
        backup_file = get_backup_file_with_regex(temporary_directory_path, file_regex)
        backup_file_path = os.path.join(temporary_directory_path, backup_file)
        restore_file(backup_file_path, file_path, password)


def get_dropbox_api() -> dropbox.Dropbox:
    dbx = dropbox.Dropbox(TOKEN)
    return dbx


def upload_to_dropbox(file_path: str, dropbox_path: str) -> dropbox.files.FileMetadata:
    dbx = get_dropbox_api()
    with open(file_path, "rb") as file:
        file_metadata = dbx.files_upload(file.read(), dropbox_path, mode=WriteMode('overwrite'))
    return file_metadata


def download_from_dropbox(zip_path: str, dropbox_path: str) -> tuple:
    dbx = get_dropbox_api()
    return dbx.files_download_to_file(zip_path, dropbox_path)


def download_archive(directory: str, temp_dir_path: str) -> str:
    zip_path = os.path.join(temp_dir_path, directory + ".zip")
    dropbox_path = '/' + directory + ".zip"
    download_from_dropbox(zip_path, dropbox_path)
    return zip_path


def list_backups() -> list:
    dbx = get_dropbox_api()
    file_names = []
    files = dbx.files_list_folder('')
    for file in files.entries:
        file_names.append(file.name)
    return file_names


def backup(directory: str, password: str) -> dropbox.files.FileMetadata:
    file_paths = get_file_paths(directory)
    file_uuids_with_paths = create_file_uuids_with_paths(file_paths)
    backup_directory = make_backup_directory(file_uuids_with_paths, password)
    backup_directory_path = backup_directory.name
    archive_file = archive_directory(directory, backup_directory_path)
    dropbox_path = "/" + os.path.basename(archive_file)
    file_metadata = upload_to_dropbox(archive_file, dropbox_path)
    backup_directory.cleanup()
    os.remove(archive_file)
    return file_metadata


def restore(directory: str, password: str):
    temporary_directory = tempfile.TemporaryDirectory()
    temporary_directory_path = temporary_directory.name
    zip_path = download_archive(os.path.basename(directory), temporary_directory_path)
    unpack_archive(zip_path, temporary_directory_path)
    configuration_file = get_configuration_file(temporary_directory_path, password)
    restore_files(configuration_file, temporary_directory_path, password)
    temporary_directory.cleanup()
