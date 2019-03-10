import socket
import tkinter as tk
from tkinter import Canvas
from PIL import ImageTk, Image
import time
from data import SocketData
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
            try:
                self.image = pickle.loads(self.data_string).image
            except Exception as e:
                print(e)
            #print("FPS: ", 1/(time.time() - start_time))

def gui(receiver):
    window = tk.Tk()
    window.geometry("1280x720")
    window.title("VNC Madafaka")
    cv = tk.Canvas()
    cv.pack(side='top', fill='both', expand='yes')

    while True:
        try:
            image = receiver.image.resize((window.winfo_width(), window.winfo_height()), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image=image)
            cv.create_image(0, 0, image=photo, anchor='nw')
        except:
            pass
        window.update()


if __name__ == "__main__":
    r = Receiver()
    #r.receive()

    th = Thread(target=r.receive, args=[])
    th.start()
    gui(r)    

