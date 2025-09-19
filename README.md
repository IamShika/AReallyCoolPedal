# 🎹 MIDI Pedal Mapper

Control your MIDI sustain pedal using your computer keyboard.  
Map keys like `Shift`, `Numpad0`, or `Alt` to toggle the sustain pedal on/off — perfect for musicians who use digital pianos or DAWs and want a shortcut control.
You should install LoopMidi to route the midi signal to DAW too.

# See gifs below for guide.

---

## ✅ Features

- ⌨️ **Trigger MIDI sustain pedal** using custom keyboard keys
- 🛠️ **Add/Remove trigger keys** directly from GUI
- 🎚️ **Select MIDI output port** from dropdown list
- 🟢🟥 **System tray icon** shows current pedal state (green = on, red = off)
- 💾 **Settings saved** automatically in `config.json`
- 📦 **Standalone `.exe` build** — no installer needed!

---

## 📸 Guide ~
note : gif colors might look a little bit weird xd

- How to start
  
![How to Start](Areallycoolpedal+-+Start.gif)

- Taskbar Indicator
  
![TBIndicator](Areallycoolpedal+-+Tray+Indicator.gif)

- Add Keys

![Add Keys](Areallycoolpedal+-+Add+Keys.gif)

- Remove Keys

![Remove Keys](Areallycoolpedal+-+Remove+Keys.gif)

---

## 🧰 Requirements

### For Running From exe :

- just download form release and run it that's all.
- Download Loopmidi

### For Running From Source:
- Download this repo as zip
- Python 3.8+
- `mido`
- `python-rtmidi`
- `pynput`
- `pystray`
- `pillow`
- `tkinter` (usually included with Python on Windows)

Install all dependencies:

```bash
pip install mido python-rtmidi pynput pystray pillow
```

# 🙌 Credits
Built using:
- Mido
- python-rtmidi
- pynput
- pystray
- Pillow

