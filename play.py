from flask import Flask, render_template, request, redirect, url_for, send_file
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pyautogui
import io
import time
import random

app = Flask(__name__)

# Configure paths
brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"


driver = None
playlist_links = []
playing = False


def change_volume(delta):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current = volume.GetMasterVolumeLevelScalar()
    new_volume = min(max(current + delta, 0.0), 1.0)
    volume.SetMasterVolumeLevelScalar(new_volume, None)
    print(f"Volume changed to {int(new_volume * 100)}%")


@app.route("/volume/up")
def volume_up():
    change_volume(+0.1)
    return "Volume Up"


@app.route("/volume/down")
def volume_down():
    change_volume(-0.1)
    return "Volume Down"


@app.route("/screenshot")
def screenshot():
    screenshot = pyautogui.screenshot()
    buf = io.BytesIO()
    screenshot.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')


def load_playlist(playlist_url):
    global playlist_links
    options = webdriver.ChromeOptions()
    options.binary_location = brave_path
    options.add_argument("--start-maximized")

    drv = webdriver.Chrome(service=Service(), options=options)
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
        print("Playlist is empty.")
        return

    if not driver:
        options = webdriver.ChromeOptions()
        options.binary_location = brave_path
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(service=Service(), options=options)

    while playlist_links and playing:
        link = playlist_links.pop(0)
        print(f"Playing: {link}")
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
        playlist_links.insert(0, playlist_links.pop())
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
