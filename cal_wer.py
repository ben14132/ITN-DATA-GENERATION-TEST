import os

import jiwer
import Levenshtein


def min_distance(sent1, sent2):
    sent1 = sent1.split()
    sent2 = sent2.split()
    m = len(sent1) + 1
    n = len(sent2) + 1

    cache = [[0] * n for _ in range(m)]

    for i in range(m):
        for j in range(n):
            if i == 0:
                cache[i][j] = j
            elif j == 0:
                cache[i][j] = i
            else:
                if sent1[i - 1] == sent2[j - 1]:
                    cache[i][j] = cache[i - 1][j - 1]
                else:
                    S_op = cache[i - 1][j - 1] + 1
                    I_op = cache[i][j - 1] + 1
                    D_op = cache[i - 1][j] + 1

                    cache[i][j] = min(S_op, I_op, D_op)

    S = 0
    I = 0
    D = 0
    C = 0
    i = m - 1
    j = n - 1
    while True:
        if i > 0 and j > 0 and cache[i - 1][j - 1] == cache[i][j]:
            C += 1
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and cache[i - 1][j - 1] == cache[i][j] - 1:
            S += 1
            i -= 1
            j -= 1
        elif i > 0 and cache[i - 1][j] == cache[i][j] - 1:
            D += 1
            i -= 1
        elif j > 0 and cache[i][j - 1] == cache[i][j] - 1:
            I += 1
            j -= 1
        else:
            if i == 0 and j == 0:
                break
            else:
                raise Exception("wer cal error")

    return S, D, I, C, cache[m - 1][n - 1]


def load_file(input_dir, ground_truth_file):
    ground_truth = ''
    hypothesises = []
    with open(ground_truth_file, 'r+') as f:
        raw_scripts = f.readlines()
        scripts = [' '.join(raw_script.split()[1:]) for raw_script in raw_scripts]
        scripts = ' '.join(scripts)
        ground_truth = scripts
    for file in os.listdir(input_dir):
        if file.endswith('.txt') and not file.startswith('wer_result'):
            with open(os.path.join(input_dir, file), 'r+') as f:
                raw_scripts = f.readlines()
            scripts = [' '.join(raw_script.split()[1:]) for raw_script in raw_scripts]
            scripts = ' '.join(scripts)
            hypothesises.append((file, scripts))
    return ground_truth, hypothesises


def cal_wer_jiwerr(ground_truth, hypothesises):
    errors = []
    for file, hypothesis in hypothesises:
        jiwerr = jiwer.compute_measures(ground_truth, hypothesis)
        errors.append((file, jiwerr))
    return errors

# def cal_wer_jiwerr_(ground_truth, hypothesises):
#     errors = []
#     for file, hypothesis in hypothesises:
#         jiwerr = jiwer.compute_measures(ground_truth, hypothesis)
#         errors.append((file, jiwerr))
#         print(jiwerr['wer'])
#     with open(os.path.join(input_dir, 'wer_result_1.txt'), 'w+') as f:
#         f.writelines('\t\t\t\t'.join(['filename', 'wer', 'mer', 'wil']) + '\n')
#         for file, error in errors:
#             f.writelines('\t'.join([file, str(error['wer']), str(error['mer']), str(error['wil'])]) + '\n')
#     print(errors)


def cal_wer_Levenshtein(ground_truth, hypothesises):
    errors = []
    for file, hypothesis in hypothesises:
        editops = Levenshtein.editops(ground_truth.split(), hypothesis.split())
        D = sum(1 if operation[0] == 'delete' else 0 for operation in editops)
        S = sum(1 if operation[0] == 'replace' else 0 for operation in editops)
        I = sum(1 if operation[0] == 'insert' else 0 for operation in editops)
        C = len(ground_truth.split()) - D - S
        #
        print(str(S) + ' ' + str(D) + ' ' + str(I) + ' ' + str(C) + ' ' + str(
            (S + D + I) * 1.0 / (S + D + C) * 1.0) + ' ' + file)


def cal_wer_local_algorithm(ground_truth, hypothesises):
    errors = []
    for file, hypothesis in hypothesises:
        S, D, I, C, dist = min_distance(ground_truth, hypothesis)
        print(str(S) + ' ' + str(D) + ' ' + str(I) + ' ' + str(C) + ' ' + str(
            (S + D + I) * 1.0 / (S + D + C) * 1.0) + ' ' + file)


if __name__ == "__main__":
    print("adf")
    S, D, I, C, dist = min_distance('is our first ever episode of twenty twenty one and today'
                                    , 'this is our first ever episode of two thousand and twenty-one')
    input_dir_ = r'D:\study\singaporeMasters\master project\chng-pipeline\JoshTanTheAstuteParent\wer_result\Ori ' \
                 r'transcript'
    ground_truth_file_ = r'D:\study\singaporeMasters\master ' \
                         r'project\chng-pipeline\JoshTanTheAstuteParent\wer_result\Ori transcript\text.txt '
    ground_truth, hypothesises = load_file(input_dir_, ground_truth_file_)
    cal_wer_jiwerr(ground_truth, hypothesises)
    cal_wer_Levenshtein(ground_truth, hypothesises)
    cal_wer_local_algorithm(ground_truth, hypothesises)
