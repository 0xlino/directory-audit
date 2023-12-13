import supabase
from supabase import create_client, Client
from cryptography.fernet import Fernet
import os

def get_env_value(key):
    try:
        return os.environ[key]
    except KeyError:
        return 'there is no such key'

SUPABASE_URL = get_env_value('SUPABASE_URL_DIRECTORY_AUDIT')
SUPABASE_KEY_SERVICE = get_env_value('SUPABASE_KEY_SERVICE_DIRECTORY_AUDIT')
BUCKET = get_env_value('BUCKET_DIRECTORY_AUDIT')

def create_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY_SERVICE)

def encrypt(message: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(message)

def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)

def check_if_data_exists_on_supbase(supaClient, table_name, column_name, column_value): 
    thing = supaClient.table(table_name).select("*").eq(column_name, column_value).execute()

    if len(thing.data) > 0:
        return True
    
    return False