import requests
import os
import json
from boas.scripts.functions import *

def update():
    repo = grabData("settings")["repository"]

    url = f'https://api.github.com/repos/{repo}/contents/test'
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    os.makedirs("test", exist_ok=True)

    for item in data:
        if item['type'] == "file":
            file_url = item['download_url']
            file_name = item['name']
            file_path = os.path.join("test", file_name)

            response = requests.get(file_url)
            response.raise_for_status()

            with open(file_path, 'wb') as f:
                f.write(response.content)

    print("Boas update successfully installed!\nRestart to use it.")