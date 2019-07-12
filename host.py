from threading import Thread

from input_manager import InputManager
from vnc import VNC

host = VNC("0.0.0.0", 7000)
input_manager = InputManager("0.0.0.0", 6969)   

if __name__ == "__main__":
    Thread(target=input_manager.receive, args=[]).start()
    host.transmit()