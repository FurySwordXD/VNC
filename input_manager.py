import socket
import time
import pyautogui
from pynput import mouse, keyboard

class InputManager:

    def __init__(self, ip='0.0.0.0', port=6969):
        self.input = {
            "mouse_pos": [0.0, 0.0],
            "lmb": False,
            "rmb": False,
            "keys": set()
        }
        self.ip = ip
        self.port = port
        
    def set_resolution(self, width=1280, height=720):
        self.width = width
        self.height = height
        #print(self.width, self.height)

    def motion(self, event):
        self.input["mouse_pos"] = [event.x/self.width, event.y/self.height]
        self.conn.send(str(self.input).encode())
        self.conn.recv(10)

    def key_pressed(self, event):
        print("Key Press: ", repr(event.char))
        self.input["keys"].add(repr(event.char))
        self.conn.send(str(self.input).encode())
        self.conn.recv(10)
    
    def key_released(self, event):
        print("Key Released: ", repr(event.char))
        try:
            self.input["keys"].remove(repr(event.char))
        finally:
            self.conn.send(str(self.input).encode())
            self.conn.recv(10)

    def left_click_pressed(self, event):
        self.input["mouse_pos"] = [event.x/self.width, event.y/self.height]
        self.input["lmb"] = True
        self.conn.send(str(self.input).encode())
        self.conn.recv(10)

    def left_click_released(self, event):
        self.input["mouse_pos"] = [event.x/self.width, event.y/self.height]
        self.input["lmb"] = False
        self.conn.send(str(self.input).encode())
        self.conn.recv(10)

    def right_click_pressed(self, event):
        self.input["mouse_pos"] = [event.x/self.width, event.y/self.height]
        self.input["rmb"] = True
        self.conn.send(str(self.input).encode())
        self.conn.recv(10)

    def right_click_released(self, event):
        self.input["mouse_pos"] = [event.x/self.width, event.y/self.height]
        self.input["rmb"] = False
        self.conn.send(str(self.input).encode())
        self.conn.recv(10)

    def transmit(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.ip, self.port))
        print("Connected to ", self.ip, ":", self.port)
        # while True:
        #     #print(self.input["mouse_pos"])
        #     conn.send(str(self.input).encode())
        #     conn.recv(10)

    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sender:

            sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sender.bind((self.ip, self.port))
            sender.listen()
            print('Waiting for connection on port('+ str(self.port) +')...')
            conn, addr = sender.accept()

            with conn:
                print('Connected by', addr)

                width, height = pyautogui.size()
                print(width, height)
                mouse_var = mouse.Controller()
                keyboard_var = keyboard.Controller()
                last_mouse_input = [0,0]
                while True:
                    #start_time = time.time()
                    received_input = eval(conn.recv(1024).decode())
                    mouse_input = received_input["mouse_pos"]
                    mouse_input[0] = mouse_input[0] * width
                    mouse_input[1] = mouse_input[1] * height
                    #print(received_input)
                    if mouse_input != last_mouse_input:
                        mouse_var.position = tuple(mouse_input)
                        last_mouse_input = mouse_input
                        #print(received_input)
                    if received_input['lmb']:
                        #mouse_var.press(mouse.Button.left)
                        mouse_var.click(mouse.Button.left)
                        print("LMB")
                    #else:
                    #    mouse_var.release(mouse.Button.left)
                    if received_input['rmb']:
                        #mouse_var.press(mouse.Button.right)
                        mouse_var.click(mouse.Button.right)
                        print("RMB")
                    #else:
                    #    mouse_var.release(mouse.Button.right)
                    for k in received_input['keys']:
                        print(k)
                        keyboard_var.press(upper(k))
                    conn.send("ACK".encode())