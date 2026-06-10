# CedBox

CedBox is a Python utility package that provides various tools for Terminal User Interfaces (TUI), Morse code processing, hierarchical data handling (Yggdrasil), user input validation, and audio generation/streaming.

## Features

- **TUI (Terminal User Interface)**: A lightweight, declarative terminal interface framework supporting:
  - Nested folder column-based menus
  - Dynamic setting/switch editing with console input validation
  - Headless/Agent execution and full schema serialization via JSON

- **Morse Code Processing**: Tools for working with Morse code:
  - Convert text to Morse code
  - Represent Morse code as time units
  - Generate Morse code sequences and WAV files

- **Yggdrasil**: A hierarchical tree-like data structure that extends Python's dictionary, with support for:
  - Automatic node creation
  - Loading data from DataFrames and SQL queries
  - Tree visualization

- **Input Utilities**: Functions for handling user input with validation and type conversion:
  - Type-safe integer, float, choice, boolean, date, email, and file path inputs.

- **Audio Generation & Streaming**: Utilities for creating WAV files or streaming audio:
  - Generate signals from sequences of durations
  - Play Morse code audio sequences directly to output devices

## Installation

```bash
pip install cedbox
```

## Usage Examples

### TUI (Terminal User Interface)

CedBox includes a lightweight, hierarchical Terminal User Interface (TUI) framework that can be built programmatically, decorated, or generated directly from any `Yggdrasil` tree. It also supports input validation and headless execution via JSON.

#### Defining TUI with Builders and Decorators

```python
import sys
from cedbox import TUI

tui = TUI(title="My TUI Application")

# Add settings with parent containers
tui.add_switch("Muted", default=True, parent="Settings/System")
tui.add_setting("Volume", default=90, parent="Settings/System")

# Add actions using parent mounting
@tui.action("Quit", "Actions")
def quit_app():
    sys.exit(0)

# Add actions using absolute path overrides
@tui.action(abs="Actions/Greet")
def greet():
    return "Hello!"

# Run interactive TUI
tui.run()
```

#### Running TUI directly from Yggdrasil Tree

```python
from cedbox import Yggdrasil, TUI

tree = Yggdrasil()
tree["Settings"]["System"]["Muted"] = False
tree["Settings"]["System"]["Volume"] = 80

tui = TUI(tree, title="Direct Yggdrasil TUI")
tui.run()
```

#### Machine-Readable Headless JSON Mode

Any application defined using `TUI` can be executed headlessly without the terminal interface, making it perfect for external agents or automated scripts to interact with:

1. **Dump Menu Schema as JSON:**
   ```bash
   python my_app.py --json-schema
   ```

2. **Execute Actions or Update Settings via Path:**
   ```bash
   python my_app.py --json-exec "Settings/System/Muted" --value False
   # Output: {"status": "success", "message": "Settings/System/Muted updated directly in state", "value": false}
   ```

---

### Morse Code Processing & Audio Generation

#### EasyMorse
The `EasyMorse` class provides tools for converting text to Morse code signals.

```python
from cedbox import EasyMorse

# Create Morse code from text
morse = EasyMorse(text="SOS")
print(f"Original text: {morse.raw_text}")
print(f"Morse code: {morse.morse_code}")

# View the time sequence (1=dot, 3=dash, -1=pause between symbols)
print(f"Time sequence: {morse.morse_seq}")
```

#### EasyWav
The `EasyWav` class allows you to create WAV audio files from sequences of durations.

```python
from cedbox import EasyMorse, EasyWav

morse = EasyMorse(text="SOS")
wav = EasyWav(
    sequence=morse.morse_seq,
    frequency=800,
    time_unit=100
)
wav.save('morse_sos.wav')
```

#### EasyStream
The `EasyStream` class allows you to stream audio directly to your output device without creating intermediate files.

```python
from cedbox import EasyMorse, EasyStream

morse = EasyMorse(text="SOS")
stream = EasyStream(
    sequence=morse.morse_seq,
    frequency=800,
    time_unit=100
)
stream.stream()
```

---

### Yggdrasil

Yggdrasil is a hierarchical tree-like data structure that extends Python's dictionary with automatic node creation.

```python
from cedbox import Yggdrasil
import pandas as pd

# Create a new tree
tree = Yggdrasil()
tree['users']['john']['email'] = 'john@example.com'
tree['users']['john']['age'] = 30
tree.print_tree()
```

#### Creating from DataFrame / SQL
```python
df = pd.DataFrame({
    'name': ['John', 'Jane'],
    'email': ['john@example.com', 'jane@example.com'],
    'age': [30, 28]
})
tree_from_df = Yggdrasil.from_dataframe(df)
```

---

### Input Utilities

CedBox provides various functions for handling user input with validation and type conversion.

```python
from cedbox.inputs import string_put, int_put, bool_put

name = string_put("Enter your name: ")
age = int_put("Enter your age: ", conditions=[lambda x: 0 < x < 120])
confirm = bool_put("Confirm? ")
```

## Dependencies

- pandas >= 2.0.0
- sounddevice >= 0.5.2 (for audio streaming)

## License

See the [LICENSE](LICENSE) file for details.
