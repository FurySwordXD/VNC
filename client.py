from tkinter import Canvas, Tk
from PIL import Image, ImageTk
from threading import Thread
from sys import argv

from input_manager import InputManager
from vnc import VNC

if __name__ == "__main__":
    
    try:
        ip = argv[1]
    except:
        ip = "127.0.0.1"
    print(ip)

    client = VNC(ip, 7000)
    input_manager = InputManager(ip, 6969)

    window = Tk()
    window.geometry("1280x720")
    window.title("VNC")
    canvas = Canvas()
    canvas.pack(side='top', fill='both', expand='yes')
    window.update()
    input_manager.set_resolution(window.winfo_width(), window.winfo_height())
    input_manager.transmit()

    window.bind("<KeyPress>", input_manager.key_pressed)
    window.bind("<KeyRelease>", input_manager.key_released)

    canvas.bind("<Motion>", input_manager.motion)
    canvas.bind("<ButtonPress-1>", input_manager.left_click_pressed)
    canvas.bind("<ButtonRelease-1>", input_manager.left_click_released)
    canvas.bind("<ButtonPress-2>", input_manager.right_click_pressed)
    canvas.bind("<ButtonRelease-2>", input_manager.right_click_released)


    client.start_receive()

    while True:

        image = client.receive()
        if image:
            image = image.resize((window.winfo_width(), window.winfo_height()), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image=image)
            canvas.create_image(0, 0, image=photo, anchor='nw')
            window.update_idletasks()
            window.update()




