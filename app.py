import eel
from vnc import VNC
from threading import Thread
import atexit
import sys

from input_manager import InputManager
from vnc import VNC

status = 'None'
connection = 'None'
vnc = VNC()
input_manager = InputManager()

eel.init('web')

@eel.expose
def host():
    global status
    global vnc
    global transmit_thread
    global input_manager

    print('Hosting...')
    status = 'host'

    transmit_thread = Thread(target=vnc.transmit)
    transmit_thread.daemon = True
    transmit_thread.start()

    input_thread = Thread(target=input_manager.receive_input, args=[])
    input_thread.daemon = True
    input_thread.start()

@eel.expose
def stop_host():
    global status
    status = 'None'
    print("Stopping server...")

@eel.expose
def connect(ip):
    global status
    global vnc
    global connection
    print('Connecting...')
    status = 'client'
    vnc.ip = ip
    input_manager.ip = ip
    try:
        vnc.start_receive()
        input_manager.connect_input()
        connection = 'active'
    except Exception as e:
        print('Connection failed...')

@eel.expose
def transmit_input(data, event_type):
    if status == 'client':
        if event_type == 'keydown':
            input_manager.transmit_input(keydown=data)
            pass
        elif event_type == 'keyup':
            input_manager.transmit_input(keyup=data)
            pass
        elif event_type == 'mousemove':
            #print(data)
            input_manager.transmit_input(mouse_pos=data)
            pass
        elif event_type == 'mousedown':
            #print(data)
            input_manager.transmit_input(mouse_pos=data['pos'], mouse_down=data['button'])
        elif event_type == 'mouseup':
            #print(data)
            input_manager.transmit_input(mouse_pos=data['pos'], mouse_up=data['button'])

eel.start('index.html', block=False, port=8080)

while True:

    if status == 'host':
        eel.updateScreen(vnc.image_serializer().decode())
    elif status == 'client':
        if connection == 'active':
            eel.updateScreen(vnc.receive())

    eel.sleep(.01)