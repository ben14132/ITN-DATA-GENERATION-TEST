import argparse
import json
import os
from _pydecimal import Decimal

from unicodedata import decimal


def google_dataset_preprocess(input_dir:str, output_dir:str, separated=True):
    file_names = []
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        if os.path.isdir(file_path):
            continue
        with open(file_path, 'r', encoding='utf-8') as in_fp: #, encoding='utf-8'
            lines =  in_fp.readlines()
            out_fp = None
            cnt_file = 0
            cnt = 0
            spoken = []
            written = []
            type = []
            out_fp = open(os.path.join(output_dir, file_name + "-" + str(cnt_file).zfill(7)), 'w', encoding='utf-8')
            file_names.append(file_name + "-" + str(cnt_file).zfill(7))
            for line in lines:
                line_split = line.split('\t')
                if len(line_split) == 2 and line_split[0] == "<eos>":
                    cnt += 1
                    out_fp.write(" ".join(written) + " ||| " + " ".join(spoken) + " ||| " + " ".join(type) + "\n")
                    spoken.clear()
                    written.clear()
                    type.clear()
                    if cnt % 50 == 0 and separated is True:
                        out_fp.close()
                        cnt_file += 1
                        out_fp = open(os.path.join(output_dir, file_name + "-" + str(cnt_file).zfill(7)), 'w', encoding='utf-8')
                        file_names.append(file_name + "-" + str(cnt_file).zfill(7))
                    continue
                if len(line_split) == 3:
                    if line_split[0] == "PLAIN" or line_split[0] == "PUNCT":
                        line_split[2] = line_split[1]
                    written.append(line_split[1].strip())
                    spoken.append(line_split[2].strip())
                    type.append(line_split[0].strip())
        out_fp.close()

        # break
    return file_names


def cal_wer():
    path = r"D:\study\singaporeMasters\master_project\term2\data\google_text_normalization_dataset\en_with_types_sentence_ChatGPT\wer.txt"

    with open(path, "r", encoding="utf-8") as fp:
        cnt = 0
        sum = 0
        lines = fp.readlines()
        for line in lines:
            wer = float(line.strip())
            if wer < 0:
                continue
            sum += wer
            cnt += 1
    print(cnt)
    print(sum/cnt)




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True)
    args = parser.parse_args()

    with open(args.json, "r") as j_obj:
        config = json.load(j_obj)

    # config = {
    #     "text_generate": {
    #         "api_key":
    #         "input_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\youtube_crawler\\Chris@HoneyMoneySG\\segmented_text_with_times",
    #         "output_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\youtube_crawler\\Chris@HoneyMoneySG\\chatGPT"
    #     },
    #     "preprocess": {
    #         "input_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\google_text_normalization_dataset\\en_with_types",
    #         "output_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\google_text_normalization_dataset\\en_with_types_sentence",
    #         "log":""
    #     }
    # }

    google_dataset_preprocess(config["preprocess"]["input_dir"], config["preprocess"]["output_dir"])
    pass


if __name__ == "__main__":
    # main()
    cal_wer()