from flask import Flask, Response, request, render_template
import pyautogui
import cv2
import numpy as np
import time
import subprocess
import threading

app = Flask(__name__)

screen_width, screen_height = pyautogui.size()
VIRTUAL_AUDIO_DEVICE = "CABLE Output (VB-Audio Virtual Cable)"

def generate_frames():
    while True:
        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (960, 540))
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.07)

def generate_audio():
    cmd = [
        "ffmpeg",
        "-f", "dshow",
        "-i", f"audio={VIRTUAL_AUDIO_DEVICE}",
        "-acodec", "libmp3lame",
        "-ab", "128k",
        "-f", "mp3",
        "pipe:1"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        while True:
            chunk = proc.stdout.read(4096)
            if not chunk:
                break
            yield chunk
    finally:
        proc.kill()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

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

@app.route('/scroll', methods=['POST'])
def scroll():
    direction = request.form.get('direction')
    amount = int(request.form.get('amount', 0))
    rel_x = float(request.form.get('x', 0.5))
    rel_y = float(request.form.get('y', 0.5))
    
    # 將滑鼠移動到用戶手指的位置（螢幕中的對應相對位置）
    abs_x = int(screen_width * rel_x)
    abs_y = int(screen_height * rel_y)
    pyautogui.moveTo(abs_x, abs_y)

    if direction == 'up':
        pyautogui.scroll(amount)
    elif direction == 'down':
        pyautogui.scroll(-amount)
    return 'OK'


@app.route('/back')
def back():
    pyautogui.hotkey('alt', 'left')
    return 'OK'

@app.route('/next_track')
def next_track():
    pyautogui.hotkey('shift', 'n')
    return 'OK'

@app.route('/random_click')
def random_click():
    pyautogui.moveTo(2151, 553)
    pyautogui.click()
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
