import unittest
import os
import wave
import struct
import math
from cedbox.easywav import EasyWav


class TestEasyWav(unittest.TestCase):
    """Tests for EasyWav class"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_sequence = [1, -1, 3, -3]
        self.test_filename = 'test_output.wav'

    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_init_default(self):
        """Test initialization with default parameters"""
        wav = EasyWav(self.test_sequence)
        self.assertEqual(wav.sample_rate, 44100)
        self.assertEqual(wav.frequency, 440)
        self.assertEqual(wav.sequence, [100, -100, 300, -300])  # Scaled by time_unit
        self.assertTrue(len(wav.audio_samples) > 0)

    def test_init_custom_params(self):
        """Test initialization with custom parameters"""
        wav = EasyWav(self.test_sequence, sample_rate=22050, frequency=880, time_unit=200)
        self.assertEqual(wav.sample_rate, 22050)
        self.assertEqual(wav.frequency, 880)
        self.assertEqual(wav.sequence, [200, -200, 600, -600])  # Scaled by time_unit
        self.assertTrue(len(wav.audio_samples) > 0)

    def test_generate_samples_positive_duration(self):
        """Test _generate_samples with positive duration (signal)"""
        wav = EasyWav([])  # Empty sequence for testing just the method
        samples = wav._generate_samples(100)  # 100ms of signal

        # Check that samples are generated
        self.assertTrue(len(samples) > 0)

        # Check that at least one sample is non-zero (sine wave should have non-zero values)
        self.assertTrue(any(sample != 0 for sample in samples))

        # Check that number of samples matches expected duration
        expected_samples = int(100 * wav.sample_rate / 1000)
        self.assertEqual(len(samples), expected_samples)

    def test_generate_samples_negative_duration(self):
        """Test _generate_samples with negative duration (pause)"""
        wav = EasyWav([])  # Empty sequence for testing just the method
        samples = wav._generate_samples(-100)  # 100ms of silence

        # Check that samples are generated
        self.assertTrue(len(samples) > 0)

        # Check that all samples are zero (silence)
        self.assertTrue(all(sample == 0 for sample in samples))

        # Check that number of samples matches expected duration
        expected_samples = int(100 * wav.sample_rate / 1000)
        self.assertEqual(len(samples), expected_samples)

    def test_from_seq(self):
        """Test from_seq method"""
        wav = EasyWav([])  # Empty sequence
        test_durations = [100, -100, 300]
        wav.from_seq(test_durations)

        # Check that audio samples are generated
        self.assertTrue(len(wav.audio_samples) > 0)

        # Calculate expected number of samples
        expected_samples = sum(int(abs(d) * wav.sample_rate / 1000) for d in test_durations)
        self.assertEqual(len(wav.audio_samples), expected_samples)

    def test_save(self):
        """Test save method creates a valid WAV file"""
        wav = EasyWav(self.test_sequence)
        wav.save(self.test_filename)

        # Check that file exists
        self.assertTrue(os.path.exists(self.test_filename))

        # Check that file is a valid WAV file
        with wave.open(self.test_filename, 'r') as wave_file:
            self.assertEqual(wave_file.getnchannels(), 1)
            self.assertEqual(wave_file.getsampwidth(), 2)
            self.assertEqual(wave_file.getframerate(), wav.sample_rate)

            # Check that file contains the correct number of frames
            self.assertEqual(wave_file.getnframes(), len(wav.audio_samples))

    def test_save_custom_filename(self):
        """Test save method with custom filename"""
        custom_filename = 'custom_test_output.wav'
        try:
            wav = EasyWav(self.test_sequence)
            wav.save(custom_filename)

            # Check that file exists
            self.assertTrue(os.path.exists(custom_filename))
        finally:
            # Clean up
            if os.path.exists(custom_filename):
                os.remove(custom_filename)

    def test_audio_content(self):
        """Test that the generated audio content matches expectations"""
        # Simple sequence with just one tone
        wav = EasyWav([1], time_unit=10)  # 10ms tone

        # First few samples should follow a sine wave pattern
        expected_first_sample = int(32767 * math.sin(2 * math.pi * 440 * (0 / 44100)))
        self.assertEqual(wav.audio_samples[0], expected_first_sample)

        # Check a few more samples to ensure the pattern is correct
        sample_index = 100
        expected_sample = int(32767 * math.sin(2 * math.pi * 440 * (sample_index / 44100)))
        self.assertEqual(wav.audio_samples[sample_index], expected_sample)


if __name__ == '__main__':
    unittest.main()
