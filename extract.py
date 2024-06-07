import os
import shutil
import sqlite3
from utils import decrypt_password, convert_chrome_time
import logging

def get_data(path: str, profile: str, key, type_of_data):
    db_file = f'{path}\\{profile}{type_of_data["file"]}'
    if not os.path.exists(db_file):
        logging.warning(f"Database file does not exist: {db_file}")
        return None

    result = ""

    try:
        shutil.copy(db_file, 'temp_db')
    except PermissionError as e:
        logging.error(f"Permission Error: {e}")
        return result

    try:
        conn = sqlite3.connect('temp_db')
        cursor = conn.cursor()
        cursor.execute(type_of_data['query'])
        for row in cursor.fetchall():
            row = list(row)
            if type_of_data['decrypt']:
                for i in range(len(row)):
                    if isinstance(row[i], bytes):
                        row[i] = decrypt_password(row[i], key)
            if type_of_data['file'] == '\\History':
                if row[2] != 0:
                    row[2] = convert_chrome_time(row[2])
                else:
                    row[2] = "0"
            result += "\n".join([f"{col}: {val}" for col, val in zip(type_of_data['columns'], row)]) + "\n\n"
        conn.close()
        os.remove('temp_db')
        logging.info(f"Data extraction for {type_of_data['file']} completed successfully")
        return result
    except Exception as e:
        logging.error(f"Error extracting data from {db_file}: {e}")
        return result
