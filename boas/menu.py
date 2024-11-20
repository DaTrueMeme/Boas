import keyboard
import os
import json
from boas.scripts.update_manager import *
from boas.scripts.functions import *

class BoasMenu:
    def __init__(self) -> None:
        self.menu_open = False
        self.menu_length = 0
        self.current_page = "home"
        self.last_page = "home"

        self.latest_version = checkLatestVersion().removesuffix("\n")
        self.version = grabData("settings")["version"]

        self.select_mode = grabData("settings")["arrow_selection"]

        self.entered = False

        self.action = None

        self.cursor_position = 0

    def setSetting(self, setting, value):
        with open(f'boas/data/settings.json', "r", encoding="utf-8") as f:
            data = json.load(f)

        data[setting] = value

        with open(f'boas/data/settings.json', "w", encoding="utf-8") as f:
            json.dump(data, f)
        
        self.cursor_position = 0
        self.render()

    def getSetting(self, setting):
        with open(f'boas/data/settings.json', "r", encoding="utf-8") as f:
            data = json.load(f)

        return data[setting]

    def renderMessage(self, message):
        with open(f'boas/data/messages/{message}.txt', "r", encoding="utf-8") as f:
            for line in f:
                print(line.removesuffix("\n"))

    def switchPage(self, page):
        self.last_page = self.current_page
        self.cursor_position = 0
        self.current_page = page
        self.render()

    def checkEnter(self):
        if keyboard.is_pressed("enter"):
            if not self.entered:
                self.entered = True
                return True
        else:
            self.entered = False
            return False

    def exit(self):
        self.menu_open = False

    def checkInteract(self, index=0):
        if self.select_mode == True:
            if self.checkEnter() and self.cursor_position == index:
                return True
            return False
        else:
            if self.action == str(index):
                self.action = None
                return True
            return False

    def renderPage(self, page):
        with open(f'boas/data/pages/{page}.json', "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f'----- {data["title"]} -----')

        self.menu_length = len(data["content"]) + 1

        index = 0
        actions = None
        for content in data["content"]:
            if index == 0:
                print(f'{"> " if self.cursor_position == index and self.select_mode else "  "}')
                index += 1

            if content["type"] == "toggle":
                print(f'{"> " if self.cursor_position == index and self.select_mode else "  "}{f"{index} " if not self.select_mode else ""}{content["label"]}: {self.getSetting(content["change"])}')
                actions = content["actions"]

                if self.checkInteract(index):
                    if actions != None:
                        if actions == []:
                            print("Action is empty.")
                            index += 1
                            continue

                        for action in actions:
                            add = 1 if self.getSetting(content["change"]) == content["states"][0] else -1
                            index = content["states"].index(self.getSetting(content["change"])) + add
                            value = content["states"][index]
                            exec(action)

            if content["type"] == "button":
                print(f'{"> " if self.cursor_position == index and self.select_mode else "  "}{f"{index} " if not self.select_mode else ""}{content["label"]}')
                actions = content["actions"]

                if self.checkInteract(index):
                    if actions != None:
                        if actions == []:
                            print("Action is empty.")
                            index += 1
                            continue

                        for action in actions:
                            exec(action)

            index += 1

    def render(self):
        os.system("cls" if os.name == "nt" else "clear")
        self.renderMessage("welcome")

        if self.version < self.latest_version:
            self.renderMessage("update")

        self.renderPage(self.current_page)

    def open(self):
        self.menu_open = True
        self.render()
        print(self.select_mode)
        
        while self.menu_open:
            if self.select_mode == True:
                event = keyboard.read_event()

                if keyboard.is_pressed("down"):
                    self.cursor_position += 1 if self.cursor_position < self.menu_length - 1 else 0
                if keyboard.is_pressed("up"):
                    self.cursor_position -= 1 if self.cursor_position > 0 else 0

                if event.event_type == "down":
                    self.render()
            else:
                self.render()
                if self.menu_open:
                    self.action = input()
BoasMenu = BoasMenu()
BoasMenu.open()