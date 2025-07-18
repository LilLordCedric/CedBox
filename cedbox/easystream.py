import math
import time

import numpy as np
import sounddevice as sd

from .easymorse import EasyMorse

class EasyStream:
    def __init__(self, sequence: list[int], sample_rate=44100, frequency=440, time_unit=100):
        """
        Initialize an EasyStream object for streaming audio directly from a sequence.

        Args:
            sequence: List of integers representing durations (positive for signal, negative for pause)
            sample_rate: Sample rate in Hz
            frequency: Frequency of the generated tone in Hz
            time_unit: Base time unit in milliseconds
        """
        self.audio_samples: list[float] = []
        self.sample_rate: int = sample_rate
        self.frequency: int = frequency
        self.time_unit: int = time_unit
        processed_sequence: list[int] = [time_unit*seq for seq in sequence]
        self.sequence: list[int] = processed_sequence

        # Generate audio samples from the sequence
        for duration in processed_sequence:
            self.audio_samples.extend(self._generate_samples(duration))

    def _generate_samples(self, duration) -> list[float]:
        """
        Generate audio samples for a given duration.

        Args:
            duration: Duration in milliseconds (positive for signal, negative for pause)

        Returns:
            List of audio samples
        """
        if duration > 0:  # Signal
            num_samples = int(abs(duration) * self.sample_rate / 1000)
            return [math.sin(2 * math.pi * self.frequency * (float(i) / self.sample_rate))
                    for i in range(num_samples)]
        else:  # Pause
            num_samples = int(abs(duration) * self.sample_rate / 1000)
            return [0.0] * num_samples


    def stream(self) -> None:
        """
        Stream the audio samples directly to the audio output device.
        """
        # Convert the list of samples to a numpy array
        audio_array = np.array(self.audio_samples, dtype=np.float32)

        # Play the audio
        sd.play(audio_array, self.sample_rate)
        sd.wait()  # Wait until the audio is finished playing

    def play_seq(self, sequence: list[int], time_unit=None) -> None:
        """
        Set a new sequence and stream it immediately.

        Args:
            sequence: List of integers representing durations (positive for signal, negative for pause)
            time_unit: Base time unit in milliseconds. If None, uses the current time_unit.
        """
        # Apply time_unit if provided, otherwise use the existing one
        if time_unit is not None:
            processed_sequence = [time_unit * seq for seq in sequence]
            self.time_unit = time_unit  # Update the time_unit attribute
        else:
            processed_sequence = [self.time_unit * seq for seq in sequence]

        # Update the sequence and generate audio samples
        self.sequence = processed_sequence
        self.audio_samples = []
        for duration in processed_sequence:
            self.audio_samples.extend(self._generate_samples(duration))

        # Stream the audio
        self.stream()


if __name__ == '__main__':
    # Example usage
    data = [1, -1, 1, -1, 3, -3, 1, -1, 1, -1, 3]
    audio_stream = EasyStream(sequence=data, time_unit=70)
    audio_stream.stream()

    time.sleep(2)

    seq = EasyMorse(text='ngfwf gjhej dhtje').morse_seq
    audio_stream.play_seq(seq)

