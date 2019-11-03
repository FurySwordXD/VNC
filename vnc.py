from PIL import Image
from io import BytesIO
import socket
import mss
import base64
import struct
import time

class VNC:

    def __init__(self, ip='0.0.0.0', port=7000):
        self.ip = ip
        self.port = port

    def screenshot(self):
        with mss.mss() as sct:
            img = sct.grab(sct.monitors[1])
        return self.rgba_to_rgb(img)

    def rgba_to_rgb(self, image):
        return Image.frombytes('RGB', image.size, image.bgra, 'raw', 'BGRX')

    def image_serializer(self, resolution=(1600, 900)):
        image = self.screenshot().resize(resolution, Image.ANTIALIAS)
        buffer = BytesIO()
        image.save(buffer, format='jpeg')
        data_string = base64.b64encode(buffer.getvalue())
        return data_string

    def image_deserializer(self, image_string):
        return Image.open(BytesIO(base64.b64decode(image_string)))

    def send_msg(self, sock, msg):
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + msg
        sock.sendall(msg)

    def recv_msg(self, sock):
        # Read message length and unpack it into an integer
        raw_msglen = self.recvall(sock, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return self.recvall(sock, msglen)

    def recvall(self, sock, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = b''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def transmit(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sender:
            sender.bind((self.ip, self.port))
            sender.listen()
            print('Waiting for connection...')
            conn, addr = sender.accept()
            with conn:
                print('Connected by', addr)      
                while True:
                    #start_time = time.time()
                    self.send_msg(conn, self.image_serializer())
                    #print(self.data_string)
                    #print("FPS: ", 1/(time.time() - start_time))
    
    def start_receive(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.ip, self.port))
        print("Connected to ", self.ip, ":", self.port)

    def receive(self):    
        try:
            #start_time = time.time()
            data_string = self.recv_msg(self.conn)
            return data_string.decode()
            #self.image.show()
            # print("FPS: ", 1/(time.time() - start_time))
            
        except Exception as e:
            print(e)
        return None
    