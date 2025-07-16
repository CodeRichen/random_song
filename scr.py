from flask import Flask, send_file
import pyautogui
import os

app = Flask(__name__)

@app.route("/")
def index():
    return '''
        <html>
            <head><meta http-equiv="refresh" content="2"></head>
            <body>
                <h2>電腦螢幕截圖</h2>
                <img src="/screenshot" width="100%" />
            </body>
        </html>
    '''

@app.route("/screenshot")
def serve_screenshot():
    try:
        save_path = os.path.join(os.getcwd(), "screenshot.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(save_path)
        return send_file(save_path, mimetype="image/png")
    except Exception as e:
        return f"擷取失敗: {e}", 500

if __name__ == "__main__":
    print("Flask 網頁啟動中…")
    print("請在瀏覽器輸入：http://localhost:5000")
    app.run(host="0.0.0.0", port=8080)
