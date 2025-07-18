import unittest
from unittest.mock import patch
import pytest
from datetime import datetime
import pathlib
from cedbox.inputs import (
    string_put, int_put, float_put, choice_put,
    bool_put, file_put, date_put, mail_put
)


class TestStringPut(unittest.TestCase):
    """Tests for string_put function"""

    @patch('builtins.input', return_value='test input')
    def test_string_put_basic(self, mock_input):
        """Test basic string input"""
        result = string_put("Enter a string: ")
        mock_input.assert_called_once_with("Enter a string: ")
        assert result == 'test input'

    @patch('builtins.input', return_value='')
    def test_string_put_empty(self, mock_input):
        """Test empty string input"""
        result = string_put("Enter a string: ")
        assert result == ''

    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_string_put_max_times(self, mock_print, mock_input):
        """Test max_times parameter"""
        result = string_put("Enter a string: ", max_times=1, times=1, default='default value')
        assert result == 'default value'
        mock_print.assert_called_once()


class TestIntPut(unittest.TestCase):
    """Tests for int_put function"""

    @patch('builtins.input', return_value='42')
    def test_int_put_valid(self, mock_input):
        """Test valid integer input"""
        result = int_put("Enter an integer: ")
        assert result == 42

    @patch('builtins.input', side_effect=['invalid', '42'])
    @patch('builtins.print')
    def test_int_put_invalid_then_valid(self, mock_print, mock_input):
        """Test invalid input followed by valid input"""
        result = int_put("Enter an integer: ")
        assert result == 42
        assert mock_input.call_count == 2
        assert mock_print.call_count == 1

    @patch('builtins.input', return_value='42')
    def test_int_put_with_conditions(self, mock_input):
        """Test integer input with conditions"""
        result = int_put("Enter an integer: ", conditions=[lambda x: x > 0, lambda x: x < 100])
        assert result == 42

    @patch('builtins.input', side_effect=['invalid', 'invalid', 'invalid'])
    @patch('builtins.print')
    def test_int_put_max_times(self, mock_print, mock_input):
        """Test max_times parameter"""
        result = int_put("Enter an integer: ", max_times=3, times=1, default=99)
        assert result == 99
        assert mock_input.call_count == 3
        assert mock_print.call_count >= 3


class TestFloatPut(unittest.TestCase):
    """Tests for float_put function"""

    @patch('builtins.input', return_value='3.14')
    def test_float_put_valid(self, mock_input):
        """Test valid float input"""
        result = float_put("Enter a float: ")
        assert result == 3.14

    @patch('builtins.input', side_effect=['invalid', '3.14'])
    @patch('builtins.print')
    def test_float_put_invalid_then_valid(self, mock_print, mock_input):
        """Test invalid input followed by valid input"""
        result = float_put("Enter a float: ")
        assert result == 3.14
        assert mock_input.call_count == 2
        assert mock_print.call_count == 1


class TestChoicePut(unittest.TestCase):
    """Tests for choice_put function"""

    @patch('builtins.input', return_value='option1')
    def test_choice_put_valid(self, mock_input):
        """Test valid choice input"""
        result = choice_put("Choose an option: ", choices=['option1', 'option2', 'option3'])
        assert result == 'option1'

    @patch('builtins.input', side_effect=['invalid', 'option2'])
    @patch('builtins.print')
    def test_choice_put_invalid_then_valid(self, mock_print, mock_input):
        """Test invalid input followed by valid input"""
        result = choice_put("Choose an option: ", choices=['option1', 'option2', 'option3'])
        assert result == 'option2'
        assert mock_input.call_count == 2
        assert mock_print.call_count == 1


class TestBoolPut(unittest.TestCase):
    """Tests for bool_put function"""

    @patch('cedbox.inputs.choice_put', return_value='y')
    def test_bool_put_true(self, mock_choice_put):
        """Test boolean input returning True"""
        result = bool_put("Yes or no? ")
        assert result is True

    @patch('cedbox.inputs.choice_put', return_value='n')
    def test_bool_put_false(self, mock_choice_put):
        """Test boolean input returning False"""
        result = bool_put("Yes or no? ")
        assert result is False


class TestFilePut(unittest.TestCase):
    """Tests for file_put function"""

    @patch('builtins.input', return_value='/path/to/file')
    @patch('pathlib.Path.exists', return_value=True)
    def test_file_put_valid(self, mock_exists, mock_input):
        """Test valid file path input"""
        result = file_put("Enter a file path: ")
        assert result == pathlib.Path('/path/to/file')

    @patch('builtins.input', side_effect=['/invalid/path', '/valid/path'])
    @patch('pathlib.Path.exists', side_effect=[False, True])
    @patch('builtins.print')
    def test_file_put_invalid_then_valid(self, mock_print, mock_exists, mock_input):
        """Test invalid path followed by valid path"""
        result = file_put("Enter a file path: ")
        assert result == pathlib.Path('/valid/path')
        assert mock_input.call_count == 2
        assert mock_print.call_count == 1


class TestDatePut(unittest.TestCase):
    """Tests for date_put function"""

    @patch('builtins.input', return_value='2023-01-15')
    def test_date_put_valid(self, mock_input):
        """Test valid date input"""
        result = date_put("Enter a date: ")
        assert result == datetime(2023, 1, 15)

    @patch('builtins.input', side_effect=['invalid-date', '2023-01-15'])
    @patch('builtins.print')
    def test_date_put_invalid_then_valid(self, mock_print, mock_input):
        """Test invalid date followed by valid date"""
        result = date_put("Enter a date: ")
        assert result == datetime(2023, 1, 15)
        assert mock_input.call_count == 2
        assert mock_print.call_count == 1


class TestMailPut(unittest.TestCase):
    """Tests for mail_put function"""

    @patch('builtins.input', return_value='user@example.com')
    def test_mail_put_valid(self, mock_input):
        """Test valid email input"""
        result = mail_put("Enter an email: ")
        assert result == 'user@example.com'

    @patch('builtins.input', side_effect=['invalid-email', 'user@example.com'])
    @patch('builtins.print')
    def test_mail_put_invalid_then_valid(self, mock_print, mock_input):
        """Test invalid email followed by valid email"""
        result = mail_put("Enter an email: ")
        assert result == 'user@example.com'
        assert mock_input.call_count == 2
        assert mock_print.call_count == 1