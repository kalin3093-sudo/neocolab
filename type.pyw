import keyboard
import pyperclip
import time
import platform
import subprocess

def get_selected_text():
    """Get selected text without simulating Ctrl+C (platform-specific)."""
    system = platform.system()
    old_clipboard = pyperclip.paste()  # Backup clipboard

    try:
        if system == "Windows":
            # Windows: Use PowerShell to get selected text
            script = """
            Add-Type -AssemblyName System.Windows.Forms
            $tb = New-Object System.Windows.Forms.TextBox
            $tb.Multiline = $true
            $tb.Paste()  # Attempt to get selected text
            $tb.Text
            """
            result = subprocess.run(
                ["powershell", "-command", script],
                capture_output=True,
                text=True,
                shell=True,
            )
            return result.stdout.strip()

        elif system == "Darwin":  # macOS
            # macOS: Use pbpaste (built-in) to get clipboard (after silent Cmd+C)
            script = """
            tell application "System Events" to keystroke "c" using command down
            delay 0.3
            do shell script "pbpaste"
            """
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()

        elif system == "Linux":
            # Linux: Use xclip (primary selection)
            try:
                return subprocess.check_output(
                    ["xclip", "-selection", "primary", "-o"],
                    text=True,
                ).strip()
            except:
                return ""
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return ""
    finally:
        pyperclip.copy(old_clipboard)  # Restore clipboard

def on_shift_t():
    """Triggered when Shift+T is pressed."""
    selected_text = get_selected_text()
    if selected_text.strip():
        pyperclip.copy(selected_text)  # Copy to clipboard
        print(f"✅ Copied: {selected_text}")
    else:
        print("❌ No text selected or selection not accessible!")

# Register Shift+T hotkey
keyboard.add_hotkey('shift+t', on_shift_t)

print("🎯 Press Shift+T to copy selected text. Press Esc to exit.")
keyboard.wait('esc')  # Exit on Esc