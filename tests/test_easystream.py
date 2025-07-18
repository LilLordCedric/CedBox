import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from cedbox.easystream import EasyStream


class TestEasyStream(unittest.TestCase):
    """Tests for EasyStream class"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_sequence = [1, -1, 3, -3]

    @patch('cedbox.easystream.sd')
    def test_init_default(self, mock_sd):
        """Test initialization with default parameters"""
        stream = EasyStream(self.test_sequence)
        self.assertEqual(stream.sample_rate, 44100)
        self.assertEqual(stream.frequency, 440)
        self.assertEqual(stream.time_unit, 100)
        self.assertEqual(stream.sequence, [100, -100, 300, -300])  # Scaled by time_unit
        self.assertTrue(len(stream.audio_samples) > 0)

    @patch('cedbox.easystream.sd')
    def test_init_custom_params(self, mock_sd):
        """Test initialization with custom parameters"""
        stream = EasyStream(self.test_sequence, sample_rate=22050, frequency=880, time_unit=200)
        self.assertEqual(stream.sample_rate, 22050)
        self.assertEqual(stream.frequency, 880)
        self.assertEqual(stream.time_unit, 200)
        self.assertEqual(stream.sequence, [200, -200, 600, -600])  # Scaled by time_unit
        self.assertTrue(len(stream.audio_samples) > 0)

    def test_generate_samples_positive_duration(self):
        """Test _generate_samples with positive duration (signal)"""
        with patch('cedbox.easystream.sd'):
            stream = EasyStream([])  # Empty sequence for testing just the method
            samples = stream._generate_samples(100)  # 100ms of signal

            # Check that samples are generated
            self.assertTrue(len(samples) > 0)

            # Check that at least one sample is non-zero (sine wave should have non-zero values)
            self.assertTrue(any(sample != 0 for sample in samples))

            # Check that number of samples matches expected duration
            expected_samples = int(100 * stream.sample_rate / 1000)
            self.assertEqual(len(samples), expected_samples)

    def test_generate_samples_negative_duration(self):
        """Test _generate_samples with negative duration (pause)"""
        with patch('cedbox.easystream.sd'):
            stream = EasyStream([])  # Empty sequence for testing just the method
            samples = stream._generate_samples(-100)  # 100ms of silence

            # Check that samples are generated
            self.assertTrue(len(samples) > 0)

            # Check that all samples are zero (silence)
            self.assertTrue(all(sample == 0 for sample in samples))

            # Check that number of samples matches expected duration
            expected_samples = int(100 * stream.sample_rate / 1000)
            self.assertEqual(len(samples), expected_samples)

    @patch('cedbox.easystream.sd')
    def test_stream(self, mock_sd):
        """Test stream method"""
        stream = EasyStream(self.test_sequence)
        stream.stream()

        # Check that play was called with the correct arguments
        mock_sd.play.assert_called_once()

        # Get the arguments passed to play
        args, kwargs = mock_sd.play.call_args

        # Check that the first argument is a numpy array with the correct shape
        self.assertIsInstance(args[0], np.ndarray)
        self.assertEqual(len(args[0]), len(stream.audio_samples))

        # Check that the second argument is the sample rate
        self.assertEqual(args[1], stream.sample_rate)

        # Check that wait was called
        mock_sd.wait.assert_called_once()

    @patch('cedbox.easystream.sd')
    def test_play_seq_default_time_unit(self, mock_sd):
        """Test play_seq method with default time unit"""
        stream = EasyStream([])  # Empty initial sequence
        new_sequence = [2, -2, 4]
        stream.play_seq(new_sequence)

        # Check that sequence was updated
        self.assertEqual(stream.sequence, [200, -200, 400])  # Scaled by default time_unit (100)

        # Check that audio samples were generated
        self.assertTrue(len(stream.audio_samples) > 0)

        # Check that play was called
        mock_sd.play.assert_called_once()

        # Check that wait was called
        mock_sd.wait.assert_called_once()

    @patch('cedbox.easystream.sd')
    def test_play_seq_custom_time_unit(self, mock_sd):
        """Test play_seq method with custom time unit"""
        stream = EasyStream([], time_unit=100)  # Empty initial sequence
        new_sequence = [2, -2, 4]
        new_time_unit = 200
        stream.play_seq(new_sequence, time_unit=new_time_unit)

        # Check that time_unit was updated
        self.assertEqual(stream.time_unit, new_time_unit)

        # Check that sequence was updated with new time_unit
        self.assertEqual(stream.sequence, [400, -400, 800])  # Scaled by new time_unit (200)

        # Check that audio samples were generated
        self.assertTrue(len(stream.audio_samples) > 0)

        # Check that play was called
        mock_sd.play.assert_called_once()

        # Check that wait was called
        mock_sd.wait.assert_called_once()

    @patch('cedbox.easystream.sd')
    def test_audio_content(self, mock_sd):
        """Test that the generated audio content matches expectations"""
        # Simple sequence with just one tone
        stream = EasyStream([1], time_unit=10)  # 10ms tone

        # First few samples should follow a sine wave pattern
        expected_first_sample = np.sin(2 * np.pi * 440 * (0 / 44100))
        self.assertAlmostEqual(stream.audio_samples[0], expected_first_sample)

        # Check a few more samples to ensure the pattern is correct
        sample_index = 100
        expected_sample = np.sin(2 * np.pi * 440 * (sample_index / 44100))
        self.assertAlmostEqual(stream.audio_samples[sample_index], expected_sample)


if __name__ == '__main__':
    unittest.main()
