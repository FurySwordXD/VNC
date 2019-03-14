import socket
import time
import pyautogui
from pynput.mouse import Controller, Button


class InputManager:

    def __init__(self, ip='0.0.0.0', port=6969):
        self.input = {
            "mouse_pos": [0.0, 0.0],
            "lmb": False,
            "rmb": False,
            "keys": []
        }
        self.ip = ip
        self.port = port
        
    def set_resolution(self, width=1280, height=720):
        self.width = width
        self.height = height
        #print(self.width, self.height)

    def motion(self, event):
        #self.input["mouse_pos"] = [event.x, event.y]
        pass

    def key(self, event):
        print(repr(event.char))
        self.input["keys"].append(repr(event.char))

    def left_click_pressed(self, event):
        self.input["mouse_pos"] = [event.x/self.width, event.y/self.height]
        self.input["lmb"] = True

    def left_click_released(self, event):
        self.input["mouse_pos"] = [event.x/self.width, event.y/self.height]
        self.input["lmb"] = False

    def right_click_pressed(self, event):
        self.input["mouse_pos"] = [event.x/self.width, event.y/self.height]
        self.input["rmb"] = True

    def right_click_released(self, event):
        self.input["mouse_pos"] = [event.x/self.width, event.y/self.height]
        self.input["rmb"] = False

    def transmit(self):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((self.ip, self.port))
        print("Connected to ", self.ip, ":", self.port)
        while True:
            conn.send(str(self.input).encode())
            self.input["keys"] = []
            conn.recv(10)

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
                mouse = Controller()
                last_mouse_input = [0,0]
                while True:
                    #start_time = time.time()
                    received_input = eval(conn.recv(1024).decode())
                    mouse_input = received_input["mouse_pos"]
                    mouse_input[0] = mouse_input[0] * width
                    mouse_input[1] = mouse_input[1] * height
                    #print(received_input)
                    if mouse_input != last_mouse_input:
                        mouse.position = tuple(mouse_input)
                        last_mouse_input = mouse_input
                        print(received_input)
                    #if received_input[2]:
                    #    mouse.press(Button.left)
                    #else:
                    #    mouse.release(Button.left)
                    #if received_input[3]:
                    #    mouse.press(Button.right)
                    #else:
                    #    mouse.release(Button.right)
                    conn.send("ACK".encode())