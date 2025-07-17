from flask import Flask, Response, request, render_template_string
import pyautogui
import cv2
import numpy as np
import time
import socket
import subprocess

app = Flask(__name__)

# 取得實際螢幕解析度
screen_width, screen_height = pyautogui.size()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

# ======== 畫面串流 ========
def generate_frames():
    while True:
        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (960, 540))  # 預覽畫面大小
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        time.sleep(0.07)

# ======== 音訊串流 ========
def generate_audio():
    cmd = [
        "ffmpeg",
        "-f", "dshow",
        "-i", "audio=CABLE Output (VB-Audio Virtual Cable)",  # ← 這個名稱請確認
        "-acodec", "libmp3lame",
        "-ab", "128k",
        "-f", "mp3",
        "pipe:1"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    try:
        while True:
            chunk = proc.stdout.read(4096)
            if not chunk:
                break
            yield chunk
    finally:
        proc.kill()

# ======== Flask 路由 ========
@app.route('/')
def index():
    html = f'''
    <html>
        <head><title>手機控制電腦</title></head>
        <body style="margin:0; overflow:hidden;">
            <img src="/video_feed" width="100%" id="screen" style="display:block;"/>
            
            <!-- 加入音訊播放 -->
            <audio controls autoplay>
                <source src="/audio" type="audio/mpeg">
                您的瀏覽器不支援 audio 元素。
            </audio>

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

@app.route('/audio')
def audio():
    return Response(generate_audio(), mimetype='audio/mpeg')

@app.route('/click')
def click_mouse():
    rel_x = float(request.args.get('x', 0))
    rel_y = float(request.args.get('y', 0))
    abs_x = int(screen_width * rel_x)
    abs_y = int(screen_height * rel_y)

    pyautogui.moveTo(abs_x, abs_y)
    pyautogui.click()

    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
