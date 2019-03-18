from threading import Thread
import time
from flask import Flask, send_file
from io import BytesIO

from input_manager import InputManager


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
    app.run(host="0.0.0.0", port=7000, debug=False)