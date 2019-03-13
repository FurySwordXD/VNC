from PIL import Image, ImageTk
import mss
import socket
import time
from data import SocketData
import pickle
import tkinter as tk
import time
import io
import cv2
import numpy
from threading import Thread

def screenshot():
    with mss.mss() as sct:
        img = sct.grab(sct.monitors[1])
    return rgba_to_rgb(img)

def rgba_to_rgb(im):
    return Image.frombytes('RGB', im.size, im.bgra, 'raw', 'BGRX')

def image_serializer(resolution=(1280, 720)):
    image = screenshot().resize(resolution, Image.ANTIALIAS)
    data = SocketData(image=image)
    data_string = pickle.dumps(data)
    return data_string

class Sender:
    def __init__(self, open_sockets=100):
        self.parts = open_sockets

        data_string = image_serializer()
        l = [data_string[i:i+int(len(data_string)/self.parts)] for i in range(0, len(data_string), int(len(data_string)/self.parts))]
        print(len(data_string))
        if len(l) > self.parts:
            l[-2] = l[-2] + l[-1]
            l.pop(-1)
            
        self.data = l
        for i in self.data:
            print(len(i))

    def start(self):
        for i in range(self.parts):
            port = 7000+i
            t = Thread(target=self.transmit, args=['0.0.0.0', port, i])
            t.start()

    def transmit(self, host='0.0.0.0', port=6969, part_index=0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sender:

            sender.bind((host, port))
            sender.listen()
            print('Waiting for connection on port('+ str(port) +')...')
            conn, addr = sender.accept()

            with conn:
                print('Connected by', addr)
                conn.send(str(len(self.data[part_index])).encode())
                print("Sending bytes...")
                time.sleep(0.5)
                while True:
                    conn.sendall(self.data[part_index])
                    #time.sleep(0.1)
                
if __name__ == "__main__":
    #transmit()
    s = Sender()
    s.start()