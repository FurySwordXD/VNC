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

def transmit(host='0.0.0.0', port=6969):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sender:

        sender.bind((host, port))
        sender.listen()
        print('Waiting for connection...')
        conn, addr = sender.accept()

        with conn:
            print('Connected by', addr)

            data_string = image_serializer()
            print(len(data_string))
            conn.send(str(len(data_string)).encode())

            while True:
                start_time = time.time()
                conn.sendall(data_string)
                data_string = image_serializer()
                print("FPS: ", 1/(time.time() - start_time))
                
if __name__ == "__main__":
    transmit()




def compress():
    image = screenshot()
    open_cv_image = numpy.array(image)
    print(len(open_cv_image))
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
    result, encimg = cv2.imencode('.jpg', open_cv_image, encode_param)
    image = Image.fromarray(cv2.imdecode(encimg, 1))
    image.show()
    data = SocketData(image=image)
    data_string = pickle.dumps(data)
    print(len(data_string))