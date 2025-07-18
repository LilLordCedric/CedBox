# CedBox

CedBox is a Python utility package that provides various tools for data handling, user input validation, Morse code processing, and audio generation.

## Features

- **Yggdrasil**: A hierarchical tree-like data structure that extends Python's dictionary, with support for:
  - Automatic node creation
  - Loading data from DataFrames and SQL queries
  - Tree visualization

- **Input Utilities**: Functions for handling user input with validation and type conversion:
  - String input
  - Integer input with validation
  - Float input with validation
  - Choice selection
  - Boolean (yes/no) input
  - File path input with validation
  - Date input with validation
  - Email input with validation

- **Morse Code Processing**: Tools for working with Morse code:
  - Convert text to Morse code
  - Represent Morse code as time units
  - Generate Morse code sequences

- **Audio Generation**: Utilities for creating WAV audio files:
  - Generate audio signals from sequences of durations
  - Create Morse code audio signals

## Installation

```bash
pip install cedbox
```

## Usage Examples

### Yggdrasil

Yggdrasil is a hierarchical tree-like data structure that extends Python's dictionary with additional functionality.

```python
from cedbox import Yggdrasil
import pandas as pd

# Create a new tree
tree = Yggdrasil()

# Add data with automatic node creation
tree['users']['john']['email'] = 'john@example.com'
tree['users']['john']['age'] = 30
tree['users']['jane']['email'] = 'jane@example.com'
tree['users']['jane']['age'] = 28

# Print tree structure
tree.print_tree()
```

**Output:**
```
Yggdrasil
├── users
│   ├── john
│   │   ├── email: john@example.com
│   │   └── age: 30
│   └── jane
│       ├── email: jane@example.com
│       └── age: 28
```

#### Creating from DataFrame

```python
# Create from DataFrame
df = pd.DataFrame({
    'name': ['John', 'Jane'],
    'email': ['john@example.com', 'jane@example.com'],
    'age': [30, 28]
})
tree_from_df = Yggdrasil.from_dataframe(df)
tree_from_df.print_tree()
```

**Output:**
```
Yggdrasil
├── 0
│   ├── name: John
│   ├── email: john@example.com
│   └── age: 30
└── 1
    ├── name: Jane
    ├── email: jane@example.com
    └── age: 28
```

#### Creating from SQL Query

```python
import sqlite3

# Create a sample database
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute('CREATE TABLE users (name TEXT, email TEXT, age INTEGER)')
cursor.execute('INSERT INTO users VALUES ("John", "john@example.com", 30)')
cursor.execute('INSERT INTO users VALUES ("Jane", "jane@example.com", 28)')
conn.commit()

# Create tree from SQL query
tree_from_sql = Yggdrasil.from_sql("SELECT * FROM users", conn)
tree_from_sql.print_tree()
```

**Output:**
```
Yggdrasil
├── 0
│   ├── name: John
│   ├── email: john@example.com
│   └── age: 30
└── 1
    ├── name: Jane
    ├── email: jane@example.com
    └── age: 28
```

### Input Utilities

CedBox provides various functions for handling user input with validation and type conversion.

```python
from cedbox.inputs import (
    string_put, int_put, float_put, choice_put, 
    bool_put, file_put, date_put, mail_put
)

# String input
name = string_put("Enter your name: ")
# User enters: John
print(f"Hello, {name}!")
# Output: Hello, John!

# Integer input with validation
age = int_put(
    "Enter your age: ", 
    conditions=[lambda x: x > 0, lambda x: x < 120],
    max_times=3,
    default=30
)
# User enters: -5
# Output: -5 is not valid assert lambda x: x > 0
# User enters: 25
print(f"You are {age} years old.")
# Output: You are 25 years old.

# Float input with validation
height = float_put(
    "Enter your height in meters: ",
    conditions=[lambda x: 0.5 < x < 2.5],
    default=1.75
)
# User enters: 1.85
print(f"Your height is {height} meters.")
# Output: Your height is 1.85 meters.

# Choice selection
color = choice_put("Select a color ", choices=['red', 'green', 'blue'])
# Output: Select a color (red/green/blue): 
# User enters: yellow
# Output: yellow is not valid
# User enters: red
print(f"You selected {color}.")
# Output: You selected red.

# Boolean input
confirm = bool_put("Confirm? ")
# Output: Confirm? (y/n): 
# User enters: y
print(f"Confirmed: {confirm}")
# Output: Confirmed: True
```

### Morse Code Processing

The EasyMorse class provides tools for working with Morse code.

```python
from cedbox import EasyMorse

# Create Morse code from text
morse = EasyMorse(text="SOS")
print(f"Original text: {morse.raw_text}")
# Output: Original text: SOS

print(f"Morse code: {morse.morse_code}")
# Output: Morse code: ._._.____-_-_-___._._._

# View the time sequence (1=dot, 3=dash, -1=pause between symbols)
print(f"Time sequence: {morse.morse_seq}")
# Output: Time sequence: [1, -1, 1, -1, 1, -1, -1, -1, 3, -1, 3, -1, 3, -1, -1, -1, 1, -1, 1, -1, 1]

# Create with custom prefix (VVV- is a common Morse prefix)
morse_with_prefix = EasyMorse(text="HELLO", prefix=True)
print(f"With prefix: {morse_with_prefix.morse_message}")
# Output: With prefix: ._._._-___._._._-___._._._-___-_._._._._-_____._._._.___._____._____._._..___._..___._..___---

# Create an instance to use the char_to_seq method
morse_instance = EasyMorse()
sequence = morse_instance.char_to_seq('A')
print(f"Sequence for 'A': {sequence}")
# Output: Sequence for 'A': [1, -1, 3]

# Use a custom Morse code dictionary
custom_dict = {'X': '....'}  # X as four dots
sequence = morse_instance.char_to_seq('X', custom_dict)
print(f"Custom sequence for 'X': {sequence}")
# Output: Custom sequence for 'X': [1, -1, 1, -1, 1, -1, 1]
```

### Audio Generation

#### EasyWav

The EasyWav class allows you to create WAV audio files from sequences of durations.

```python
from cedbox import EasyMorse, EasyWav

# Create Morse code sequence for "SOS"
morse = EasyMorse(text="SOS")
sequence = morse.morse_seq
print(f"Morse sequence: {sequence}")
# Output: Morse sequence: [1, -1, 1, -1, 1, -1, -1, -1, 3, -1, 3, -1, 3, -1, -1, -1, 1, -1, 1, -1, 1]

# Generate WAV file from sequence
wav = EasyWav(
    sequence=sequence,
    frequency=800,  # 800 Hz tone
    time_unit=100   # 100ms per unit
)
wav.save('morse_sos.wav')
print("Audio file created: morse_sos.wav")
# Output: Audio file created: morse_sos.wav

# Create a more complex audio pattern
custom_sequence = [1, -1, 3, -1, 1, -3, 5, -5]  # Custom pattern of tones and pauses
wav = EasyWav(
    sequence=custom_sequence,
    frequency=440,  # A4 note
    sample_rate=48000  # Higher quality
)
wav.save('custom_pattern.wav')
```

#### EasyStream

The EasyStream class allows you to stream audio directly to your audio output device without creating intermediate files.

```python
from cedbox import EasyMorse, EasyStream
import time

# Create Morse code sequence for "SOS"
morse = EasyMorse(text="SOS")
sequence = morse.morse_seq

# Stream audio directly to output device
stream = EasyStream(
    sequence=sequence,
    frequency=800,  # 800 Hz tone
    time_unit=100   # 100ms per unit
)
stream.stream()  # Play the audio

# Wait a moment before playing another sequence
time.sleep(2)

# Play a different sequence without creating a new EasyStream object
new_sequence = [1, -1, 3, -1, 1, -3, 5, -5]  # Custom pattern
stream.play_seq(new_sequence)

# Play another sequence with a different time unit (faster)
stream.play_seq([3, -1, 1, -1, 3], time_unit=50)
```

## Complete Examples

### Morse Code to WAV Converter

Here's a complete example that combines multiple components to create a Morse code to WAV converter:

```python
from cedbox import EasyMorse, EasyWav, string_put

def morse_wav_converter():
    # Get input text from user
    text = string_put("Enter text to convert to Morse code: ")

    # Convert to Morse code
    morse = EasyMorse(text, prefix=True)

    print(f"Text: {morse.raw_text}")
    print(f"Morse code: {morse.morse_code}")

    # Generate audio file
    wav = EasyWav(
        sequence=morse.morse_seq,
        frequency=800,
        time_unit=80  # Faster speed
    )

    filename = f"morse_{text.replace(' ', '_')}.wav"
    wav.save(filename)
    print(f"Audio saved to {filename}")

    return morse, filename

# Run the converter
morse_result, audio_file = morse_wav_converter()
```

### Morse Code Streaming

Here's an example that uses EasyStream to play Morse code directly:

```python
from cedbox import EasyMorse, EasyStream, string_put
import time

def morse_streamer():
    # Get input text from user
    text = string_put("Enter text to convert to Morse code: ")

    # Convert to Morse code
    morse = EasyMorse(text, prefix=True)

    print(f"Text: {morse.raw_text}")
    print(f"Morse code: {morse.morse_code}")
    print("Playing Morse code...")

    # Stream the audio
    stream = EasyStream(
        sequence=morse.morse_seq,
        frequency=800,
        time_unit=80  # Faster speed
    )
    stream.stream()

    # Ask if user wants to hear it again at a different speed
    if string_put("Play again at a different speed? (y/n): ").lower() == 'y':
        new_time_unit = int(string_put("Enter new time unit (ms, e.g., 50 for faster): "))
        print(f"Playing at {new_time_unit}ms time unit...")
        stream.play_seq(morse.morse_seq, time_unit=new_time_unit)

    return morse

# Run the streamer
morse_result = morse_streamer()
```

## Dependencies

- pandas >= 2.0.0
- sounddevice >= 0.5.2 (for audio streaming)

## License

See the [LICENSE](LICENSE) file for details.
