#!/usr/bin/env python

import threading, time

def thread1():
    global key
    lock = threading.Lock()
    while True:
        with lock:
            key = input()

threading.Thread(target = thread1).start()

while True:
    time.sleep(1)
    print(key)