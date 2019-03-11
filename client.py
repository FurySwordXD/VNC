import socket
import tkinter as tk
from tkinter import Canvas
from PIL import ImageTk, Image
import time
from data import SocketData, InputData
import pickle
from threading import Thread
from pynput.mouse import Listener

class Receiver:

    def __init__(self, host='127.0.0.1', port=6969):
        self.data_string = ""
        self.length = 0
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiver.connect((host, port))
        self.mouse_pos = (0,0)
    
    def on_move(self, x, y):
        self.mouse_pos = (x, y)

    def on_click(self, x, y, button, pressed):
        pass
        #print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))

    def on_scroll(self, x, y, dx, dy):
        pass
        #print('Scrolled {0}'.format((x, y)))

    def receive(self):
  
        data = self.receiver.recv(10)
        print(data.decode())
        self.length = int(data.decode())

        while True:
            #start_time = time.time()
            self.data_string = b''
            self.data_string = self.receiver.recv(self.length)

            self.image = pickle.loads(self.data_string).image

            #data = InputData(mouse_pos=self.mouse_pos)
            #data = pickle.dumps(data)
            #input_length = len(data)
            self.receiver.send(str(self.mouse_pos).encode())
            #self.receiver.send(pickle.dumps(data))
            #print("FPS: ", 1/(time.time() - start_time))

    def motion(self, event):
        self.mouse_pos = (event.x, event.y)

def gui(receiver):
    window = tk.Tk()
    window.geometry("1280x720")
    window.title("VNC Madafaka")
    window.bind('<Motion>', receiver.motion)
    cv = tk.Canvas()
    cv.pack(side='top', fill='both', expand='yes')

    while True:
        try:
            image = receiver.image.resize((window.winfo_width(), window.winfo_height()), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image=image)
            cv.create_image(0, 0, image=photo, anchor='nw')
        except:
            pass
        try:
            window.update()
        except:
            exit(0)




# Collect events until released

if __name__ == "__main__":
    r = Receiver()
    #r.receive()

    th = Thread(target=r.receive, args=[])
    th.start()
    #listener = Listener(on_move=r.on_move, on_click=r.on_click, on_scroll=r.on_scroll)
    #listener.start()
    gui(r)    




