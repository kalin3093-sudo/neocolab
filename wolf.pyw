import os
import subprocess
import pyautogui
import pyperclip
import time
import keyboard
import threading
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyBxlPy1FAiHohdI-AYcOkzbz0wR39WPHJc")

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 1000000,
    "response_mime_type": "text/plain",
}

# Create the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Start chat session with the model
chat_session = model.start_chat(history=[])

# Function to search for code using Gemini and copy result to clipboard
def search_code():
    print("Started search using Gemini")
    
    clipboard_text = pyperclip.paste()
    query = clipboard_text + " use html and css give only code no comments or explanation inside code, give only the code.write code as short as you can.do not use functions"
    
    response = chat_session.send_message(query)
    
    # Process the response
    # code_response = response.text.replace("```", "").replace("python", "").strip()
    code_response = "\n".join([line.lstrip() for line in response.text.splitlines()])
    code_response = code_response.replace("```", "").replace("python", "").strip()
    
    
    # Copy the response to clipboard
    pyperclip.copy(code_response)
    print("Response copied to clipboard!")

    # Press '#' to trigger typing (optional)
    pyautogui.press("#")
    time.sleep(0.01)
    pyautogui.press("#")
    time.sleep(0.01)
    pyautogui.press("#")

# Typing related variables and functions
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
