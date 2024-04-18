import argparse
import os
import subprocess
import json
import argparse
import yt_dlp

video_id = "lodo-O_Ejfw"
video_url = "https://www.youtube.com/watch?v=" + video_id
output_dir = r"D:\study\singaporeMasters\master project\text-cleaning-2022\manual\raw_vtts"
out_path = output_dir + "/" + video_id + "_%(title)s.%(ext)s"
#out_path = output_dir + "/" + video_id # + ".vtt"
subprocess.run(["yt-dlp", "--write-auto-sub", "--sub-format", "vtt", "--verbose", video_url, "-o", out_path])

#
# os.chdir(r"D:\study\singaporeMasters\master project\text-cleaning-2022\manual")
# fd = open("Jen Tan Property_video_ids.txt", "w+")
# os.chdir(r"D:\study\singaporeMasters\master project\text-cleaning-2022\manual\transcripts\Jen Tan Property")
# for file in os.listdir():
#     if file.endswith(".txt"):
#         fd.writelines(file[:-4] + '\n')
# fd.close()
