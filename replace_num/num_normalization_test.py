import sys
sys.path.append(r"D:\study\singaporeMasters\master_project\chng-pipeline")

import os
import number_replace
import cal_wer as cal_wer


def check_value(v) -> bool:
    '''check string is a number or not'''
    if v.isdigit():
        return True
    elif v.isascii():
        items = v.split('.')
        if len(items) == 2 and items[0].isdigit() and items[1].isdigit():
            return True
        else:
            return False
    else:
        return False


#
def main(wav_path: str, original_text_path: str, to_normalize_text_path: str, out_path: str) -> None:
    """
    wav_path: path to store wav file
    original_text_path: texts from Youtube. format: "time time text" *n in one file
    to_normalize_text_path: result from WeNET. format: "filename time time"
    out_path: output path
    """
    original_text_dict = dict()
    last_key = None
    for file_name in os.listdir(original_text_path):
        file_path = os.path.join(original_text_path, file_name)
        with open(file_path, 'r+') as f:
            lines = f.readlines()
            for line in lines:
                line_split = line.split()
                if check_value(line_split[0]) and check_value(line_split[1]):
                    last_key = os.path.splitext(file_name)[-2] + "_" + str(
                        int(float(line_split[0]) * 1000)) + "-" + str(int(float(line_split[1]) * 1000))
                    original_text_dict[last_key] = " ".join(line_split[2:])
                else:
                    last_text = original_text_dict[last_key]
                    last_text = last_text[:-2] + " " + line
                    original_text_dict[last_key] = last_text

    for file_name in os.listdir(to_normalize_text_path):
        file_pure_name = os.path.splitext(file_name)[-2]
        extension = os.path.splitext(file_name)[-1]
        if file_pure_name in original_text_dict.keys():
            example_text = original_text_dict[file_pure_name]
            print(example_text)
            with open(os.path.join(to_normalize_text_path, file_name), "r+") as f:
                line = f.readline()
                line_handled = " ".join(line.split()[3:])
                normalized_text = number_replace.try_method(example_text, line_handled, "<num>")
                wer = cal_wer.cal_wer_jiwerr(example_text, [(file_pure_name, normalized_text)])[0][1]['wer']
                a = 1
                file_path = os.path.join(out_path, file_pure_name)
                # with open(file_path + "_original.txt", 'w+') as out_f:
                #     # out_f.writelines('wer: ' + str(wer) + '\n')
                #     out_f.writelines(example_text)
                # with open(file_path + "_wenet.txt", 'w+') as out_f:
                #     # out_f.writelines('wer: ' + str(wer) + '\n')
                #     out_f.writelines(line_handled)
                with open(file_path + "_wenet_num_masked.txt", 'w+') as out_f:
                    # out_f.writelines('wer: ' + str(wer) + '\n')
                    out_f.writelines(normalized_text)
                    #out_f.writelines('generated: ' + normalized_text + '\n')

    return


def fix():
    to_normalize_text_path = r"D:\study\singaporeMasters\master project\data\result_on_wenet"
    out_path = r"D:\study\singaporeMasters\master project\data\out_path_new"
    for file_name in os.listdir(to_normalize_text_path):
        with open(os.path.join(to_normalize_text_path, file_name), "r+") as f:
            line = f.readline()
            with open(os.path.join(out_path, file_name), 'w+') as out_f:
                out_f.writelines(line.split("wer: ")[0])


def run_text_number_replace(wav_path: str, original_text_path: str, to_normalize_text_path: str, out_path: str) -> None:
    """
    wav_path: path to store wav file
    original_text_path: texts from Youtube. format: "text text" in one file
    to_normalize_text_path: result from WeNET. format: "filename_time_time_timestamp.txt"
    out_path: output path
    """
    original_text_dict = dict()
    last_key = None
    for file_name in os.listdir(original_text_path):
        file_path = os.path.join(original_text_path, file_name)
        if not file_name.endswith('.txt'):
            continue
        with open(file_path, 'r+') as f:
            line = f.readline()
            original_text_dict[file_name[:-4]] = line

    for file_name in os.listdir(to_normalize_text_path):
        if not file_name.endswith('_transcript.txt'):
            continue
        file_pure_name = os.path.splitext(file_name)[-2][:-11]
        extension = os.path.splitext(file_name)[-1]
        if file_pure_name in original_text_dict.keys():
            example_text = original_text_dict[file_pure_name]
            print(example_text)
            with open(os.path.join(to_normalize_text_path, file_name), "r+") as f:
                line = f.readline()
                line_handled = line #" ".join(line.split()[3:])
                normalized_text = number_replace.try_method(example_text, line_handled, "<num>")
                wer = cal_wer.cal_wer_jiwerr(example_text, [(file_pure_name, normalized_text)])[0][1]['wer']
                a = 1
                file_path = os.path.join(out_path, file_pure_name)
                # with open(file_path + "_original.txt", 'w+') as out_f:
                #     # out_f.writelines('wer: ' + str(wer) + '\n')
                #     out_f.writelines(example_text)
                # with open(file_path + "_wenet.txt", 'w+') as out_f:
                #     # out_f.writelines('wer: ' + str(wer) + '\n')
                #     out_f.writelines(line_handled)
                with open(file_path + "_masked.txt", 'w+') as out_f:
                    # out_f.writelines('wer: ' + str(wer) + '\n')
                    out_f.writelines(normalized_text)
                    #out_f.writelines('generated: ' + normalized_text + '\n')

    return


def run_text_number_replace_folder(wav_path: str, original_text_path: str, to_normalize_text_path: str, out_path: str) -> None:
    """
       wav_path: path to store wav file
       original_text_path: texts from Youtube sub folders. format: "text text" in one file
       to_normalize_text_path: result from WeNET. format: "filename_time_time_timestamp.txt"
       out_path: output path
       """
    original_text_dict = dict()
    last_key = None
    for subfolder_name in os.listdir(original_text_path):
        subfolder_path = os.path.join(original_text_path, subfolder_name)
        for file_name in os.listdir(subfolder_path):
            file_path = os.path.join(subfolder_path, file_name)
            if not file_name.endswith('.txt'):
                continue
            with open(file_path, 'r+') as f:
                line = f.readline()
                original_text_dict[file_name[:-4]] = line

    for file_name in os.listdir(to_normalize_text_path):
        if file_name.endswith('_timestamp.txt'):
            continue
        file_pure_name = os.path.splitext(file_name)[-2] #0ndrawiGAk8_000179_003050
        extension = os.path.splitext(file_name)[-1]
        if file_pure_name in original_text_dict.keys():
            example_text = original_text_dict[file_pure_name]
            print(example_text)
            with open(os.path.join(to_normalize_text_path, file_name), "r+") as f:
                line = f.readline()
                line_handled = " ".join(line.split()[3:])
                normalized_text = number_replace.try_method(example_text, line_handled, "<num>")
                wer = cal_wer.cal_wer_jiwerr(example_text, [(file_pure_name, normalized_text)])[0][1]['wer']
                a = 1
                file_path = os.path.join(out_path, file_pure_name)
                # with open(file_path + "_original.txt", 'w+') as out_f:
                #     # out_f.writelines('wer: ' + str(wer) + '\n')
                #     out_f.writelines(example_text)
                # with open(file_path + "_wenet.txt", 'w+') as out_f:
                #     # out_f.writelines('wer: ' + str(wer) + '\n')
                #     out_f.writelines(line_handled)
                with open(file_path + "_masked.txt", 'w+') as out_f:
                    # out_f.writelines('wer: ' + str(wer) + '\n')
                    out_f.writelines(normalized_text)
                    # out_f.writelines('generated: ' + normalized_text + '\n')

    return


if __name__ == "__main__":
    ssttr  = "fgwer re"
    ssttr_split = ssttr.split("wer: ")
    wav_path = r"D:\study\singaporeMasters\master project\data\wav_by_sentence"
    original_text_path = r"D:\study\singaporeMasters\master_project\term2\data\youtube_crawler\Chris@HoneyMoneySG\segmented_wav"
    to_normalize_text_path = r"D:\study\singaporeMasters\master_project\term2\data\youtube_crawler\Chris@HoneyMoneySG\wenet_transcript"
    out_path = r"D:\study\singaporeMasters\master_project\term2\data\youtube_crawler\Chris@HoneyMoneySG\wenet_transcript_masked"
    # fix()
    run_text_number_replace_folder(wav_path, original_text_path, to_normalize_text_path, out_path)
    os.getcwd()
