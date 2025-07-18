import wave
import math
import struct


class EasyWav:
    def __init__(self, sequence: list[int], sample_rate=44100, frequency=440, time_unit=100):
        self.audio_samples: list[int] = []
        self.sample_rate: int = sample_rate
        self.frequency: int = frequency
        sequence: list[int] = [time_unit*seq for seq in sequence]
        self.sequence: list[int] = sequence
        self.from_seq(sequence)

    def _generate_samples(self, duration) -> list[int]:
        if duration > 0:  # Signal
            num_samples = int(abs(duration) * self.sample_rate / 1000)
            return [int(32767 * math.sin(2 * math.pi * self.frequency * (float(i) / self.sample_rate)))
                    for i in range(num_samples)]
        else:  # Pause
            num_samples = int(abs(duration) * self.sample_rate / 1000)
            return [0] * num_samples

    def from_seq(self, durations) -> None:
        audio_samples = []
        for duration in durations:
            audio_samples.extend(self._generate_samples(duration))
        self.audio_samples = audio_samples

    def save(self, filename='output.wav') -> None:
        with wave.open(filename, 'w') as wave_file:
            wave_file.setnchannels(1)
            wave_file.setsampwidth(2)
            wave_file.setframerate(self.sample_rate)
            wave_file.writeframes(struct.pack('h' * len(self.audio_samples), *self.audio_samples))


if __name__ == '__main__':
    data = [1, -1, 3, 1, -1, 3, 1, -1, 3, 1, -1, 3]
    wav = EasyWav(sequence=data)
    wav.save('output.wav')
