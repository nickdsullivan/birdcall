import socket
import struct
import numpy as np
from scipy.io.wavfile import write
from scipy.signal import butter, filtfilt, sosfiltfilt
import time
import timeit
import noisereduce as nr
class UDPListener:
    def __init__(self, output_path, main_queue, DURATION):
        UDP_IP = "0.0.0.0"
        UDP_PORT = 5005
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))
        
        self.SAMPLE_RATE = 16000
        self.DURATION = DURATION
        self.NUM_SAMPLES = self.SAMPLE_RATE * self.DURATION

        self.queue = main_queue
        self.output_path = output_path


        print(f"Listening on UDP port {UDP_PORT} saving to {self.output_path}")


    def run(self):
        audio_buffer = []
        while True:
            data, _ = self.sock.recvfrom(4096)  # large buffer to receive 1024 samples
            samples = struct.unpack('<' + 'h'*(len(data) // 2), data)
            audio_buffer.extend(samples)
            
            if len(audio_buffer) >= self.NUM_SAMPLES:
                # start = timeit.default_timer()
                self.save_chunk(audio_buffer[:self.NUM_SAMPLES])
                audio_buffer = audio_buffer[self.NUM_SAMPLES:] 
                # elapsed = timeit.default_timer() - start
        
        
    def highpass_filter(self, y, cutoff=2000, order=6):
        """
        High-pass filter for bird vocalizations.
        y must be float32 in range [-1, 1]
        """
        sos = butter(
            order,
            cutoff,
            btype="highpass",
            fs=self.SAMPLE_RATE,
            output="sos"
        )
        return sosfiltfilt(sos, y)


    def rms_normalize(self, y, target_db=-20):
        """
        Normalize audio to target RMS level (safe, no clipping).
        """
        rms = np.sqrt(np.mean(y ** 2))
        scalar = 10 ** (target_db / 20) / (rms + 1e-9)
        y = y * scalar
        return np.clip(y, -1.0, 1.0)
    def save_chunk(self, samples):


        
            audio_np = np.array(samples, dtype=np.int16)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = self.output_path + f"/audio_{timestamp}.wav"
            # audio_np = self.highpass_filter(audio_np, cutoff=2000, fs=16000)
           
            # Save as WAV  
            # audio_np = self.rms_normalize(audio_np, target_db=-20)
            
            # audio_np = nr.reduce_noise(
            #     audio_np,
            #     sr=self.SAMPLE_RATE,
            #     stationary=True,
            #     prop_decrease=0.4
            # )
            # audio_np = np.clip(audio_np, -32768, 32767).astype(np.int16)
            write(filename, self.SAMPLE_RATE, audio_np)
            self.queue.put(filename)


    # def save_chunk(self, samples):
    #     # Convert int16 -> float32 [-1, 1]
    #     y = np.asarray(samples, dtype=np.float32) / 32768.0

    #     # 1️⃣ High-pass filter (critical for sparrows)
    #     y = self.highpass_filter(y, cutoff=2000)

    #     # 2️⃣ RMS normalize
    #     y = self.rms_normalize(y, target_db=-20)

    #     # 3️⃣ Light noise reduction (do NOT overdo)
    #     y = nr.reduce_noise(
    #         y=y,
    #         sr=self.SAMPLE_RATE,
    #         stationary=True,
    #         prop_decrease=0.4
    #     )

    #     # Convert back to int16 for WAV
    #     audio_int16 = np.clip(y * 32768, -32768, 32767).astype(np.int16)

    #     # Save
    #     timestamp = time.strftime("%Y%m%d_%H%M%S")
    #     filename = f"{self.output_path}/audio_{timestamp}.wav"
    #     print("Saving audio")
    #     write(filename, self.SAMPLE_RATE, audio_int16)

    #     # Queue for BirdNET
    #     self.queue.put(filename)



    