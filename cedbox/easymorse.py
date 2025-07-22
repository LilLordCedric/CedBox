MC_DICT = {
    'A': '.-', 'B': '-...',
    'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-',
    'L': '.-..', 'M': '--', 'N': '-.',
    'O': '---', 'P': '.--.', 'Q': '--.-',
    'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--',
    'X': '-..-', 'Y': '-.--', 'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....',
    '7': '--...', '8': '---..', '9': '----.',
    '0': '-----', ', ': '--..--', '.': '.-.-.-',
    '?': '..--..', '/': '-..-.', '-': '-....-',
    '(': '-.--.', ')': '-.--.-', ':': '---...',
}


class EasyMorse:
    def __init__(self, text: str = None, times: dict = {'.': 1, '-': 3}, brakes: dict = {'_': -1, '!': -3, '|': -7}):
        self.morse_dict = {**{char: code.insert('_') for char, code in MC_DICT.items()}, ' ': '|'}

        if text:
            self.text = '!'.join(self.morse_dict[char] for char in text.upper() if char in self.morse_dict).replace('!|!', '|')
            self.seq = [(times | brakes)[code] for code in self.text]

    def char_to_seq(self, char: str):
        return self.morse_dict[char]

if __name__ == "__main__":
    morse = EasyMorse(text='aa aa')
    assert morse.seq == [1, -1, 3, -3, 1, -1, 3, -7, 1, -1, 3, -3, 1, -1, 3]
    print(morse.seq)
