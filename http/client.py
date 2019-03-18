from tkinter import Canvas, Tk
from PIL import Image, ImageTk
from threading import Thread
from sys import argv
import time
import requests
import numpy as np
import cv2
from input_manager import InputManager

def gui(ip, port, input_manager):

    window = Tk()
    window.geometry("1280x720")
    window.title("VNC Madafaka")
    
    window.update()
    input_manager.set_resolution(window.winfo_width(), window.winfo_height())
    input_manager.transmit()
    
    canvas = Canvas()

    window.bind("<KeyPress>", input_manager.key_pressed)
    window.bind("<KeyRelease>", input_manager.key_released)

    canvas.bind("<Motion>", input_manager.motion)
    canvas.bind("<ButtonPress-1>", input_manager.left_click_pressed)
    canvas.bind("<ButtonRelease-1>", input_manager.left_click_released)
    canvas.bind("<ButtonPress-2>", input_manager.right_click_pressed)
    canvas.bind("<ButtonRelease-2>", input_manager.right_click_released)
    canvas.pack(side='top', fill='both', expand='yes')

    url = "http://" + str(ip) + ":" + str(port)
    print(url)
    while True:
        try:
            imgResp = requests.get(url)
            imgNp = np.array(bytearray(imgResp.content),  dtype=np.uint8)
            frame = cv2.cvtColor(cv2.imdecode(imgNp, -1), cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            image = image.resize((window.winfo_width(), window.winfo_height()), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image=image)
            canvas.create_image(0, 0, image=photo, anchor='nw')
        except Exception as e:
            print(e)
        
        window.update_idletasks()
        window.update()
        input_manager.set_resolution(window.winfo_width(), window.winfo_height())

if __name__ == "__main__":  
    try:
        ip = argv[1]
    except:
        ip = "127.0.0.1"
    print(ip)
    input_manager = InputManager(ip, 6969)

    gui(ip, 7000, input_manager)




