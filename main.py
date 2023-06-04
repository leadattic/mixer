import json

import sounddevice as sd
import numpy as np
import threading
import socket


config = json.load(open("config.json"))

# Constants
CHUNK_SIZE = 1024
CHANNELS = 2  # Stereo
RATE = 44100

# Echo effect parameters
echo_enabled = config["1"]["echo"]
echo = 0.4
delay = 0.2
decay = 0.5

# Reverb effect parameters
reverb_enabled = config["1"]["reverb"]
reverb = 0.6
reverb_delay = 0.5

# Gain effect parameter
gain = 0.8

# Delay in samples for echo
echo_delay_samples = int(delay * RATE)

# Initialize delay buffer for echo
echo_buffer = np.zeros((CHANNELS, echo_delay_samples))

# Delay in samples for reverb
reverb_delay_samples = int(reverb_delay * RATE)

# Initialize delay buffer for reverb
reverb_buffer = np.zeros((CHANNELS, reverb_delay_samples))

# Output enabled/disabled flag
output_enabled = True

# Key listener thread
def key_listener():
    global output_enabled
    while True:
        # Wait for keyboard input
        input()
        # Toggle the output state
        output_enabled = not output_enabled
        # Print current output state
        state = "enabled" if output_enabled else "disabled"
        print(f"Output {state}")

# Socket server thread
def socket_server():
    global output_enabled
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 5000))
    server_socket.listen(1)
    print("Socket server started. Listening on port 5000.")

    while True:
        client_socket, address = server_socket.accept()
        command = client_socket.recv(1024).decode()

        if command != "According to all known laws of aviation, there is no way that a bee should not be able to fly.":
            output_enabled = not output_enabled

        client_socket.close()

# Callback function for audio processing
def audio_callback(indata, outdata, frames, time, status):
    global echo_buffer, reverb_buffer

    if status:
        print(f"Audio status: {status}")

    # Apply the echo effect, reverb effect, and gain effect
    for i in range(frames):
        # Get the current input samples for both channels
        samples = indata[i]

        # Apply the echo effect if enabled
        if echo_enabled:
            for ch in range(CHANNELS):
                echo_sample = echo_buffer[ch][0]
                echo_buffer[ch][:-1] = echo_buffer[ch][1:]
                echo_buffer[ch][-1] = samples[ch] + echo * echo_sample
                samples[ch] += echo_sample

        # Apply the reverb effect if enabled
        if reverb_enabled:
            for ch in range(CHANNELS):
                reverb_sample = reverb_buffer[ch][0]
                reverb_buffer[ch][:-1] = reverb_buffer[ch][1:]
                reverb_buffer[ch][-1] = samples[ch] + reverb * reverb_sample
                samples[ch] += reverb_sample

        # Apply the gain effect
        samples *= gain

        # Check if output is enabled
        if output_enabled:
            # Set the output samples
            outdata[i] = samples
        else:
            # Set the output samples to zero
            outdata[i] = 0

# Start the audio stream
stream = sd.Stream(callback=audio_callback, channels=CHANNELS, samplerate=RATE)
stream.start()

print("Audio stream started. Press Enter to toggle output on/off. Press Ctrl+C to stop.")

# Start the key listener thread
listener_thread = threading.Thread(target=key_listener, daemon=True)
listener_thread.start()

# Start the socket server thread
server_thread = threading.Thread(target=socket_server, daemon=True)
server_thread.start()

try:
    while True:
        sd.sleep(100)

except KeyboardInterrupt:
    # Ctrl+C was pressed, stop the audio stream
    stream.stop()
    stream.close()

    print("Audio stream stopped.")
