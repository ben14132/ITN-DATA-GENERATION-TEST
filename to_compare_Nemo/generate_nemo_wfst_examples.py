import argparse
import json
import os

import pynini
from nemo_text_processing.text_normalization.normalize import Normalizer


def align(raw_str: str, normalized: str) -> list:
    raw_split = raw_str.split()
    raw_split.append('/end')
    normalized_split = normalized.split()
    normalized_split.append('/end')
    aligned = []
    raw_idx = 0
    raw_len = len(raw_split)
    normalized_flag = False
    normalized_start = -1
    to_normalize = []
    for word in normalized_split:
        if raw_idx >= raw_len:
            break
        if word == raw_split[raw_idx] and not normalized_flag:
            aligned.append(word + '\t' + '<self>' + '\n')
            raw_idx += 1
        else:
            if not normalized_flag:
                normalized_flag = True
                normalized_start = raw_idx
                to_normalize.append(word)
                raw_idx += 1
            else:
                tmp = raw_idx
                while tmp < raw_len and raw_split[tmp] != word:
                    tmp += 1
                if tmp == raw_len:
                    to_normalize.append(word)
                    continue
                aligned.append(' '.join(raw_split[normalized_start: tmp]) + '\t' + ' '.join(to_normalize) + '\n')
                aligned.append(raw_split[tmp] + '\t' + '<self>' + '\n')
                to_normalize = []
                normalized_flag = False
                raw_idx = tmp + 1
                pass
    if normalized_flag:
        aligned.append(' '.join(raw_split[normalized_start:]) + '\t' + ' '.join(to_normalize) + '\n')

    return aligned[:-1]


def generate_transcript(input_dir: str, output_dir: str) -> None:
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        youtube_url = file_name[:11]
        transcript = []
        with open(file_path, 'r+') as fp:
            lines = fp.readlines()
            for line in lines:
                transcript.append(line.split()[0])

        output_file_path = os.path.join(output_dir, youtube_url)
        with open(output_file_path + '.txt', 'w+') as out_fp:
            out_fp.write(' '.join(transcript))


def generate_nemo_example(input_dir: str, output_dir: str) -> None:
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    normalizer = Normalizer(input_case='cased', lang='en')
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        normalized = None
        with open(file_path, 'r+') as fp:
            line = fp.readline()
            normalized = normalizer.normalize(line, verbose=True, punct_post_process=True)

        output_file_path = os.path.join(output_dir, file_name)
        with open(output_file_path, 'w+') as out_fp:
            out_fp.write(normalized)


def generate_nemo_example_segmented(input_dir: str, output_dir: str) -> None:
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    aligned_dir = os.path.join(output_dir, 'aligned')
    if not os.path.exists(aligned_dir):
        os.mkdir(aligned_dir)

    normalizer = Normalizer(input_case='cased', lang='en')
    for url in os.listdir(input_dir):
        url_dir_path = os.path.join(input_dir, url)
        normalized = None
        output_file_path = os.path.join(output_dir, url)

        aligned_file_path = os.path.join(aligned_dir, url)

        aligned_fp = open(aligned_file_path + '.txt', 'w+')
        out_fp = open(output_file_path + '.txt', 'w+')
        for file_name in os.listdir(url_dir_path):
            file_path = os.path.join(url_dir_path, file_name)
            if os.path.isdir(file_path):
                continue

            with open(file_path, 'r+') as fp:
                line = fp.readline()
                normalized = normalizer.normalize(line, verbose=True, punct_post_process=True)
                out_fp.write(normalized + ' ')
                aligned_word = align(line, normalized)
                aligned_fp.writelines(aligned_word)

        out_fp.close()


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--json", required=True)
    # args = parser.parse_args()
    #
    # with open(args.json, "r") as j_obj:
    #     config = json.load(j_obj)

    config = {
        "generate_transcript": {
            "input_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\youtube_crawler\\Chris@HoneyMoneySG\\youtube_timestamp",
            "output_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\youtube_crawler\\Chris@HoneyMoneySG\\youtube_transcript"
        },
        "nemo_example": {
            "mode": "segmented",
            "segmented_transcript_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\youtube_crawler\\Chris@HoneyMoneySG\\segmented_wav",
            "output_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\youtube_crawler\\Chris@HoneyMoneySG\\nemo_result",
            "output_aligned_dir": "D:\\study\\singaporeMasters\\master_project\\term2\\data\\youtube_crawler\\Chris@HoneyMoneySG\\nemo_result_aligned"
        }
    }

    input_dir = config["generate_transcript"]["input_dir"]
    output_dir = config["generate_transcript"]["output_dir"]
    nemo_example_output_dir = config["nemo_example"]["output_dir"]
    mode = config["nemo_example"]["mode"]
    segmented_transcript_dir = config["nemo_example"]["segmented_transcript_dir"]

    # generate_transcript(input_dir, output_dir)

    if mode == "segmented":
        generate_nemo_example_segmented(segmented_transcript_dir, nemo_example_output_dir)
    else:
        generate_nemo_example(output_dir, nemo_example_output_dir)


if __name__ == "__main__":
    # normalizer = Normalizer(input_case='cased', lang='en')
    # line = "FPGA 23 45th ants refuse to sign on 2022 annual file"
    #
    # line = line.strip()
    # line = pynini.escape(line)
    # tagged_lattice = normalizer.find_tags(line)
    # tagged_text = normalizer.select_tag(tagged_lattice)
    # normalizer.parser(tagged_text)
    # tokens = normalizer.parser.parse()
    # split_tokens = normalizer._split_tokens_to_reduce_number_of_permutations(tokens)
    # output = ""
    # for s in split_tokens:
    #     tags_reordered = normalizer.generate_permutations(s)
    #     verbalizer_lattice = None
    #     for tagged_text in tags_reordered:
    #         tagged_text = pynini.escape(tagged_text)
    #
    #         verbalizer_lattice = normalizer.find_verbalizer(tagged_text)
    #         if verbalizer_lattice.num_states() != 0:
    #             break
    #     if verbalizer_lattice is None:
    #         raise ValueError(f"No permutations were generated from tokens {s}")
    #     final_token = Normalizer.select_verbalizer(verbalizer_lattice)
    #     b = 1
    #
    # tagged_text = Normalizer.select_tag(tagged_lattice)
    # normalized = normalizer.normalize(line, verbose=True, punct_post_process=True)
    main()
