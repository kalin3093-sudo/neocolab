import os
import subprocess
import pyautogui
import pyperclip
import time
import keyboard
import threading
import google.generativeai as genai
from langchain_ollama import OllamaLLM
import easyocr
from PIL import ImageGrab
import numpy as np

# Initialize EasyOCR reader
ocr_reader = easyocr.Reader(['en'], gpu=False)

# Screenshot variables
click_stage = 0
top_left = (0, 0)
bottom_right = (0, 0)
screenshot_session_text = ""  # Stores combined text from multiple screenshots

# Start Ollama server in background
def start_ollama_server():
    if os.name == 'nt':  # Windows
        subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NO_WINDOW)
    else:  # Mac/Linux
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Ollama server started!")

start_ollama_server()

# Configure Gemini
genai.configure(api_key="AIzaSyBxlPy1FAiHohdI-AYcOkzbz0wR39WPHJc")
model = genai.GenerativeModel(model_name="gemini-1.5-flash")
chat_session = model.start_chat(history=[])

# Screenshot Functions
def start_screenshot_session():
    global click_stage, screenshot_session_text
    click_stage = 0
    screenshot_session_text = ""
    print("New screenshot session started - ready for first region")

def capture_screenshot_region():
    global click_stage, top_left, bottom_right, screenshot_session_text
    pos = pyautogui.position()
    
    if click_stage == 0:
        top_left = pos
        click_stage = 1
        print(f"Top-left corner set at: {top_left}")
    else:
        bottom_right = pos
        click_stage = 0
        print(f"Bottom-right corner set at: {bottom_right}")
        process_screenshot()

def process_screenshot():
    global screenshot_session_text
    
    # Calculate region coordinates
    x1, y1 = top_left
    x2, y2 = bottom_right
    left = min(x1, x2)
    top = min(y1, y2)
    right = max(x1, x2)
    bottom = max(y1, y2)
    
    # Capture and process screenshot
    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
    result = ocr_reader.readtext(np.array(screenshot), detail=0)
    new_text = " ".join(result).strip()
    
    if new_text:
        # Add to session text with separator
        if screenshot_session_text:
            screenshot_session_text += "\n\n--- New Region ---\n\n" + new_text
        else:
            screenshot_session_text = new_text
        
        pyperclip.copy(screenshot_session_text)
        print(f"Text added to session (Total regions: {screenshot_session_text.count('--- New Region ---') + 1})")
    else:
        print("No text found in this region")

# AI Search Functions
def perform_search(search_function, model_name):
    global screenshot_session_text
    
    if not screenshot_session_text:
        print("No screenshots taken yet! Capture some regions first.")
        return
    
    print(f"Searching with {model_name}...")
    pyperclip.copy(screenshot_session_text)  # Ensure clipboard has all captured text
    search_function()
    start_screenshot_session()  # Reset for new session after search

def gemini_search():
    clipboard_text = pyperclip.paste()
    query = f"{clipboard_text} use java language give only code no comments or explanation inside code. use using namespace std"
    response = chat_session.send_message(query)
    clean_response = response.text.replace("```", "").replace("python", "").strip()
    pyperclip.copy(clean_response)
    print("Gemini response copied to clipboard!")
    _signal_ready()

def ollama_search():
    llm = OllamaLLM(model="deepseek-coder-v2")
    clipboard_text = pyperclip.paste()
    query = f"{clipboard_text} use java language give only code no comments or explanation inside code. use using namespace std"
    response = llm.invoke(query)
    clean_response = response.replace("```", "").replace("python", "").strip()
    pyperclip.copy(clean_response)
    print("Ollama response copied to clipboard!")
    _signal_ready()

def _signal_ready():
    for _ in range(3):
        pyautogui.press("#")
        time.sleep(0.05)

# Typing Functions
typing_enabled = False
pause_typing = False

def start_typing():
    global typing_enabled
    if not typing_enabled:
        typing_enabled = True
        text = pyperclip.paste()
        
        def type_text():
            for char in text:
                while pause_typing:
                    time.sleep(0.1)
                if not typing_enabled:
                    break
                pyautogui.press(char)
                time.sleep(0.05)
        
        threading.Thread(target=type_text).start()

def stop_typing():
    global typing_enabled
    typing_enabled = False

def toggle_pause_typing():
    global pause_typing
    pause_typing = not pause_typing
    print("Typing paused" if pause_typing else "Typing resumed")

# Hotkeys Setup
keyboard.add_hotkey('shift+s', capture_screenshot_region)  # Capture screenshot region
keyboard.add_hotkey('shift+x', lambda: perform_search(gemini_search, "Gemini"))  # Gemini search
keyboard.add_hotkey('shift+y', lambda: perform_search(ollama_search, "Ollama"))  # Ollama search
keyboard.add_hotkey('shift+h', start_typing)  # Start typing
keyboard.add_hotkey('shift+f', stop_typing)  # Stop typing
keyboard.add_hotkey('shift+p', toggle_pause_typing)  # Pause typing
keyboard.add_hotkey('shift+n', start_screenshot_session)  # New screenshot session

# Initialize first session
start_screenshot_session()

# Main Program
print("""
Program ready! Hotkeys:
SHIFT+S - Capture screenshot region (two clicks)
SHIFT+X - Gemini code search (uses all captured regions)
SHIFT+Y - Ollama code search (uses all captured regions)
SHIFT+H - Start typing
SHIFT+F - Stop typing
SHIFT+P - Pause/resume typing
SHIFT+N - Start new screenshot session

Workflow:
1. Use SHIFT+S to capture multiple regions (text accumulates)
2. When ready, use SHIFT+X (Gemini) or SHIFT+Y (Ollama) to search
3. After search, new screenshot session automatically starts
4. Use SHIFT+H to type the result
5. Use SHIFT+N anytime to manually start new session
""")

keyboard.wait()