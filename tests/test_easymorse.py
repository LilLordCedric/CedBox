import unittest
from cedbox.easymorse import EasyMorse, MORSE_CODE_DICT


class TestEasyMorse(unittest.TestCase):
    """Tests for EasyMorse class"""

    def test_init_default(self):
        """Test initialization with default parameters"""
        morse = EasyMorse()
        self.assertIsNotNone(morse.morse_dict)
        self.assertIn('A', morse.morse_dict)
        self.assertEqual(morse.morse_dict['A'], '_'.join(MORSE_CODE_DICT['A']))
        self.assertEqual(morse.morse_dict[' '], '|')
        self.assertFalse(hasattr(morse, 'text'))
        self.assertFalse(hasattr(morse, 'seq'))

    def test_init_with_text(self):
        """Test initialization with text parameter"""
        morse = EasyMorse(text='SOS')
        self.assertTrue(hasattr(morse, 'text'))
        self.assertTrue(hasattr(morse, 'seq'))
        # SOS in Morse is ... --- ...
        # With _ between dots/dashes and ! between characters
        self.assertEqual(morse.text, '._._.!-_-_-!._._.')
        # Default times and brakes: . = 1, - = 3, _ = -1, ! = -3, | = -7
        expected_seq = [1, -1, 1, -1, 1, -3, 3, -1, 3, -1, 3, -3, 1, -1, 1, -1, 1]
        self.assertEqual(morse.seq, expected_seq)

    def test_init_with_custom_times_and_brakes(self):
        """Test initialization with custom times and brakes"""
        custom_times = {'.': 2, '-': 6}
        custom_brakes = {'_': -2, '!': -6, '|': -14}
        morse = EasyMorse(text='SOS', times=custom_times, brakes=custom_brakes)
        # SOS in Morse is ... --- ...
        # With _ between dots/dashes and ! between characters
        expected_seq = [2, -2, 2, -2, 2, -6, 6, -2, 6, -2, 6, -6, 2, -2, 2, -2, 2]
        self.assertEqual(morse.seq, expected_seq)

    def test_init_with_spaces(self):
        """Test initialization with text containing spaces"""
        morse = EasyMorse(text='S O S')
        # S O S in Morse is ... | --- | ...
        # With _ between dots/dashes, ! between characters, and | for spaces
        self.assertEqual(morse.text, '._._.|-_-_-|._._.')
        # Check that !|! is replaced with |
        self.assertNotIn('!|!', morse.text)

    def test_init_with_invalid_chars(self):
        """Test initialization with text containing invalid characters"""
        morse = EasyMorse(text='S#O@S')
        # Invalid characters should be filtered out
        self.assertEqual(morse.text, '._._.!-_-_-!._._.')

    def test_init_with_lowercase(self):
        """Test initialization with lowercase text"""
        morse = EasyMorse(text='sos')
        # Should convert to uppercase
        self.assertEqual(morse.text, '._._.!-_-_-!._._.')

    def test_char_to_seq_method(self):
        """Test the char_to_seq method"""
        morse = EasyMorse()
        self.assertEqual(morse.char_to_seq('A'), '_'.join(MORSE_CODE_DICT['A']))
        self.assertEqual(morse.char_to_seq(' '), '|')

    def test_empty_text(self):
        """Test initialization with empty text"""
        morse = EasyMorse(text='')
        # Empty text should not create text and seq attributes
        self.assertFalse(hasattr(morse, 'text'))
        self.assertFalse(hasattr(morse, 'seq'))

    def test_all_characters(self):
        """Test all characters in the MORSE_CODE_DICT"""
        for char in MORSE_CODE_DICT:
            if len(char) == 1 and char not in [',', '.']:  # Skip multi-character keys for simplicity
                morse = EasyMorse(text=char)
                expected_text = '_'.join(MORSE_CODE_DICT[char])
                self.assertEqual(morse.text, expected_text)


if __name__ == '__main__':
    unittest.main()
