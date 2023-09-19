#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# data_update.py - Neurainodes Website Data Updater.
#
# By Jeroz, 2019
#
# Code Adapted from Michael Cho:
# https://www.michaelcho.me/article/using-pythons-watchdog-to-monitor-changes-to-a-directory
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
Data change watcher

Usage:
    ./data_update.py FULL_PATH_TO_FOLDER
"""

import time
import sys
import os
import pandas as pd
from utils import parse_data
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Param:
    json_data = []
    WATCH = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath('.')
    OUTPUT = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.abspath('.')


def initialize():
    print("Initializing...")
    print('reading all JSON files from: ' + Param.WATCH)
    Param.json_data = parse_data(Param.WATCH, Param.OUTPUT, Param.json_data, [], init=True)
    print("Done.")


class Watcher:
    """
    Folder change watcher
    """
    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, Param.WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):
    """
    Folder change handler
    """

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)
            if event.src_path.endswith('.json'):
                try:
                    df = pd.read_json(event.src_path)
                    if len(df) == 0:
                        print("Data point is empty. Removing data point...")
                        os.remove(event.src_path)
                except:
                    print("Corrupted json file. Removing data point...")
                    os.remove(event.src_path)
                else:
                    print("Updating data...")
                    Param.json_data = parse_data(Param.WATCH, Param.OUTPUT, Param.json_data, event.src_path, init=False)
                    print("Reloading Supervisor...")
                    os.system('sudo service supervisor reload')


            else:
                print("Ignoring")


if __name__ == '__main__':
    initialize()
    w = Watcher()
    w.run()
