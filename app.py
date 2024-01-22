import sys
import ui
from PyQt6.QtWidgets import QApplication
from data import VitaminDTracker, UserData
from time import sleep


class Controller:
    def __init__(self):
        self.tracker = VitaminDTracker()
        self.app = QApplication([])
        self.sensor_data = []
        self.items = []
        self.curr = 0
        self.user_data = UserData()

        self.button_callbacks = {
            "settings": self.on_click_settings,
            "log": self.on_click_log,
            "back": self.on_click_back,
            # "sensor": self.onClickSensor,
        }

        self.window = ui.MainWindow(self.user_data, self.tracker, self.button_callbacks)
        self.window.sensor_data = self.sensor_data

    def task(self):
        self.items.extend(list(range(0, 20)))
        self.curr = 19

        while True:
            print(self.items)
            self.items.append(self.curr)
            self.curr += 1

            sleep(2)

    def start(self):
        self.window.show()

        exit_code = self.app.exec()
        self.tracker.backup()

        sys.exit(exit_code)

    def on_click_settings(self):
        print("settings!")
        self.window.change_view("settings")

    def on_click_log(self):
        print("log!")
        self.window.change_view("log")

    def on_click_back(self):
        print("back!")
        self.window.change_view("main")

    def on_click_sensor(self):
        print("sensor!")
        self.window.change_view("sensor")


if __name__ == "__main__":
    Controller().start()
