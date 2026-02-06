import os
import subprocess
import pyautogui
import pyperclip
import time
import keyboard
import threading
import google.generativeai as genai
from langchain_community.llms import Ollama

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

# AI Search Functions
def ollama_search_code():
    print("Searching with Ollama...")
    clipboard_text = pyperclip.paste()
    query = f"{clipboard_text} use c++ language give only code no comments or explanation inside code. use using namespace std"
    # query = f"{clipboard_text} use html tailwind css and javascript give only code no comments or explanation inside code"
    
    llm = Ollama(model="qwen2.5-coder:7b")
    response = llm.invoke(query)
    
    # Clean up the response
    clean_response = response.replace("```", "").replace("cpp", "").strip()
    pyperclip.copy(clean_response)
    print("Ollama response copied to clipboard!")
    _signal_ready()

def gemini_search_code():
    print("Searching with Gemini...")
    clipboard_text = pyperclip.paste()
    query = f"{clipboard_text} use cpp give only code no comments or explanation inside code. use using namespace std"
    # query = f"{clipboard_text} use html tailwind css and javascript give only code no comments or explanation inside code"
    
    response = chat_session.send_message(query)
    clean_response = response.text.replace("```", "").replace("python", "").strip()
    pyperclip.copy(clean_response)
    print("Gemini response copied to clipboard!")
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

# Clipboard Functions
def append_to_clipboard():
    time.sleep(0.5)
    current = pyperclip.paste()
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.1)
    new_text = pyperclip.paste()
    
    if new_text and new_text != current:
        combined = current + "\n" + new_text
        pyperclip.copy(combined)
        print("Text appended to clipboard!")

def normal_copy():
    pyperclip.copy('')
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.1)
    print("Text copied to clipboard.")

# Hotkeys Setup
keyboard.add_hotkey('shift+y', ollama_search_code)
keyboard.add_hotkey('shift+x', gemini_search_code)
keyboard.add_hotkey('shift+h', start_typing)
keyboard.add_hotkey('shift+f', stop_typing)
keyboard.add_hotkey('shift+p', toggle_pause_typing)
keyboard.add_hotkey('alt+a', append_to_clipboard)
keyboard.add_hotkey('ctrl+c', normal_copy)

# Main Program
print("""
Program ready! Hotkeys:
SHIFT+Y - Ollama code search (C++)
SHIFT+X - Gemini code search (Python)
SHIFT+H - Start typing
SHIFT+F - Stop typing
SHIFT+P - Pause/resume typing
ALT+A - Append selected text to clipboard
CTRL+C - Normal copy
""")

keyboard.wait()