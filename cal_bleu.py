import math

import cal_wer
from nltk.translate.bleu_score import sentence_bleu

from nltk.translate.bleu_score import SmoothingFunction


def ngram_count(in_ground_truth, n):
    count_dict = dict()
    ground_truth_list = in_ground_truth.split()
    for i in range(1, n + 1):
        count_dict[i] = dict()
        for j in range(0, len(ground_truth_list) - i + 1):
            token = ' '.join(ground_truth_list[j: j + i])
            if token not in count_dict[i]:
                count_dict[i][token] = 1
            else:
                count_dict[i][token] += 1
    return count_dict


def cal_ngram_match(ngram_dict, in_hypothesis, n):
    hypothesises_list = in_hypothesis.split()
    match_dict = dict()
    for i in range(1, n + 1):
        match_count = 0
        to_match = len(hypothesises_list) - i + 1
        for j in range(0, to_match):
            token = ' '.join(hypothesises_list[j: j + i])
            if token in ngram_dict[i]:
                if ngram_dict[i][token] > 0:
                    ngram_dict[i][token] -= 1
                    match_count += 1
        match_dict[i] = match_count * 1.0 / to_match * 1.0
    return match_dict


def brevity_penalty(ground_truth_len, hypothesis_len):
    if ground_truth_len <= hypothesis_len:
        bp = 1
    else:
        bp = math.exp(1 - (float(hypothesis_len) / hypothesis_len))

    return bp


def cal_BLEU_loacl_algorithm(ground_truth, hypothesises, n=4):

    to_return = []
    for hypothesis in hypothesises:
        ground_truth_dict = ngram_count(ground_truth, n)
        bp = brevity_penalty(len(ground_truth), len(hypothesis))
        match_dict = cal_ngram_match(ground_truth_dict, hypothesis[1], n)
        mid1 = 0
        for i in range(1, n + 1):
            if match_dict[i] == 0:
                mid1 += float("-inf")
                continue
            mid1 += math.log(match_dict[i])
        to_return.append((hypothesis[0], bp * math.exp(mid1 / n * 1.0)))
    return to_return

def cal_BLEU_nltk(ground_truth, hypothesises, n=4):
    smooth = SmoothingFunction()
    to_return = []
    for hypothesis in hypothesises:
        candidate = hypothesis[1].split()
        references = [ground_truth.split()]
        score = sentence_bleu(references, candidate)
            #, weights=(0.25,0.25, 0.25, 0.25),
             #                 smoothing_function=smooth.method1())
        to_return.append((hypothesis[0], score))
    return to_return


if __name__ == "__main__":
    d = dict()
    #print(d[0])
    # candidate, references = fetch_data(sys.argv[1], sys.argv[2])
    input_dir_ = r'D:\study\singaporeMasters\master project\chng-pipeline\JoshTanTheAstuteParent\wer_result\Ori ' \
                 r'transcript'
    ground_truth_file_ = r'D:\study\singaporeMasters\master ' \
                         r'project\chng-pipeline\JoshTanTheAstuteParent\wer_result\Ori transcript\text.txt '
    ground_truth_, hypothesises_ = cal_wer.load_file(input_dir_, ground_truth_file_)
    bleus = cal_BLEU_loacl_algorithm(ground_truth_, hypothesises_, 4)
    print(bleus)
    out = open('bleu_out.txt', 'w')
    for bleu in bleus:
        out.write(str(bleu) + '\n')
    out.close()
    bleus2 = cal_BLEU_nltk(ground_truth_, hypothesises_, 4)
    print(bleus2)
    out = open('bleu_out2.txt', 'w')
    for bleu in bleus2:
        out.write(str(bleu) + '\n')
    out.close()
