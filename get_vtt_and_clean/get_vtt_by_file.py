"""
Author: Charangan Vasantharajan
Date: 05/04/2022
Description: This script is to get VTT files from YT
Args:
    Inputs
        video_ids_dir (str): string to input folder directory [Required]
        raw_vtt_dir (str): string to output vtt file directory [Required]
"""

import argparse
import os
import subprocess
import json
import argparse

def check_dir(dir2chk,verbose=False):
	if not os.path.isdir(dir2chk):	
		if verbose:
			print('Making directory:',dir2chk)
		os.makedirs(dir2chk)
	else:
		if verbose:
			print('Directory',dir2chk,'exists, moving on')

def get_vtt_file(video_id, output_dir):
    video_url = "https://www.youtube.com/watch?v=" + video_id
    out_path = output_dir + "/" + video_id + "_%(title)s.%(ext)s"
    #out_path = output_dir + "/" + video_id # + ".vtt"
    subprocess.run(["yt-dlp", "--write-auto-sub", "--skip-download", video_url, "-o", out_path])


# ------------------------------------------------------------------------------------------ #

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--json", required=True)
    # args = parser.parse_args()
    #
    # with open(args.json, "r") as j_obj:
    #     config = json.load(j_obj)

    config = {
        "sentence_segmentation": {
            "input_type": "folder",
            "path": "D:\\study\\singaporeMasters\\master project\\text-cleaning-2022\\manual\\transcripts\\Chicken Genius Singapore"
        },
        "sentence_segmentation_with_times": {
            "input_type": "folder",
            "path": "get_vtt_and_clean/normalized_vtt"
        },
        "get_vtt_and_clean": {
            "video_ids_dir": "D:\\study\\singaporeMasters\\master project\\text-cleaning-2022\\manual",
            "raw_vtt_dir": "D:\\study\\singaporeMasters\\master project\\text-cleaning-2022\\manual\\raw_vtts\\Jen Tan Property",
            "normalized_vtt_dir": "D:\\study\\singaporeMasters\\master project\\text-cleaning-2022\\manual\\normalized_vtts\\Chicken Genius Singapore"
        },
        "folder_path": "D:\\study\\singaporeMasters\\master project\\text-cleaning-2022\\manual\\transcripts\\Chicken Genius Singapore"
    }

    # Check whether the specified path exists or not
    video_ids_dir = config["get_vtt_and_clean"]["video_ids_dir"]
    raw_vtt_dir = config["get_vtt_and_clean"]["raw_vtt_dir"]

    # video_ids_dir = os.path.join(
    # 	str(video_ids_dir), '')
    assert os.path.isdir(
    	video_ids_dir), f'Directory {video_ids_dir} does not exist.'

    os.chdir(video_ids_dir)

    if(not os.path.exists(raw_vtt_dir)):
        os.makedirs(raw_vtt_dir)
    
    for file in os.listdir():
        if file.endswith(".txt"):
            with open(os.path.join(video_ids_dir,file), 'r') as rf:
                video_ids = rf.readlines()

            for video_id in video_ids:
                video_id = video_id[:-1]
                try:
                    get_vtt_file(video_id, raw_vtt_dir)
                except Exception as e:
                    print(e)

            print("Finished!")


if __name__ == "__main__":
    main()


