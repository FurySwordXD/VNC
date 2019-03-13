import socket
import time
from pynput.mouse import Controller, Button

class InputManager:

    def __init__(self, ip='0.0.0.0', port=7000):
        self.input = {
            "mouse_pos": [0,0],
            "lmb": False,
            "rmb": False,
            "keys": []
        }
        self.ip = ip
        self.port = port
        
    def motion(self, event):
        #self.input["mouse_pos"] = [event.x, event.y]
        pass

    def key(self, event):
        print(repr(event.char))
        self.input["keys"].append(repr(event.char))

    def left_click_pressed(self, event):
        self.input["mouse_pos"] = [event.x, event.y]
        self.input["lmb"] = True

    def left_click_released(self, event):
        self.input["mouse_pos"] = [event.x, event.y]
        self.input["lmb"] = False

    def right_click_pressed(self, event):
        self.input["mouse_pos"] = [event.x, event.y]
        self.input["rmb"] = True

    def right_click_released(self, event):
        self.input["mouse_pos"] = [event.x, event.y]
        self.input["rmb"] = False

    def transmit(self):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((self.ip, self.port))

        while True:
            conn.send(str(self.input).encode())
            self.input["keys"] = []
            time.sleep(0.2)

    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sender:

            sender.bind((self.ip, self.port))
            sender.listen()
            print('Waiting for connection...')
            conn, addr = sender.accept()

            with conn:
                print('Connected by', addr)

                mouse = Controller()
                last_mouse_input = [0,0]
                while True:
                    #start_time = time.time()
                    received_input = eval(conn.recv(1024).decode())
                    mouse_input = received_input["mouse_pos"]
                    mouse_input[0] = mouse_input[0]/1280 * 1920
                    mouse_input[1] = mouse_input[1]/720 * 1080
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