import argparse
import json
import os
import shutil


def contain_digit(in_str) -> bool:
    for s in in_str:
        if s.isdigit():
            return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True)
    args = parser.parse_args()

    with open(args.json, "r") as j_obj:
        config = json.load(j_obj)

    # config = {
    #     "get_vtt_and_clean": {
    #         "video_ids_dir": "D:\\study\\singaporeMasters\\master project\\text-cleaning-2022\\manual\\transcripts\\Chicken Genius Singapore",
    #         "raw_vtt_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\youtube-dl-output\\raw_vtt_dir",
    #         "normalized_vtt_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\youtube-dl-output\\normalized_vtt_dir",
    #         "word_time_split_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\youtube-dl-output\\word_time_split_dir"
    #     },
    #     "folder_path": "D:\\study\\singaporeMasters\\master project\\text-cleaning-2022\\manual\\transcripts\\Chicken Genius Singapore",
    #     "get_wenet_output": {
    #         "wenet_input_wav_dir": ""
    #     },
    #     "align": {
    #         "youtube_word_time_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\youtube_crawler\\Chris@HoneyMoneySG\\youtube_timestamp",
    #         "wenet_word_time_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\youtube_crawler\\Chris@HoneyMoneySG\\wenet_transcript",
    #         "wenet_masked_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\youtube_crawler\\Chris@HoneyMoneySG\\wenet_transcript_masked",
    #         "output_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\youtube_crawler\\Chris@HoneyMoneySG\\itn_dataset"
    #     }
    # }

    youtube_word_time_dir = config["align"]["youtube_word_time_dir"]
    wenet_word_time_dir = config["align"]["wenet_word_time_dir"]
    output_dir = config["align"]["output_dir"]
    wenet_masked_dir = config["align"]["wenet_masked_dir"]

    youtube_transcript_time = dict()

    # for wenet_word_time_sub_dir in os.listdir(wenet_word_time_dir):
    #     wenet_word_time_sub_dir_path = os.path.join(wenet_word_time_dir, wenet_word_time_sub_dir)
    #
    #     wenet_masked_sub_dir_path = os.path.join(wenet_masked_dir, wenet_word_time_sub_dir)
    #     if not os.path.exists(wenet_masked_sub_dir_path):
    #         os.mkdir(wenet_masked_sub_dir_path)
    #     else:
    #         shutil.rmtree(wenet_masked_sub_dir_path)
    #         os.mkdir(wenet_masked_sub_dir_path)
    # get youtube word time
    for youtube_word_time_file in os.listdir(youtube_word_time_dir):
        youtube_word_time_file_path = os.path.join(youtube_word_time_dir, youtube_word_time_file)
        file_name = youtube_word_time_file[:11]
        with open(youtube_word_time_file_path, 'r+') as youtube_f:
            try:
                youtube_transcript_time[file_name] = []
                lines = youtube_f.readlines()
                for line in lines:
                    line_split = line.split()
                    youtube_transcript_time[file_name].append(
                        [line_split[0], int(line_split[1]), int(line_split[2])])
            except Exception as e:
                print(e)
                youtube_transcript_time.pop(file_name, 'no key ' + file_name)

    for filename in os.listdir(wenet_word_time_dir):
        # filename = str(filename)
        if not filename.endswith("_timestamp.txt"):
            continue
        original_filename = str(filename[:-14])
        youtube_url = original_filename[:11]

        if original_filename == '-UUcOKNMYmg_130640_133680':
            a = 1

        wenet_masked_file_path = os.path.join(wenet_masked_dir,
                                              original_filename + "_masked.txt")
        youtube_word_time_path = os.path.join(youtube_word_time_dir, original_filename[:11] + '.txt')
        wenet_word_time_path = os.path.join(wenet_word_time_dir, filename)

        if not os.path.exists(wenet_masked_file_path) or not os.path.exists(youtube_word_time_path):
            pass

        if youtube_url not in youtube_transcript_time.keys():
            continue
        youtube_word_time = youtube_transcript_time[youtube_url]

        # allocate wenet word time
        times = original_filename.split('_')  # -2=file start time -1 = file end time
        times[-2] = int(times[-2])
        times[-1] = int(times[-1])
        wenet_word_time = []
        with open(wenet_word_time_path, 'r+') as wenet_f:
            lines = wenet_f.readlines()
            for line in lines:
                line = line.split()
                line[1] = int(line[1]) + int(times[-2])
                wenet_word_time.append([line[0], line[1]])
                if len(wenet_word_time) > 1:
                    wenet_word_time[-2].append(line[1])
        if len(wenet_word_time) == 0:
            continue
        wenet_word_time[-1].append(int(times[-1]))  # each item: word, actual start, actual end

        # read masked wenet word
        wenet_masked_word = []
        with open(wenet_masked_file_path, 'r+') as wenet_mask_f:
            line = wenet_mask_f.readline()
            wenet_masked_word = line.split()
        end_time = wenet_masked_file_path.split('_')[-1][:-4]

        # assign masked with time
        wenet_masked_word_time = []
        word_time_idx = 0
        word_time_length = len(wenet_word_time)
        num_flag = False
        start_idx = -1
        for word in wenet_masked_word:
            if word_time_idx >= word_time_length:
                break
            if word == wenet_word_time[word_time_idx][0]:
                wenet_masked_word_time.append(
                    ["<self>", word, wenet_word_time[word_time_idx][1], wenet_word_time[word_time_idx][2]])
                word_time_idx += 1
            else:
                if word == "<num>":
                    num_flag = True
                    start_idx = word_time_idx
                else:

                    while word_time_idx < word_time_length and not word == wenet_word_time[word_time_idx][0]:
                        word_time_idx += 1
                    if word_time_idx == word_time_length:
                        break
                    else:
                        tmp_str_list = []
                        for i in range(start_idx, word_time_idx):
                            tmp_str_list.append(wenet_word_time[i][0])
                        wenet_masked_word_time.append(
                            ["<num>", ' '.join(tmp_str_list), wenet_word_time[start_idx][1],
                             wenet_word_time[word_time_idx][1]])
                        num_flag = False
                        wenet_masked_word_time.append(
                            ["<self>", word, wenet_word_time[word_time_idx][1], wenet_word_time[word_time_idx][2]])
                        word_time_idx += 1
        if num_flag is True:
            tmp_str_list = []
            for i in range(start_idx, word_time_length):
                tmp_str_list.append(wenet_word_time[i][0])
            wenet_masked_word_time.append(
                ["<num>", ' '.join(tmp_str_list), wenet_word_time[start_idx][1], times[-1]])
        # formed: label, word(s), start time, end time

        # find wenet segment time slot
        time_slot = [-1, -1]
        cnt = 0
        for idx, item in enumerate(youtube_word_time):
            if item[1] == times[-2]:
                time_slot[0] = idx
            if item[2] == times[-2]:
                time_slot[0] = idx + 1
            if item[1] == times[-1]:
                time_slot[1] = idx
            if item[2] == times[-1]:
                time_slot[1] = idx + 1
            if time_slot[0] != -1 and time_slot[1] != -1:
                break

        youtube_word_time = youtube_word_time[time_slot[0]: time_slot[1]]
        youtube_word_time_idx = 0
        youtube_word_time_length = time_slot[1] - time_slot[0]
        result = ["" for i in range(youtube_word_time_length)]
        visited = [0] * youtube_word_time_length
        for item in wenet_masked_word_time:
            if youtube_word_time_idx >= youtube_word_time_length:
                break
            if item[0] == "<num>":
                guess_start = int(item[2]) - 350
                guess_end = int(item[3]) + 100

                try:
                    if len(youtube_word_time[youtube_word_time_idx]) < 3:
                        b = 1
                except Exception as e:
                    c = 1
                while youtube_word_time[youtube_word_time_idx][2] <= guess_start:
                    youtube_word_time_idx += 1

                youtube_num_idx = []
                while youtube_word_time_idx < youtube_word_time_length and youtube_word_time[youtube_word_time_idx][
                    1] <= guess_end:
                    youtube_num_idx.append(youtube_word_time_idx)
                    youtube_word_time_idx += 1

                for possible_idx in youtube_num_idx:
                    if contain_digit(youtube_word_time[possible_idx][0]):
                        result[possible_idx] = youtube_word_time[possible_idx][0] + '\t' + item[1] + '\n'
                        visited[possible_idx] = 1
                        youtube_word_time_idx = possible_idx + 1
                        break

                # while youtube_word_time_idx < youtube_word_time_length and youtube_word_time[youtube_word_time_idx][
                #     2] < item[2]:
                #     youtube_word_time_idx += 1
                # if youtube_word_time_idx < youtube_word_time_length:
                #     result[youtube_word_time_idx - 1] = youtube_word_time[youtube_word_time_idx - 1][0] + '\t' + \
                #                                         item[1]
                #     visited[youtube_word_time_idx - 1] = 1

        for idx, boo in enumerate(visited):
            if boo == 0:
                result[idx] = youtube_word_time[idx][0] + '\t' + "<self>" + '\n'

        with open(os.path.join(output_dir, original_filename) + '.txt', 'w+') as f:
            f.writelines(result)


if __name__ == "__main__":
    main()
