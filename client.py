import socket
import tkinter as tk
from tkinter import Canvas
from PIL import ImageTk, Image
import time
from data import SocketData, InputData
import pickle
from threading import Thread

class Receiver:

    def __init__(self, host='127.0.0.1', port=6969):
        self.data_string = ""
        self.length = 0
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiver.connect((host, port))

    def receive(self):
  
        data = self.receiver.recv(10)
        print(data.decode())
        self.length = int(data.decode())

        while True:
            #start_time = time.time()
            self.data_string = b''
            self.data_string = self.receiver.recv(self.length)

            self.image = pickle.loads(self.data_string).image


class InputManager:

    def __init__(self, host='127.0.0.1', port=7000):
        self.input = [0, 0, False, False, []]
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((host, port))
        
    def motion(self, event):
        pass
        #self.input[0], self.input[1] = event.x, event.y

    def key(self, event):
        self.input[4].append(repr(event.char))

    def left_click_pressed(self, event):
        self.input[0], self.input[1] = event.x, event.y
        self.input[2] = True

    def left_click_released(self, event):
        self.input[0], self.input[1] = event.x, event.y
        self.input[2] = False

    def right_click_pressed(self, event):
        self.input[0], self.input[1] = event.x, event.y
        self.input[3] = True

    def right_click_released(self, event):
        self.input[0], self.input[1] = event.x, event.y
        self.input[3] = False

    def transmit(self):
        while True:
            self.conn.send(str(self.input).encode())
            self.input[4] = []
            time.sleep(0.2)
        
def gui(receiver, input_manager):
    window = tk.Tk()
    window.geometry("1280x720")
    window.title("VNC Madafaka")
    
    canvas = tk.Canvas()
    canvas.bind("<Motion>", input_manager.motion)
    canvas.bind("<Key>", input_manager.key)
    canvas.bind("<ButtonPress-1>", input_manager.left_click_pressed)
    canvas.bind("<ButtonRelease-1>", input_manager.left_click_released)
    canvas.bind("<ButtonPress-2>", input_manager.right_click_pressed)
    canvas.bind("<ButtonRelease-2>", input_manager.right_click_released)
    canvas.pack(side='top', fill='both', expand='yes')
    while True:
        try:
            image = receiver.image.resize((window.winfo_width(), window.winfo_height()), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image=image)
            canvas.create_image(0, 0, image=photo, anchor='nw')
        except:
            pass
        try:
            window.update()
        except:
            exit(0)


if __name__ == "__main__":
    r = Receiver()
    #r.receive()
    th = Thread(target=r.receive, args=[])
    th.start()
    i = InputManager()
    t2 = Thread(target=i.transmit, args=[])
    t2.start()
    gui(r, i)    




