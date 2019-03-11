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
from pynput.mouse import Controller, Button
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
                #start_time = time.time()
                conn.sendall(data_string)
                data_string = image_serializer()
                
                #print("FPS: ", 1/(time.time() - start_time))

def recveive_input(host='0.0.0.0', port=7000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sender:

        sender.bind((host, port))
        sender.listen()
        print('Waiting for connection...')
        conn, addr = sender.accept()

        with conn:
            print('Connected by', addr)

            mouse = Controller()
            last_mouse_input = [0,0]
            while True:
                #start_time = time.time()
                received_input = list(eval(conn.recv(100).decode()))
                mouse_input = [received_input[0]] + [received_input[1]]
                mouse_input[0] = mouse_input[0]/1280 * 1920
                mouse_input[1] = mouse_input[1]/720 * 1080
                #print(received_input)
                if mouse_input != last_mouse_input:
                    mouse.position = tuple(mouse_input)
                    last_mouse_input = mouse_input
                if received_input[2]:
                    mouse.press(Button.left)
                else:
                    mouse.release(Button.left)
                if received_input[3]:
                    mouse.press(Button.right)
                else:
                    mouse.release(Button.right)
        
if __name__ == "__main__":
    t1 = Thread(target=transmit, args=[])
    t2 = Thread(target=recveive_input, args=[])
    t1.start()
    t2.start()



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