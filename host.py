from threading import Thread
import time
from flask import Flask, send_file
from io import BytesIO

from input_manager import InputManager
from vnc import VNC

host = VNC("0.0.0.0", 7000)
input_manager = InputManager("0.0.0.0", 6969)
app = Flask(__name__)


@app.route("/")
def index():
    pil_img = host.screenshot()
    output = BytesIO()
    pil_img.save(output, 'JPEG', quality=70)
    output.seek(0, 0)
    return send_file(output, mimetype='image/jpeg')
    

if __name__ == "__main__":

    #host.start_transmit()
    #feed_transmitter_thread = Thread(target=host.transmit, args=[])
    #feed_transmitter_thread.start()

    input_receiver_thread = Thread(target=input_manager.receive, args=[])
    input_receiver_thread.start()

    app.run(host=host.ip, port=host.port, debug=False)



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