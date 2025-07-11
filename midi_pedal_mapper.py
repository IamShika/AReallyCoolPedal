import mido
mido.set_backend('mido.backends.rtmidi')
import json
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pynput import keyboard
import pystray
from PIL import Image, ImageDraw

# === Configuration ===
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "trigger_keys": ["shift", "numpad0"],
    "midi_port": ""
}

# === Globals ===
trigger_keys = []
output = None
pedal_on = False
key_held = False
listener = None
listener_running = False
tray_icon = None

# === Load & Save Config ===
def load_config():
    global trigger_keys, selected_port
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            trigger_keys.clear()
            trigger_keys.extend(data.get("trigger_keys", []))
            selected_port.set(data.get("midi_port", ""))
    else:
        trigger_keys.extend(DEFAULT_CONFIG["trigger_keys"])
        selected_port.set(DEFAULT_CONFIG["midi_port"])
    update_trigger_display()

def save_config():
    data = {
        "trigger_keys": trigger_keys,
        "midi_port": selected_port.get()
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

# === MIDI ===
def connect_midi_port():
    global output
    try:
        output = mido.open_output(selected_port.get())
        print(f"[\u2713] Connected to MIDI port: {selected_port.get()}")
        return True
    except Exception as e:
        print(f"[!] MIDI error: {e}")
        messagebox.showerror("MIDI Error", f"Could not open MIDI port:\n'{selected_port.get()}'\n\n{e}")
        return False

def close_midi_output():
    global output
    if output:
        try:
            output.close()
        except:
            pass
        output = None

def send_pedal(value):
    if output:
        msg = mido.Message('control_change', control=64, value=value)
        output.send(msg)
        print(f"[MIDI] Sent pedal value: {value}")

# === Key Listener ===
def on_press(key):
    global pedal_on, key_held
    if not listener_running:
        return
    key_str = str(key).lower().replace('key.', '')  # Normalize key
    if key_str in map(str.lower, trigger_keys) and not key_held:
        pedal_on = not pedal_on
        send_pedal(127 if pedal_on else 0)
        key_held = True
        update_status()

def on_release(key):
    global key_held
    key_str = str(key).lower().replace('key.', '')  # Normalize key
    if key_str in map(str.lower, trigger_keys):
        key_held = False


def start_listener():
    global listener
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

def stop_listener():
    global listener
    if listener:
        listener.stop()
        listener = None
    close_midi_output()

# === GUI ===
def toggle_listener():
    global listener_running
    if listener_running:
        stop_listener()
        listener_running = False
        start_button.config(text="Start Pedal Listener")
        update_status()
    else:
        if not connect_midi_port():
            return
        save_config()
        start_listener()
        listener_running = True
        start_button.config(text="Stop Pedal Listener")
        update_status()

def update_status():
    if not listener_running:
        status.set("OFF")
        status_label.config(fg="red")
        if tray_icon:
            tray_icon.icon = create_icon_image(False)
    else:
        status.set("ON" if pedal_on else "OFF")
        status_label.config(fg="green" if pedal_on else "red")
        if tray_icon:
            tray_icon.icon = create_icon_image(pedal_on)

def update_trigger_display():
    trigger_display.config(text=", ".join(f"**{k.upper()}**" for k in trigger_keys))
    trigger_display.config(font=("Arial", 10, "bold"))

def prompt_add_key():
    popup = tk.Toplevel(root)
    popup.title("Add Trigger Key")
    tk.Label(popup, text="Press a key (ESC to cancel)").pack(padx=10, pady=10)
    popup.geometry("250x100")
    popup.grab_set()

    def on_key(event):
        if event.keysym == "Escape":
            popup.destroy()
        else:
            key_name = event.keysym.lower()
            if key_name not in trigger_keys:
                trigger_keys.append(key_name)
                save_config()
                update_trigger_display()
            popup.destroy()

    popup.bind("<Key>", on_key)

def prompt_remove_key():
    popup = tk.Toplevel(root)
    popup.title("Remove Trigger Key")
    tk.Label(popup, text="Click a key to remove (ESC to cancel)").pack(padx=10, pady=5)
    popup.geometry("300x150")
    popup.grab_set()

    def remove_key(k):
        trigger_keys.remove(k)
        save_config()
        update_trigger_display()
        popup.destroy()

    for k in trigger_keys:
        btn = tk.Button(popup, text=k.upper(), command=lambda k=k: remove_key(k), width=10)
        btn.pack(pady=2)

    def esc_close(event):
        if event.keysym == "Escape":
            popup.destroy()

    popup.bind("<Key>", esc_close)

def update_port_list():
    ports = mido.get_output_names()
    port_dropdown['values'] = ports
    if selected_port.get() not in ports:
        selected_port.set(ports[0] if ports else "")

def on_exit():
    stop_listener()
    if tray_icon:
        tray_icon.stop()
    root.destroy()

def create_icon_image(is_on):
    img = Image.new('RGB', (64, 64), color='white')
    d = ImageDraw.Draw(img)
    color = 'green' if is_on else 'red'
    d.rectangle([16, 24, 48, 40], fill=color)
    return img

# === Tray Icon ===
def create_tray_icon():
    global tray_icon
    tray_icon = pystray.Icon("MIDI Pedal")
    tray_icon.icon = create_icon_image(False)
    tray_icon.menu = pystray.Menu(
        pystray.MenuItem("Toggle Pedal", lambda icon, item: root.after(0, toggle_listener)),
        pystray.MenuItem("Quit", lambda icon, item: on_exit())
    )
    threading.Thread(target=tray_icon.run, daemon=True).start()

# === App Init ===
root = tk.Tk()
root.title("MIDI Pedal Mapper")
root.geometry("350x250")
root.resizable(False, False)

frame = tk.Frame(root)
frame.pack(pady=10)

# MIDI Port Dropdown
tk.Label(frame, text="Select MIDI Port:").grid(row=0, column=0, sticky='w')
selected_port = tk.StringVar()
port_dropdown = ttk.Combobox(frame, textvariable=selected_port, state="readonly", width=30)
port_dropdown.grid(row=1, column=0, columnspan=2)
update_port_list()

# Trigger Keys
tk.Label(frame, text="Trigger Keys:").grid(row=2, column=0, sticky='w')
trigger_display = tk.Label(frame, text="", anchor='w', justify='left')
trigger_display.grid(row=3, column=0, columnspan=2, sticky='w')

add_button = tk.Button(frame, text="Add Key", command=prompt_add_key)
add_button.grid(row=4, column=0, sticky='w')

remove_button = tk.Button(frame, text="Remove Key", command=prompt_remove_key)
remove_button.grid(row=4, column=1, sticky='e')

# Start Button
start_button = tk.Button(frame, text="Start Pedal Listener", command=toggle_listener, bg="#3fa")
start_button.grid(row=5, column=0, pady=10)

# Status Label
status = tk.StringVar()
status.set("OFF")
status_label = tk.Label(frame, textvariable=status, fg="red", font=("Arial", 12, "bold"))
status_label.grid(row=5, column=1)

load_config()
update_status()
create_tray_icon()
root.protocol("WM_DELETE_WINDOW", on_exit)
root.mainloop()
