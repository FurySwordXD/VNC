from PIL import Image
from threading import Thread
from io import StringIO
from flask import send_file
import socket
import time
import pickle
import mss
import numpy
import json
import re

class VNC:

    def __init__(self, ip='127.0.0.1', port=7000, open_sockets=5):
        self.data_string = b''
        self.ip = ip
        self.port = port

        self.open_sockets = open_sockets

    def screenshot(self):
        with mss.mss() as sct:
            img = sct.grab(sct.monitors[1])
        return self.rgba_to_rgb(img)

    def rgba_to_rgb(self, image):
        return Image.frombytes('RGB', image.size, image.bgra, 'raw', 'BGRX')

    def image_serializer(self, resolution=(200, 200)):
        image = self.screenshot().resize(resolution, Image.ANTIALIAS)
        data_string = pickle.dumps(image)
        return data_string

    def split_data(self, data_string):
        l = [data_string[i:i+int(len(data_string)/self.open_sockets)] for i in range(0, len(data_string), int(len(data_string)/self.open_sockets))]
        if len(l) > self.open_sockets:
            l[-2] = l[-2] + l[-1]
            l.pop(-1)
        return l
    
    def recvall(self, receiver, length, buffer_size=60000):
        data_buffer = b''
        while len(data_buffer) < length:
            packet, addr = receiver.recvfrom(buffer_size)
            if not packet: 
                break
            data_buffer += packet
        return data_buffer


    def transmit(self, ip, port, part_index):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        address = (ip, port)
        
        data_string = self.image_serializer()
        split_data_list = self.split_data(data_string)
        sock.sendto(str(len(split_data_list[part_index])).encode(), address)

        time.sleep(1)
        while True:
            data_string = self.image_serializer()
            split_data_list = self.split_data(data_string)
            sock.sendto(split_data_list[part_index], address)
    
    def receive(self, ip, port, part_index):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        address = (ip, port)
        sock.bind(address)
        
        data, addr = sock.recvfrom(10)
        length = int(data.decode())

        print(length)
        data_string = b""
        stride = 0
        self.data = []      
        for i in range(self.open_sockets*2):
            self.data.append([])
        while True:
            try:
                start_time = time.time()
                byte_data = self.recvall(sock, length)
                data_string += byte_data
                try:
                    self.data[stride][part_index] = data_string[:length]
                except:
                    self.data[stride].insert(part_index, data_string[:length])
                data_string = data_string[length:]

                if len(self.data[stride]) == self.open_sockets:
                    self.image = pickle.loads(b"".join(self.data[stride]))
                    self.data[stride] = []

                stride = (stride + 1)%(self.open_sockets*2)
                print("FPS: ", 1/(time.time() - start_time))
                
            except Exception as e:
                print(e)

    def start_transmit(self):
        for i in range(self.open_sockets):
            t = Thread(target=self.transmit, args=[self.ip, self.port+i, i])
            t.start()

    def start_receive(self):
        for i in range(self.open_sockets):
            t = Thread(target=self.receive, args=[self.ip, self.port+i, i])
            t.start()
                