# -*- coding: utf-8 -*-
import pyaudio
import wave

def record(fname, record_time):
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 44100
	RECORD_SECONDS = record_time
	WAVE_OUTPUT_FILENAME = fname

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					input=True,
					frames_per_buffer=CHUNK)

	print("Start to record the audio.")

	frames = []

	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		data = stream.read(CHUNK)
		frames.append(data)

	print("Recording is finished.")

	stream.stop_stream()
	stream.close()
	p.terminate()

	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()

def main():
	fname = raw_input('Input Save File(.wav): ')
	record_time = raw_input('Iput Record Time(s): ')
	record(fname, int(record_time))
	
if __name__ == '__main__':
	main()