from flask import Flask, Response
import pyautogui
import cv2
import numpy as np
import time

app = Flask(__name__)

def generate_frames():
    while True:
        start = time.time()

        # 擷取螢幕畫面
        screenshot = pyautogui.screenshot()

        # 轉成 OpenCV 格式並縮小畫面（提升速度）
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (960, 540))  # 或 (1280, 720)

        # 壓縮成 JPEG 格式
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        frame = buffer.tobytes()

        # 發送 MJPEG 格式
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        # 控制 FPS：盡量靠近 ~10–15fps，視 CPU 情況可再調整
        elapsed = time.time() - start
        time.sleep(max(0, 0.07 - elapsed))  # ~14fps

@app.route('/')
def index():
    return '''
        <html>
            <head><title>即時螢幕串流</title></head>
            <body style="margin:0;">
                <img src="/video_feed" width="100%" />
            </body>
        </html>
    '''

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
