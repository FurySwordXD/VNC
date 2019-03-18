from threading import Thread
import time

from input_manager import InputManager
from vnc import VNC

host = VNC("127.0.0.1", 5000)
input_manager = InputManager("0.0.0.0", 6969)   

if __name__ == "__main__":

    host.start_transmit()