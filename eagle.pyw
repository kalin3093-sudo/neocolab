import subprocess
import pyautogui
import pyperclip
import time
import keyboard
import threading
from langchain_community.llms import Ollama
import os

# Start Ollama server in background
def start_ollama_server():
    if os.name == 'nt':  # For Windows
        subprocess.Popen(
            ["ollama", "serve"], 
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    else:  # For Unix-based systems
        subprocess.Popen(
            ["ollama", "serve", "&"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
    print("Ollama server started!")

start_ollama_server()

# Function to search for code using Ollama and copy result to clipboard
def search_code():
    print("started")
    llm = Ollama(model="codellama")
    clipboard_text = pyperclip.paste()
    response = llm.invoke(clipboard_text + "write code for problem solving using python,it should solve hidden cases.give only code don't give explanation")
    response = response.replace("```", "")
    response = response.replace(":", "?")
    response = response.strip()  
    pyperclip.copy(response)
    print("Response copied to clipboard!")
    pyautogui.press("#")
    time.sleep(0.01)
    pyautogui.press("#")
    time.sleep(0.01)
    pyautogui.press("#")

# Function to type clipboard content
typing_enabled = True
pause_typing = False

def type_clipboard_content():
    global typing_enabled, pause_typing
    time.sleep(1)
    clipboard_content = pyperclip.paste()
    typing_enabled = True
    pause_typing = False
    for char in clipboard_content:
        while pause_typing:
            time.sleep(1)  # Wait while typing is paused
        if not typing_enabled:
            break
        pyautogui.press(char)
        time.sleep(0.01)
    typing_enabled = False

# Function to stop typing
def stop_typing():
    global typing_enabled
    typing_enabled = False

# Function to toggle pause/resume typing
def toggle_pause_typing():
    global pause_typing
    pause_typing = not pause_typing
    print("Typing paused" if pause_typing else "Typing resumed")

# Define shortcuts
search_shortcut = 'shift+s'
type_shortcut = 'shift+h'
stop_shortcut = 'shift+f'
pause_resume_shortcut = 'shift+p'  # Shortcut to pause/resume typing

# Assign hotkeys
keyboard.add_hotkey(search_shortcut, search_code)  # Start search
keyboard.add_hotkey(type_shortcut, lambda: threading.Thread(target=type_clipboard_content).start())  # Start typing
keyboard.add_hotkey(stop_shortcut, stop_typing)  # Stop typing
keyboard.add_hotkey(pause_resume_shortcut, toggle_pause_typing)  # Pause/resume typing

# Wait for keyboard events
keyboard.wait()





