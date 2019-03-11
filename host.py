from threading import Thread

from input_manager import InputManager
from vnc import VNC
        
if __name__ == "__main__":
    host = VNC("0.0.0.0", 6969)
    input_manager = InputManager("0.0.0.0", 7000)
    t1 = Thread(target=host.transmit, args=[])
    t2 = Thread(target=input_manager.receive, args=[])
    t1.start()
    t2.start()



'''
import cv2
import numpy

def compress():
    image = screenshot()
    open_cv_image = numpy.array(image)
    print(len(open_cv_image))
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
    result, encimg = cv2.imencode('.jpg', open_cv_image, encode_param)
    image = Image.fromarray(cv2.imdecode(encimg, 1))
    image.show()
    data = SocketData(image=image)
    data_string = pickle.dumps(data)
    print(len(data_string))
'''