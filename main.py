# audit_script.py

import os
import json
from cryptography.fernet import Fernet
from supabased import create_supabase_client, Client, check_if_data_exists_on_supbase, BUCKET
import zipfile
from datetime import datetime
from storage3.utils import StorageException
import uuid

# Supabase bucket
bucket = BUCKET

def check_if_directory_exists(directory_name):
    """Check if a directory exists.

    Args:
        directory_name (str): The name of the directory to check.

    Returns:
        bool: True if the directory exists, False otherwise.
    """
    if os.path.isdir(f'./{directory_name}'):
        return True
    return False

def read_directory(path, ignores=['.git', '.DS_Store']):
    """Read the contents of a directory, excluding specified files and directories.

    Args:
        path (str): The path of the directory to read.
        ignores (list): List of files/directories to ignore during the reading process.

    Returns:
        tuple: A tuple containing a list of file entries and the total number of files.
    """
    entries = []
    amountOfFiles = 0
    for root, dirs, files in os.walk(path):
        for filename in files:
            file_path = os.path.join(root, filename)

            if any(ignore in file_path for ignore in ignores):
                continue

            entry = {'filename': filename, 'path': file_path}
            entries.append(entry)
            amountOfFiles += 1
    return entries, amountOfFiles

def create_directory_audit(directory, ignores=['.git', '.DS_Store']):
    """Create an audit of a directory by reading its contents.

    Args:
        directory (str): The path of the directory to audit.
        ignores (list): List of files/directories to ignore during the audit.

    Returns:
        tuple: A tuple containing the audit result (list of file entries) and the total number of files.
    """
    entry, amountOfFiles = read_directory(directory, ignores)
    audit_result = [entry]
    audit = {'audit': audit_result}
    return audit, amountOfFiles

def check_if_audit_exists_on_supbase(supaClient):
    """Check if an audit exists on Supabase.

    Args:
        supaClient: The Supabase client.

    Returns:
        bool: True if the audit exists, False otherwise.
    """
    thing = supaClient.table('directory_audits').select("*").eq("name", 'test').execute()

    if len(thing.data) > 0:
        return True
    
    return False

def create_zip_of_directory(directory_name):
    """Create a zip file of a directory.

    Args:
        directory_name (str): The name of the directory to zip.
    """
    zipf = zipfile.ZipFile(f'{directory_name}.zip', 'w', zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(f'./{directory_name}'):
        for file in files:
            zipf.write(os.path.join(root, file))

    zipf.close()

def create_password_protected_zip_of_directory(directory_name):
    """Create a password-protected zip file of a directory.

    Args:
        directory_name (str): The name of the directory to zip.
    """
    # TO BE IMPLEMENTED
    pass

def upload_zip_to_supabase(supaClient, directory_name):
    """Upload a zip file to Supabase storage.

    Args:
        supaClient: The Supabase client.
        directory_name (str): The name of the directory.
    """
    try:
        with open(f'{directory_name}.zip', 'rb') as file:
            supaClient.storage.from_(bucket).upload(f'{directory_name}.zip', file)
    except StorageException as e:
        print(e)
        print('Error uploading to Supabase')
        shouldIContinue = input('Do you want to continue? (y/n) ')
        if shouldIContinue == 'y':
            with open(f'{directory_name}.zip', 'rb') as file:
                supaClient.storage.from_(bucket).upload(f'{directory_name}-{uuid.uuid4()}.zip', file)
        else:
            print('Exiting')
            exit()

def get_audit_from_supabase(supaClient, directory_name):
    """Retrieve an audit from Supabase.

    Args:
        supaClient: The Supabase client.
        directory_name (str): The name of the directory.

    Returns:
        dict: The retrieved audit data.
    """
    thing = supaClient.table('directory_audits').select("*").eq("name", directory_name).execute()
    return thing.data[0]

def save_json_pretty(directory_name, output):
    """Save JSON output to a file in a pretty format.

    Args:
        directory_name (str): The name of the directory.
        output (dict): The JSON output to save.
    """
    with open(f'{directory_name}_output.json', 'w') as outfile:
        json.dump(output, outfile, indent=4)

def download_zip_from_supabase(supaClient, directory_name):
    """Download a zip file from Supabase storage.

    Args:
        supaClient: The Supabase client.
        directory_name (str): The name of the directory.
    """
    with open(f'./{directory_name}.zip', 'wb+') as f:
        res = supaClient.storage.from_('test').download(f'{directory_name}.zip')
        f.write(res)

def extract_zip_to_directory(directory_name):
    """Extract the contents of a zip file to a directory.

    Args:
        directory_name (str): The name of the directory.
    """
    with zipfile.ZipFile(f'./{directory_name}.zip', 'r') as zip_ref:
        print('Extracting...')
        zip_ref.extractall()

def open_and_extract_the_supabase_zip(directory_name):
    """Download and extract the contents of a zip file from Supabase.

    Args:
        directory_name (str): The name of the directory.
    """
    download_zip_from_supabase(supaClient, directory_name)
    extract_zip_to_directory(directory_name)

if __name__ == "__main__":
    supaClient = create_supabase_client()
    directory_name = input('Enter directory name: ')

    if not check_if_directory_exists(directory_name):
        print('Folder does not exist')
        exit()

    create_zip_of_directory(directory_name)
    upload_zip_to_supabase(supaClient, directory_name)
    audit, amountOfFiles = create_directory_audit(f'./{directory_name}')

    output = {
        'name': directory_name,
        "filechain": audit,
        "amountOfFiles": amountOfFiles,
        "bucket": directory_name + '.zip'
    }

    supaClient.table("directory_audits").insert(output).execute()

    # save to json file nice and pretty
    save_json_pretty(directory_name, output)
    print('Finished downloading.')
