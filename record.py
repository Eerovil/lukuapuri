import pyaudio
import wave
import os
import numpy as np
from collections import deque

# Define the list of sounds to record
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'y', 'ä', 'ö']

vowels = ['a', 'e', 'i', 'o', 'u', 'y', 'ä', 'ö']

# Upper case all
letters = [s.upper() for s in letters]
vowels = [s.upper() for s in vowels]

consonants = [s for s in letters if s not in vowels]

# Define the list of sounds to record

sounds = [s for s in letters]

# Double vowels
for v in vowels:
    sounds.append(v + v)

# consonant + vowel
for c in consonants:
    for v in vowels:
        sounds.append(c + v)

# consonant + double vowel
for c in consonants:
    for v in vowels:
        sounds.append(c + v + v)

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
THRESHOLD = 1000  # Adjust this value for sensitivity
SILENCE_DURATION = 0.2  # Duration in seconds to consider as silence
BACKLOG_DURATION = 0.3  # Duration in seconds to keep as backlog
OUTPUT_FOLDER = 'recordings'

# Create output folder if it doesn't exist
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Function to check if the input audio signal is silent
def is_silent(data):
    audio_data = np.frombuffer(data, dtype=np.int16)
    return np.abs(audio_data).mean() < THRESHOLD

# Function to record sound based on sound detection with backlog
def record_sound(filename, sound, next_sound):
    print(f"{sound} -> {next_sound}")

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    backlog = deque(maxlen=int(BACKLOG_DURATION * RATE / CHUNK))
    frames = []
    silent_chunks = 0
    recording = False

    while True:
        data = stream.read(CHUNK)
        if not recording:
            backlog.append(data)
            if not is_silent(data):
                print("Recording started...")
                frames.extend(backlog)  # Add backlog frames to the recording
                recording = True
        else:
            frames.append(data)
            if is_silent(data):
                silent_chunks += 1
            else:
                silent_chunks = 0

            if silent_chunks > SILENCE_DURATION * RATE / CHUNK:
                break

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Save the recording
    if frames:
        wave_file = wave.open(filename, 'wb')
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(audio.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()
        print(f"Recorded: {filename}")

# Remove existing recordings from sounds list
missing_sounds = []
for sound in sounds:
    filename = os.path.join(OUTPUT_FOLDER, f"{sound}.wav")
    if not os.path.exists(filename):
        missing_sounds.append(sound)

sounds = missing_sounds

print(f"Missing sounds: {len(sounds)}")

# Loop through each sound and record
i = -1
for sound in sounds:
    i += 1
    next_sound = sounds[i + 1] if i + 1 < len(sounds) else None
    filename = os.path.join(OUTPUT_FOLDER, f"{sound}.wav")
    record_sound(filename, sound, next_sound)

# Terminate PyAudio
audio.terminate()
