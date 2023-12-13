import os
import json
from cryptography.fernet import Fernet
from supabased import create_supabase_client, Client, check_if_data_exists_on_supbase, BUCKET
import zipfile
from datetime import datetime
from storage3.utils import StorageException
import uuid

bucket = BUCKET

def check_if_directory_exists(directory_name):
    if os.path.isdir(f'./{directory_name}'):
        return True
    return False

def read_directory(path, ignores = ['.git', '.DS_Store']):
    entries = []
    amountOfFiles = 0
    for root, dirs, files in os.walk(path):
        for filename in files:
            file_path = os.path.join(root, filename)

            if any(ignore in file_path for ignore in ignores):
                continue

            entry = {'filename': filename, 'path': file_path }
            entries.append(entry)
            amountOfFiles += 1
    return entries, amountOfFiles

def create_directory_audit(directory, ignores = ['.git', '.DS_Store']):
    entry, amountOfFiles = read_directory(directory, ignores)
    audit_result = [entry]
    audit = {'audit': audit_result}
    return audit, amountOfFiles

def check_if_audit_exists_on_supbase(supaClient): 
    thing = supaClient.table('directory_audits').select("*").eq("name", 'test').execute()

    if len(thing.data) > 0:
        return True
    
    return False

def create_zip_of_directory(directory_name):
    # create a zip of a directory
    zipf = zipfile.ZipFile(f'{directory_name}.zip', 'w', zipfile.ZIP_DEFLATED)

    # replace directory into zip
    for root, dirs, files in os.walk(f'./{directory_name}'):
        for file in files:
            zipf.write(os.path.join(root, file))

    zipf.close()

def create_password_protected_zip_of_directory(directory_name):
    return 'TO_BE_IMPLEMENTED'

def upload_zip_to_supabase(supaClient, directory_name):
    try:
        with open(f'{directory_name}.zip', 'rb') as file:
             supaClient.storage.from_(bucket).upload(f'{directory_name}.zip', file)
    except StorageException as e:
        print(e)
        print('Error uploading to supabase')
        shouldIContinue = input('Do you want to continue? (y/n) ')
        if shouldIContinue == 'y':
            with open(f'{directory_name}.zip', 'rb') as file:
                supaClient.storage.from_(bucket).upload(f'{directory_name}-{uuid.uuid4()}.zip', file)
        else:
            print('Exiting')
            exit()

def get_audit_from_supabase(supaClient, directory_name):
    thing = supaClient.table('directory_audits').select("*").eq("name", directory_name).execute()
    return thing.data[0]

def save_json_pretty(directory_name, output):
    with open(f'{directory_name}_output.json', 'w') as outfile:
        json.dump(output, outfile, indent=4)

def download_zip_from_supabase(supaClient, directory_name):
    with open(f'./{directory_name}.zip', 'wb+') as f:
        res = supaClient.storage.from_('test').download(f'{directory_name}.zip')
        f.write(res)

def extract_zip_to_directory(directory_name):
    with zipfile.ZipFile(f'./{directory_name}.zip', 'r') as zip_ref:
        print('extracting')
        zip_ref.extractall()

def open_and_extract_the_supabase_zip(directory_name):
    download_zip_from_supabase(supaClient, directory_name)
    extract_zip_to_directory(directory_name)

if __name__ == "__main__":
    supaClient = create_supabase_client()
    directory_name = input('Enter directory name: ')

    if (check_if_directory_exists(directory_name)) == False:
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

    # # save to json file nice and pretty
    save_json_pretty(directory_name, output)
    print('finished downloading')
