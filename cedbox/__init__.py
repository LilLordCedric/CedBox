"""
CedBox - A Python utility package for data handling, input validation, Morse code processing, and audio generation.
"""

from cedbox.yggdrasil import Yggdrasil
from cedbox.inputs import (
    string_put, int_put, float_put, choice_put, 
    bool_put, file_put, date_put, mail_put
)
from cedbox.easymorse import EasyMorse, MORSE_CODE_DICT
from cedbox.easywav import EasyWav
from cedbox.easystream import EasyStream

__version__ = "0.1.0"
