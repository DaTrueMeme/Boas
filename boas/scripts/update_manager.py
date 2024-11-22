import requests
import os
import shutil
from boas.scripts.functions import *

def permissionFix(func, path, exc_info):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

def downloadContent(repo, folder_name, temp_folder_name):
    url = f'https://api.github.com/repos/{repo}/contents/{folder_name}'
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    for item in data:
        if item['type'] == 'file':
            file_url = item['download_url']
            file_name = item['name']
            file_path = os.path.join(temp_folder_name, item['path'])

            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            file_response = requests.get(file_url)
            file_response.raise_for_status()
            with open(file_path, 'wb') as f:
                f.write(file_response.content)
        elif item['type'] == 'dir':
            downloadContent(repo, item['path'], temp_folder_name)

def update(folder_name="boas"):
    temp_folder_name = f'temp_{folder_name}'
    repo = grabData("settings")["repository"]

    os.makedirs(temp_folder_name, exist_ok=True)

    downloadContent(repo, folder_name, temp_folder_name)

    try:
        shutil.rmtree(folder_name, onerror=permissionFix)
    except Exception as e:
        print(f"An error occurred while deleting the old folder: {e}")

    os.rename(temp_folder_name, f'{folder_name}_')

    print("Boas update successfully installed!\nRestart to use it.")