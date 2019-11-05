import socket
import time
import pyautogui
import struct
from pynput import mouse
from pynput import keyboard

class InputManager:

    def __init__(self, ip='0.0.0.0', port=6969):
        self.input = {
            "mouse_pos": [0.0, 0.0],
            "lmb": False,
            "rmb": False,
            "keys": [],
        }
        self.ip = ip
        self.port = port
    
    def send_msg(self, sock, msg):
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + msg
        sock.sendall(msg)

    def recv_msg(self, sock):
        # Read message length and unpack it into an integer
        raw_msglen = self.recvall(sock, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return self.recvall(sock, msglen)
    
    def recvall(self, sock, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = b''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data
        
    def set_resolution(self, width=1280, height=720):
        self.width = width
        self.height = height
        #print(self.width, self.height)

    def motion(self, event):
        self.input["mouse_pos"] = [event.x/self.width, event.y/self.height]
        self.send_msg(self.conn, str(self.input).encode())

    def key_pressed(self, event):
        print("Key Press: ", repr(event.char))
        self.input["keys"].append(repr(event.char))
        self.input["keys"] = list(set(self.input["keys"]))
        self.send_msg(self.conn, str(self.input).encode())
    
    def key_released(self, event):
        print("Key Released: ", repr(event.char))
        try:
            self.input["keys"].remove(repr(event.char))
        finally:
            self.send_msg(self.conn, str(self.input).encode())

    def left_click_pressed(self, event):
        self.input["mouse_pos"] = [event.x/self.width, event.y/self.height]
        self.input["lmb"] = True
        self.send_msg(self.conn, str(self.input).encode())

    def left_click_released(self, event):
        self.input["mouse_pos"] = [event.x/self.width, event.y/self.height]
        self.input["lmb"] = False
        self.send_msg(self.conn, str(self.input).encode())

    def right_click_pressed(self, event):
        self.input["mouse_pos"] = [event.x/self.width, event.y/self.height]
        self.input["rmb"] = True
        self.send_msg(self.conn, str(self.input).encode())

    def right_click_released(self, event):
        self.input["mouse_pos"] = [event.x/self.width, event.y/self.height]
        self.input["rmb"] = False
        self.send_msg(self.conn, str(self.input).encode())

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
                    received_input = eval(self.recv_msg(conn).decode())
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
                        print(eval(k))
                        keyboard_var.press(str(eval(k)))

    #EEL

    def connect_input(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.ip, self.port))
        print("Connected to ", self.ip, ":", self.port)

    def transmit_input(self, mouse_pos = None, mouse_down = None, mouse_up = None, keydown = None, keyup = None):
        key_input = {
            "mouse_pos": mouse_pos,
            "mouse_down": mouse_down,
            "mouse_up": mouse_up,
            "keydown": keydown,
            "keyup": keyup
        }
        self.send_msg(self.conn, str(key_input).encode())

    def receive_input(self):
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
                mouse_controller = mouse.Controller()
                keyboard_controller = keyboard.Controller() 

                mouse_buttons = [mouse.Button.left, mouse.Button.middle, mouse.Button.right]

                while True:
                    #start_time = time.time()
                    try:
                        received_input = eval(self.recv_msg(conn).decode())
                        print(received_input)
                        
                        mouse_input = received_input['mouse_pos']
                        if mouse_input:
                            mouse_input[0] = mouse_input[0] * width
                            mouse_input[1] = mouse_input[1] * height

                            mouse_controller.position = tuple(mouse_input)

                        if received_input['mouse_down'] == 0:
                            mouse_controller.press(mouse.Button.left)

                        if received_input['mouse_up'] == 0:
                            mouse_controller.release(mouse.Button.left)

                        if received_input['mouse_down'] == 2:
                            mouse_controller.press(mouse.Button.right)

                        if received_input['mouse_up'] == 2:
                            mouse_controller.release(mouse.Button.right)

                        if received_input['keydown']:
                            keyboard_controller.press(keyboard.KeyCode(received_input['keydown']))

                        if received_input['keyup']:
                            keyboard_controller.release(keyboard.KeyCode(received_input['keyup']))

                    except Exception as e:
                        print(e)
                        pass