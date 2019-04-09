from threading import Thread
import time
from PIL import Image
import mss
from flask import Flask, send_file
from io import BytesIO

from input_manager import InputManager

input_manager = InputManager("0.0.0.0", 6969)
Thread(target=input_manager.receive, args=[]).start()

app = Flask(__name__)

@app.route("/")
def index():
    output = BytesIO()
    with mss.mss() as sct:
        image = sct.grab(sct.monitors[1])
        pil_img = Image.frombytes('RGB', image.size, image.bgra, 'raw', 'BGRX')
        pil_img.save(output, 'JPEG', quality=70)
    output.seek(0, 0)
    return send_file(output, mimetype='image/jpeg')
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000, debug=False)