from flask import Flask, render_template, request, redirect, url_for
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time, random

app = Flask(__name__)

# 設定 Brave 路徑與 ChromeDriver 路徑
brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
chromedriver_path = r"C:\Users\User\Desktop\Programm\chromedriver.exe"

# 全域變數控制播放狀態
driver = None
playlist_links = []
playing = False

def load_playlist(playlist_url):
    global playlist_links
    options = webdriver.ChromeOptions()
    options.binary_location = brave_path
    options.add_argument("--start-maximized")

    drv = webdriver.Chrome(service=Service(chromedriver_path), options=options)
    drv.get(playlist_url)
    time.sleep(5)

    last_height = drv.execute_script("return document.documentElement.scrollHeight")
    while True:
        drv.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)
        new_height = drv.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    video_elements = drv.find_elements(By.CSS_SELECTOR, "a.ytd-playlist-video-renderer")
    links = [el.get_attribute("href") for el in video_elements if el.get_attribute("href") and "watch" in el.get_attribute("href")]
    playlist_links = list(set(links))
    random.shuffle(playlist_links)

    drv.quit()

def play_next():
    global playlist_links, driver, playing

    if not playlist_links:
        print("播放清單為空")
        return

    if not driver:
        options = webdriver.ChromeOptions()
        options.binary_location = brave_path
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)

    while playlist_links and playing:
        link = playlist_links.pop(0)
        print(f"🎵 播放：{link}")
        driver.get(link)
        time.sleep(5)

        while True:
            try:
                ended = driver.execute_script("return document.querySelector('video')?.ended")
                if ended:
                    break
            except:
                pass
            time.sleep(5)

@app.route("/", methods=["GET", "POST"])
def index():
    global playing
    if request.method == "POST":
        playlist_url = request.form.get("playlist_url")
        if playlist_url:
            load_playlist(playlist_url)
            playing = True
            thread = Thread(target=play_next)
            thread.start()
            return redirect(url_for('index'))
    return render_template("index.html", playing=playing)

@app.route("/stop")
def stop():
    global playing
    playing = False
    return redirect(url_for('index'))

@app.route("/next")
def next_song():
    global playlist_links
    if playlist_links:
        playlist_links.insert(0, playlist_links.pop())  # 將下一首移到最前面
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  # 手機也能連進來
