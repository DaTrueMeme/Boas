import json
import requests

def grabData(path):
    file_path = f'boas/data/{path}.json'
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def checkLatestVersion():
    url = f'https://raw.githubusercontent.com/{grabData("settings")["repository"]}/refs/heads/main/version.txt'
    response = requests.get(url)

    if response.status_code == 200:
        version = response.text
        return version
    else:
        return "Failed to fetch version."