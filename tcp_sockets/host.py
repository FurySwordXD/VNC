from threading import Thread
import time

from input_manager import InputManager
from vnc import VNC

host = VNC("0.0.0.0", 7000)
input_manager = InputManager("0.0.0.0", 6969)   

if __name__ == "__main__":

    host.start_transmit()
    #feed_transmitter_thread = Thread(target=host.transmit, args=[])
    #feed_transmitter_thread.start()

    input_receiver_thread = Thread(target=input_manager.receive, args=[])
    input_receiver_thread.start()