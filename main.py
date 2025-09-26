import os
import sys
import librosa
import numpy

def clean_up():
    old_files = os.listdir("./imgs/")
    for file in old_files:
        os.remove(f"./imgs/{file}")

def get_data_at_time(audio_data, sample_rate, time) -> (float, str):
    index = int(time * sample_rate)
    if index > len(audio_data):
        return (None, "Data out of range.")
    else:
        if index < len(audio_data):
            return (numpy.abs(audio_data[index]), None)
        else:
            return (None, "Index out of range")

if len(sys.argv) != 2:
    print("Usage: main.py [output name].mp4")
elif ".mp4" != sys.argv[1][len(sys.argv[1])-4:len(sys.argv[1])]:
    sys.argv[1] = sys.argv[1] + ".mp4"

if os.path.exists("./imgs"):
    clean_up()
else:
    os.makedirs("./imgs")

audio_data, sample_rate = librosa.load('./res/audio.mp3', sr=24000)

i = 0
error = None
volumes_to_analyze = []
while error == None:
    volume, error = get_data_at_time(audio_data, sample_rate, i * (1/24))
    if error == None:
        volumes_to_analyze.append(volume)
    i += 1

average_volume = sum(volumes_to_analyze)/len(volumes_to_analyze)

i = 0
for volume in volumes_to_analyze:
    if volume > average_volume:
        os.symlink(os.path.abspath("./res/open.jpg"), f"./imgs/{i:06}.jpg")
    else:
        os.symlink(os.path.abspath("./res/closed.jpg"), f"./imgs/{i:06}.jpg")
    i += 1

os.system(f"""ffmpeg -loglevel error -framerate 48 -pattern_type glob -i "./imgs/*.jpg" -i "./res/audio.mp3" -c:a aac -c:v h264 {sys.argv[1]}""")

clean_up()
