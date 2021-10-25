import pickle
from datetime import datetime

import keyboard
import mouse
import pandas as pd
from PySide2.QtCore import QEvent
from PySide2.QtGui import QMoveEvent, QResizeEvent
from PySide2.QtWidgets import QMainWindow

from tkinter import END, Button, Entry, Text, Tk, filedialog


class MouseLogger:
    def __init__(self, window: QMainWindow):
        self.window = window
        self.active_times = pd.DataFrame()
        self.start_active = None

        self.mouse_events = []

        mouse.hook(self.mouse_events.append)
        keyboard.start_recording()  # Starting the recording

        keyboard.add_hotkey("ctrl+ü", self.stop_logging)

        self.master = Tk()
        self.text_box = Text(self.master)
        # self.text_box.grid(row=0)
        self.text_box.pack()

        e = Entry(self.master)
        #        e.grid(row=0, column=1)

        btn_ok = Button(self.master, text="OK", command=self.handle_mode)
        btn_ok.pack()

        self.master.mainloop()

    def handle_mode(self):
        self.mode = self.text_box.get("1.0", END)
        self.save_file_directory = filedialog.askdirectory()
        self.master.destroy()

    def move_event(self, event: QMoveEvent):
        # only for the study we record if the window was moved
        # print("TODO: trigger changeEvent")
        self._add_change("move")

    def resize_event(self, event: QResizeEvent):
        self._add_change("resize")

    def change_event(self, event: QEvent):
        # only for the study we record when the window is active
        if self.window.isHidden():
            return
        print(self.window.children())
        if self.window.isActiveWindow():
            self.start_active = datetime.now().timestamp()
        else:
            self._add_change("active")

    def stop_logging(self):
        self._add_change("active")

        mouse.unhook(self.mouse_events.append)
        keyboard_events = keyboard.stop_recording()

        from pathlib import Path

        here = Path(__file__).absolute().parent
        print(here)

        self.mode = self.mode.replace("\n", "")

        with open(str(Path(self.save_file_directory) / f"{self.mode}_mouse_events.pkl"), "wb") as f:
            pickle.dump(self.mouse_events, f)

        with open(str(Path(self.save_file_directory) / f"{self.mode}_window_positions.pkl"), "wb") as f:
            pickle.dump(self.active_times, f)

    def _add_change(self, description: str):
        if description in ["move", "resize"]:
            start = None
        else:
            start = self.start_active
        df = pd.DataFrame(
            data=[
                [
                    start,
                    datetime.now().timestamp(),
                    self.window.pos().x(),
                    self.window.pos().y(),
                    self.window.size().width(),
                    self.window.size().height(),
                    description,
                ]
            ],
            columns=["start", "stop", "pos_x", "pos_y", "width", "height", "event_description"],
        )
        self.active_times = self.active_times.append(df)
        print(self.active_times)
