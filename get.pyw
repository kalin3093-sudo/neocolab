import subprocess
import keyboard
import psutil
import time

def start_getscreen():
    print("Starting GetscreenHidden service...")
    subprocess.run("sc config GetscreenHidden start= auto", shell=True)
    subprocess.run("net start GetscreenHidden", shell=True)

def fully_stop_getscreen():
    print("Stopping GetscreenHidden service and disabling it...")
    subprocess.run("sc stop GetscreenHidden", shell=True)
    subprocess.run("sc config GetscreenHidden start= disabled", shell=True)

    print("Killing all getscreen.exe processes...")
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and 'getscreen.exe' in proc.info['name'].lower():
            try:
                print(f"Terminating getscreen.exe (PID {proc.pid})")
                proc.terminate()
                proc.wait(timeout=5)
            except psutil.NoSuchProcess:
                print(f"Process {proc.pid} already terminated.")
            except psutil.TimeoutExpired:
                print(f"Force killing getscreen.exe (PID {proc.pid})")
                proc.kill()

# Hotkey bindings
keyboard.add_hotkey("shift+s", start_getscreen)
keyboard.add_hotkey("shift+e", fully_stop_getscreen)

print("✅ Press Shift+S to START GetscreenHidden")
print("❌ Press Shift+E to STOP & DISABLE GetscreenHidden and kill all getscreen.exe processes")

keyboard.wait()
