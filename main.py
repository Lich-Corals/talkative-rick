# Talkative-Rick - Make him say anything
# Copyright (C) 2025  Linus Tibert
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public Licence as published
# by the Free Software Foundation, either version 3 of the Licence, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public Licence for more details.
#
# You should have received a copy of the GNU Affero General Public Licence
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import math
import numpy
import librosa

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

def get_standard_deviation(data, average) -> float:
    sum = 0
    for i in range(len(data)):
        sum += (data[i] - average) ** 2
    standard_deviation = math.sqrt( sum * (1 / (len(data) - 1)) )
    return standard_deviation


check_ffmpeg = os.system("ffmpeg -version")
if check_ffmpeg != 0:
    print("ffmpeg not executeable!")
    exit()

output_file = ""
audio_input = "./res/audio.mp3"
averaging_mode = "--averaging-global"
averaging_tolerance = 1.0
if len(sys.argv) < 2 or len(sys.argv) > 4:
    print("Usage: main.py (--averaging-[global|padded|local]_[tolarance]) (audio_file) [output name]\nOptional arguments in (brackets); obligatory arguments in [square brackets].")
    exit()
else:
    output_file = sys.argv[len(sys.argv) - 1]
    match len(sys.argv):
        case 3:
            if "--averaging-" in sys.argv[1]:
                averaging_mode = sys.argv[1].split("_")[0]
                averaging_tolerance = float(sys.argv[1].split("_")[1])
            else:
                audio_input = sys.argv[1]
        case 4:
            audio_input = sys.argv[2]
            averaging_mode = sys.argv[1].split("_")[0]
            averaging_tolerance = float(sys.argv[1].split("_")[1])
    if ".mp4" != output_file[len(output_file)-4:len(output_file)]:
        output_file += ".mp4"

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
    open = False
    match averaging_mode:
        case "--averaging-global":
            open = volume > average_volume
        case "--averaging-padded":
            standard_deviation = get_standard_deviation(volumes_to_analyze, average_volume)
            open = volume + standard_deviation*averaging_tolerance > average_volume
        case "--averaging-local":
            local_range = 12
            local_range_add = local_range
            if i + local_range >= len(volumes_to_analyze):
                local_range_add = len(volumes_to_analyze) - i - 1
            dataset = volumes_to_analyze[i-local_range:i+local_range_add]
            dataset_average = sum(dataset)/(len(dataset) + 1)
            standard_deviation = get_standard_deviation(dataset, dataset_average)
            open = volume + standard_deviation*averaging_tolerance > dataset_average
    if open:
        os.symlink(os.path.abspath("./res/open.jpg"), f"./imgs/{i:06}.jpg")
    else:
        os.symlink(os.path.abspath("./res/closed.jpg"), f"./imgs/{i:06}.jpg")
    i += 1

print(f"Creating {output_file} with audio data from {audio_input}...")

os.system(f"""ffmpeg -loglevel error -framerate 48 -pattern_type glob -i "./imgs/*.jpg" -i "{audio_input}" -c:a aac -c:v h264 {output_file}""")

clean_up()
