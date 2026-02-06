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
def gemini_search_code():
    print("Started search using Gemini")
    
    clipboard_text = pyperclip.paste()
    query = clipboard_text + " use java language give only code no comments or explanation inside code. use using namespace std"
    
    response = chat_session.send_message(query)
    
    # Process the response
    code_response = "\n".join([line.lstrip() for line in response.text.splitlines()])
    code_response = code_response.replace("```", "").replace("cpp", "").strip()
    
    # Copy the response to clipboard
    pyperclip.copy(code_response)
    print("Response copied to clipboard!")

    # Press '#' to trigger typing (optional)
    pyautogui.press("#")

# Function to search for code using Ollama and copy result to clipboard
def ollama_search_code():
    print("Started search using Ollama")
    
    llm = Ollama(model="deepseek-coder-v2")
    clipboard_text = pyperclip.paste()
    query = clipboard_text + " use java language give only code no comments or explanation inside code. use using namespace std"
    
    response = llm.invoke(query)
    response = response.replace("```", "").replace("cpp", "").strip()
    
    pyperclip.copy(response)
    print("Response copied to clipboard!")

    # Press '#' to trigger typing (optional)
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

def append_to_clipboard():
    time.sleep(0.5)
    current_clipboard = pyperclip.paste()  # Get the current clipboard content before copying
    pyautogui.hotkey('ctrl', 'c')  # Copy the selected text
    time.sleep(0.1)  # Wait for the clipboard to update

    selected_text = pyperclip.paste()  # Get the newly selected text after the clipboard updates

    # If the new text is different from the current clipboard content, append it
    if selected_text and selected_text != current_clipboard:
        new_clipboard = current_clipboard + "\n" + selected_text
        pyperclip.copy(new_clipboard)
        print("Selected text appended to clipboard!")
    else:
        print("No new text selected to append.")

# Function to handle regular copy behavior (Ctrl+C)
def normal_copy():
    pyperclip.copy('')  # Clear the clipboard first
    pyautogui.hotkey('ctrl', 'c')  # Trigger Ctrl+C to copy selected text
    time.sleep(0.1)  # Wait for the clipboard to update
    print("Clipboard cleared and text copied to clipboard.")

# Global variable to track whether shortcuts are enabled
shortcuts_enabled = True

# Function to toggle enabling/disabling all shortcuts
def toggle_shortcuts():
    global shortcuts_enabled
    shortcuts_enabled = not shortcuts_enabled
    if shortcuts_enabled:
        # Reassign hotkeys
        keyboard.add_hotkey(ollama_search_shortcut, ollama_search_code)
        keyboard.add_hotkey(gemini_search_shortcut, gemini_search_code)
        keyboard.add_hotkey(type_shortcut, lambda: threading.Thread(target=type_clipboard_content).start())
        keyboard.add_hotkey(stop_shortcut, stop_typing)
        keyboard.add_hotkey(pause_resume_shortcut, toggle_pause_typing)
        keyboard.add_hotkey(append_shortcut, append_to_clipboard)
        keyboard.add_hotkey(copy_shortcut, normal_copy)
        print("Shortcuts enabled!")
    else:
        # Remove hotkeys if they exist
        try:
            keyboard.remove_hotkey(ollama_search_shortcut)
        except KeyError:
            pass
        try:
            keyboard.remove_hotkey(gemini_search_shortcut)
        except KeyError:
            pass
        try:
            keyboard.remove_hotkey(type_shortcut)
        except KeyError:
            pass
        try:
            keyboard.remove_hotkey(stop_shortcut)
        except KeyError:
            pass
        try:
            keyboard.remove_hotkey(pause_resume_shortcut)
        except KeyError:
            pass
        try:
            keyboard.remove_hotkey(append_shortcut)
        except KeyError:
            pass
        try:
            keyboard.remove_hotkey(copy_shortcut)
        except KeyError:
            pass
        print("Shortcuts disabled!")


# Define shortcuts
ollama_search_shortcut = 'shift+y'  # Ollama search
gemini_search_shortcut = 'shift+x'  # Gemini search
type_shortcut = 'shift+h'  # Start typing
stop_shortcut = 'shift+f'  # Stop typing
pause_resume_shortcut = 'shift+p'  # Pause/resume typing
append_shortcut = 'alt+a'  # Shortcut to append selected text to clipboard
copy_shortcut = 'ctrl+c'  # Standard copy shortcut
toggle_shortcuts_shortcut = 'shift+s+r+i'  # Toggle all shortcuts

# Assign hotkey to toggle shortcuts
keyboard.add_hotkey(toggle_shortcuts_shortcut, toggle_shortcuts)

# Wait for keyboard events
keyboard.wait()
