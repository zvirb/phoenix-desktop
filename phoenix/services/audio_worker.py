import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QDateTime
from PyQt6.QtMultimedia import QAudioSource, QAudioFormat, QMediaDevices

import wave
import os
from datetime import datetime

# ... imports ...

class AudioWorker(QObject):
    levels_ready = pyqtSignal(list)
    recording_finished = pyqtSignal(str) # Path to saved file
    
    def __init__(self):
        super().__init__()
        self.source = None
        self.io = None
        self.is_running = False
        self.is_recording = False
        self.recorded_frames = []
        self.audio_format = None # Store to use in wave write

    # ... start() ...
        # After format selected:
        self.audio_format = format
    # ...

    def set_recording(self, recording):
        if recording:
            print("AudioWorker: Recording STARTED")
            self.recorded_frames = []
            self.is_recording = True
        else:
            print("AudioWorker: Recording STOPPED")
            self.is_recording = False
            self.save_recording()
            
    def save_recording(self):
        if not self.recorded_frames:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voice_note_{timestamp}.wav"
        
        # Ensure directory exists
        save_dir = os.path.join(os.getcwd(), "captures")
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, filename)
        
        try:
            # We need to convert list of bytes/arrays to single bytes
            raw_data = b''.join(self.recorded_frames)
            
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2) # Int16 = 2 bytes
                wf.setframerate(16000)
                wf.writeframes(raw_data)
                
            print(f"AudioWorker: Saved {len(raw_data)} bytes to {filepath}")
            self.recording_finished.emit(filepath)
            
        except Exception as e:
            print(f"AudioWorker: Save failed: {e}")
        
        self.recorded_frames = []

    def read_data(self):
        self.last_read_time = QDateTime.currentMSecsSinceEpoch()
        
        if not self.io: return
        qbyte_array = self.io.readAll()
        if qbyte_array.size() == 0: return
        
        data = qbyte_array.data()
        
        # Capture if recording
        if self.is_recording:
            self.recorded_frames.append(data)
            
        # ... rest of FFT logic ...
        
    def start(self):
        if self.is_running: return
        
        device = QMediaDevices.defaultAudioInput()
        if not device or device.isNull():
            print("AudioWorker: No default audio input device found.")
            return 
            
        print(f"AudioWorker: Using device {device.description()}")
        
        format = device.preferredFormat()
        # Ensure we can work with it (we expect Int16 usually, but let's check)
        # Actually, let's try to request what we want, and if not supported, take nearest.
        
        req_format = QAudioFormat()
        req_format.setSampleRate(16000)
        req_format.setChannelCount(1)
        req_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        
        if not device.isFormatSupported(req_format):
            print("AudioWorker: Requested format not supported, using preferred.")
            format = device.preferredFormat()
        else:
            format = req_format
            
        print(f"AudioWorker: Selected Format - SampleRate: {format.sampleRate()}, ChannelCount: {format.channelCount()}, SampleFormat: {format.sampleFormat()}")

        self.source = QAudioSource(device, format)
        self.source.setBufferSize(1024) # ~30ms latency for 16kHz Int16
        
        self.io = self.source.start()
        if self.io:
            self.io.readyRead.connect(self.read_data)
            self.is_running = True
            print("AudioWorker: Started capture.")
            
        else:
            print("AudioWorker: Failed to start QAudioSource.")

        # Watchdog to ensure we don't stall
        self.watchdog_timer = QTimer()
        self.watchdog_timer.timeout.connect(self.check_activity)
        self.watchdog_timer.start(2000)
        self.last_read_time = QDateTime.currentMSecsSinceEpoch()

    def check_activity(self):
        now = QDateTime.currentMSecsSinceEpoch()
        if now - self.last_read_time > 2000 and self.is_running:
            print("AudioWorker watchdog: Stream stalled, restarting...")
            self.stop()
            self.start()

    def stop(self):
        if hasattr(self, 'watchdog_timer'):
            self.watchdog_timer.stop()
            
        if self.source:
            self.source.stop()
            self.source = None
            self.io = None
        self.is_running = False
            
    def read_data(self):
        self.last_read_time = QDateTime.currentMSecsSinceEpoch()
        
        if not self.io: return
        # Read available bytes
        qbyte_array = self.io.readAll()
        if qbyte_array.size() == 0: return
        
        # Convert to numpy
        # Int16 -> 2 bytes
        # Must ensure event length is even
        data = qbyte_array.data()
        
        # Capture if recording
        if self.is_recording:
            self.recorded_frames.append(data)
            
        # Handle odd bytes just in case
        if len(data) % 2 != 0:
            data = data[:-1]
            
        if len(data) < 256: 
            return # Process even small chunks
        
        try:
            samples = np.frombuffer(data, dtype=np.int16)
            
            # FFT
            # Take last 512 samples for resolution, padding if needed
            fft_samples = samples
            if len(samples) < 512:
                fft_samples = np.pad(samples, (0, 512 - len(samples)), 'constant')
            elif len(samples) > 1024:
                fft_samples = samples[-1024:]
            
            # Windowing
            window = np.hanning(len(fft_samples))
            fft_result = np.fft.rfft(fft_samples * window)
            magnitude = np.abs(fft_result)
            
            # We want 20 bars
            # Skip 0Hz (DC offset)
            magnitude = magnitude[1:]
            
            num_bins = len(magnitude)
            bars = 20
            
            # Logarithmic mapping (Mel-like) often looks better, 
            # but linear chunking is safer for simple viz.
            # Let's do simple linear integration for now.
            chunk_size = max(1, num_bins // bars)
            
            levels = []
            for i in range(bars):
                start = i * chunk_size
                end = min((i + 1) * chunk_size, num_bins)
                if start >= end: break
                
                # Average magnitude in this band
                avg = np.mean(magnitude[start:end])
                levels.append(avg)
                
            # Pad if needed
            while len(levels) < bars:
                levels.append(0.0)
                
            levels = np.array(levels)
            
            # BOOOST GAIN!
            # Log scale: log10(v + 1)
            # Input magnitude can be small.
            levels = np.log10(levels + 1) 
            
            # Normalization factor. 
            # If max magnitude is ~1000 => log is 3. 
            # We want full height (1.0) for standard speech.
            # Adjusted to 5.5 to prevent saturation
            levels = levels / 5.5
            
            # Linear fine tune
            levels = levels * 1.0 
            
            levels = np.clip(levels, 0.0, 1.0)
            
            self.levels_ready.emit(levels.tolist())
            
        except Exception as e:
            print(f"AudioWorker Error: {e}")
