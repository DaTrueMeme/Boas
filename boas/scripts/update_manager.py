import requests
import os
from boas.scripts.functions import *

def update(folder_name="boas"):
    repo = grabData("settings")["repository"]

    url = f'https://api.github.com/repos/{repo}/contents/{folder_name}'
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    os.makedirs(folder_name, exist_ok=True)

    for item in data:
        if item['type'] == "file":
            file_url = item['download_url']
            file_name = item['name']
            file_path = os.path.join(folder_name, file_name)

            response = requests.get(file_url)
            response.raise_for_status()

            with open(file_path, 'wb') as f:
                f.write(response.content)

    print("Boas update successfully installed!\nRestart to use it.")