from PIL import Image
import socket
import time
import pickle
import mss

class SocketData:
    image = []

    def __init__(self, image):
        self.image = image

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
        data = SocketData(image=image)
        data_string = pickle.dumps(data)
        return data_string


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
                self.data_string = b''
                self.data_string = conn.recv(length)
                self.image = pickle.loads(self.data_string).image
                #print(self.image)
                #self.image.show()
                #print("FPS: ", 1/(time.time() - start_time))0
            except:
                pass