from flask import Flask, Response
import pyautogui
import cv2
import numpy as np
import time

app = Flask(__name__)

def generate_frames():
    while True:
        # 擷取螢幕
        screenshot = pyautogui.screenshot()

        # 轉成 OpenCV 圖片
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # 編碼成 JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # 傳送 multipart 資料
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        time.sleep(0.1)  # 控制 FPS（10fps）

@app.route('/')
def index():
    return '''
        <html>
            <head><title>螢幕串流畫面</title></head>
            <body>
                <h1>即時螢幕畫面</h1>
                <img src="/video_feed" width="100%">
            </body>
        </html>
    '''

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
