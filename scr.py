from flask import Flask, Response, request, render_template_string
import pyautogui
import cv2
import numpy as np
import time

app = Flask(__name__)

# 取得實際螢幕解析度（重要）
screen_width, screen_height = pyautogui.size()

def generate_frames():
    while True:
        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (960, 540))  # 預覽解析度
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        time.sleep(0.07)  # 控制FPS

@app.route('/')
def index():
    html = f'''
    <html>
        <head><title>手機控制電腦</title></head>
        <body style="margin:0; overflow:hidden;">
            <img src="/video_feed" width="100%" id="screen" style="display:block;"/>
            <script>
                const img = document.getElementById("screen");
                img.addEventListener("click", function(e) {{
                    const rect = img.getBoundingClientRect();
                    const relX = (e.clientX - rect.left) / rect.width;
                    const relY = (e.clientY - rect.top) / rect.height;

                    // 傳送點擊座標
                    fetch(`/click?x=${{relX}}&y=${{relY}}`);
                }});
            </script>
        </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/click')
def click_mouse():
    # 接收手機點擊位置（相對百分比）
    rel_x = float(request.args.get('x', 0))
    rel_y = float(request.args.get('y', 0))

    # 計算實際座標
    abs_x = int(screen_width * rel_x)
    abs_y = int(screen_height * rel_y)

    pyautogui.moveTo(abs_x, abs_y)
    pyautogui.click()

    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
