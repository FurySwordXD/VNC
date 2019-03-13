from PIL import Image
import socket
import time
import pickle
import mss
import numpy
import json

class VNC:

    def __init__(self, ip='127.0.0.1', port=6969):
        self.data_string = b''
        self.ip = ip
        self.port = port

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


    def recvall(self, receiver, buffer_size=65536):
        data_buffer = []
        while True:
            packet = receiver.recv(4096)
            if not packet: break
            data_buffer.append(packet)

        return b"".join(data_buffer)

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
                    #start_time = time.time()
                    conn.sendall(self.data_string)
                    self.data_string = self.image_serializer()
                    #print("FPS: ", 1/(time.time() - start_time))
    
    def receive(self):    
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((self.ip, self.port))
        print("Connected to ", self.ip, ":", self.port)

        data = conn.recv(10)
        print(data.decode())
        length = int(data.decode())

        while True:
            try:
                #start_time = time.time()
                #self.data_string = b''
                self.data_string = self.recvall(conn)
                #self.data_string = conn.recv(length)
                self.image = pickle.loads(self.data_string[:length])
                #self.image.show()
                #print(self.image)
                # self.image.show()
                #print("FPS: ", 1/(time.time() - start_time))0
            except Exception as e:
                print(e)