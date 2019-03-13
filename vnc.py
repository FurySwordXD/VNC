from PIL import Image
from threading import Thread
import socket
import time
import pickle
import mss
import numpy
import json
import re

class VNC:

    def __init__(self, ip='127.0.0.1', port=7000, open_sockets=4):
        self.data_string = b''
        self.ip = ip
        self.port = port
        self.open_sockets = open_sockets
        self.data = []
        for i in range(open_sockets):
            self.data.append([])

    def screenshot(self):
        with mss.mss() as sct:
            img = sct.grab(sct.monitors[1])
        return self.rgba_to_rgb(img)

    def rgba_to_rgb(self, image):
        return Image.frombytes('RGB', image.size, image.bgra, 'raw', 'BGRX')

    def image_serializer(self, resolution=(1280, 720)):
        image = self.screenshot().resize(resolution, Image.ANTIALIAS)
        #np_image = numpy.array(image)
        data_string = pickle.dumps(image)
        #print("Start")
        #data_string = "["
        #for row in np_image:
        #    data_string += "["
        #    for column in row:
        #        data_string += str(column)
        #    data_string += "]"
        #data_string += "]"
        return data_string


    def recvall(self, receiver, length, buffer_size=65536):
        data_buffer = b''
        while len(data_buffer) < length:
            packet = receiver.recv(buffer_size)
            if not packet: break
            data_buffer += packet
        return data_buffer

    def transmit(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sender:
            sender.bind((self.ip, self.port))
            sender.listen()
            print('Waiting for connection...')
            conn, addr = sender.accept()
            with conn:
                print('Connected by', addr)

                self.data_string = self.image_serializer()
                print(len(self.data_string))
                conn.send(str(len(self.data_string)).encode())

                while True:
                    start_time = time.time()
                    conn.sendall(self.data_string)
                    self.data_string = self.image_serializer()
                    #print(conn.recv(10).decode())
                    print("FPS: ", 1/(time.time() - start_time))
    
    def receive(self):    
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((self.ip, self.port))
        print("Connected to ", self.ip, ":", self.port)

        data = conn.recv(10)
        print(data.decode())
        length = int(data.decode())

        while True:
            try:
                start_time = time.time()
                #self.data_string = b''
                self.data_string += self.recvall(conn, length)
                #self.data_string = conn.recv(length)
                self.image = pickle.loads(self.data_string[:length])
                self.data_string = self.data_string[length:]
                #conn.send("Received".encode())
                print("FPS: ", 1/(time.time() - start_time))
            except Exception as e:
                print(e)


    def split_data(self, data_string):
        l = [data_string[i:i+int(len(data_string)/self.open_sockets)] for i in range(0, len(data_string), int(len(data_string)/self.open_sockets))]
        if len(l) > self.open_sockets:
            l[-2] = l[-2] + l[-1]
            l.pop(-1)
        return l

    def transmit_multi(self, ip='0.0.0.0', port=7000, part_index=0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sender:

            sender.bind((ip, port))
            sender.listen()
            print('Waiting for connection on port('+ str(port) +')...')
            conn, addr = sender.accept()

            with conn:
                print('Connected by', addr)

                data_string = self.image_serializer()
                self.split_data_list = self.split_data(data_string) 
                print(len(self.split_data_list[part_index]))
                conn.send(str(len(self.split_data_list[part_index])).encode())

                time.sleep(1)
                #print("Sending bytes...")
                while True:
                    if part_index == 0:
                        data_string = self.image_serializer()
                        self.split_data_list = self.split_data(data_string)
                    try: 
                        conn.sendall(self.split_data_list[part_index])
                        print(conn.recv(20).decode())
                    except Exception as e:
                        print(e)
                    
    def receive_multi(self, ip='127.0.0.1', port=7000, part_index=0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as receiver:
            
            receiver.connect((ip, port))

            length = int(receiver.recv(10).decode())
            print(length)
            
            stride = 0
            byte_data = b''
            while True:
                byte_data += self.recvall(receiver, length)
                self.data[stride].insert(part_index, byte_data[:length])
                byte_data = byte_data[length:]
                #print("Thread ("+str(part_index)+"): ", len(self.data[stride]))
                try:
                    if len(self.data[stride]) == self.open_sockets:
                        self.image = pickle.loads(b"".join(self.data[stride]))
                        self.data[stride] = []
                except Exception as e:
                    print(e)
                    self.data[stride] = []

                stride += 1
                if stride == self.open_sockets:
                    stride = 0
                
                receiver.send("Received".encode())

    def start_transmit(self):
        for i in range(self.open_sockets):
            t = Thread(target=self.transmit_multi, args=[self.ip, self.port+i, i])
            t.start()

    def start_receive(self):
        for i in range(self.open_sockets):
            t = Thread(target=self.receive_multi, args=[self.ip, self.port+i, i])
            t.start()