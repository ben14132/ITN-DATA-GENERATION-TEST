import os

import nltk
from nltk import word_tokenize

import WER_in_python
from nltk.corpus import wordnet as wn
from nltk.stem.porter import PorterStemmer

number_map = {
    'o': 0,  # twenty o one
    'zero': 0,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
    'thirteen': 13,
    'fourteen': 14,
    'fifteen': 15,
    'sixteen': 16,
    'seventeen': 17,
    'eighteen': 18,
    'nineteen': 19,
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90,
}

multiplier_map = {
    'hundred': 100,
    'thousand': 1000,
    'million': 1000000,
    'billion': 1000000000,
    'trillion': 1000000000000,
    'quadrillion': 1000000000000000,
    'quintillion': 1000000000000000000,
    'sextillion': 1000000000000000000000,
    'septillion': 1000000000000000000000000,
    'octillion': 1000000000000000000000000000,
    'nonillion': 1000000000000000000000000000000,
    'decillion': 1000000000000000000000000000000000,
}

pow_map = {
'o': 0,  # twenty o one
    'zero': 1,
    'one': 1,
    'two': 1,
    'three': 1,
    'four': 1,
    'five': 1,
    'six': 1,
    'seven': 1,
    'eight': 1,
    'nine': 1,
    'ten': 2,
    'eleven': 2,
    'twelve': 2,
    'thirteen': 2,
    'fourteen': 2,
    'fifteen': 2,
    'sixteen': 2,
    'seventeen': 2,
    'eighteen': 2,
    'nineteen': 2,
    'twenty': 2,
    'thirty': 2,
    'forty': 2,
    'fifty': 2,
    'sixty': 2,
    'seventy': 2,
    'eighty': 2,
    'ninety': 2,
    'hundred': 3,
    'thousand': 4,
    'million': 7,
    'billion': 10,
    'trillion': 13,
    'quadrillion': 16,
    'quintillion': 19,
    'sextillion': 22,
    'septillion': 25,
    'octillion': 28,
    'nonillion': 31,
    'decillion': 34,
}

conj_set = {
    'and',
    'point',
    'dot',
}

special_map = {
    'dollar': '$',
}


class NumberReplace:
    def __init__(self, example: str, to_be_replaced: str):
        self.replace = None
        self.example_in_replace = None
        self.example = example
        self.target = to_be_replaced

    # create index linking word in example with word in target. i=>index of word in example,
    # example_in_replace[i]=>index of word in target
    def make_index(self) -> list[int]:
        example_split = self.example.split()
        to_be_replaced_split = self.target.split()
        e_len = len(example_split)
        r_len = len(to_be_replaced_split)
        e_idx = 0
        r_idx = 0
        num_start = 0
        num_end = 0
        example_in_replace = [-99999] * e_len

        while e_idx != e_len:
            if example_split[e_idx] == to_be_replaced_split[r_idx]:
                example_in_replace[e_idx] = r_idx
                e_idx += 1
                r_idx += 1
            else:
                # here currently treat it as the start of the number
                tmp_e_idx = e_idx
                tmp_r_idx = r_idx
                while tmp_r_idx < r_len:
                    t1 = example_split[tmp_e_idx]
                    t2 = to_be_replaced_split[tmp_r_idx]
                    if example_split[tmp_e_idx] == to_be_replaced_split[tmp_r_idx]:
                        example_in_replace[tmp_e_idx] = tmp_r_idx
                        break
                    tmp_r_idx += 1
                e_idx += 1
                if example_in_replace[tmp_e_idx] - example_in_replace[tmp_e_idx - 1] == 1:
                    r_idx = tmp_r_idx + 1
        self.example_in_replace = example_in_replace
        return example_in_replace

    # create period to replace. replace=[[(example_start, example_end),(target_start, target_end)],...]
    def generate_replace_zone(self, example_in_replace: list[int] = None) -> list[((int, int), (int, int))]:
        example_split = self.example.split()
        to_be_replaced_split = self.target.split()
        e_len = len(example_split)
        r_len = len(to_be_replaced_split)

        if example_in_replace is None:
            example_in_replace = self.example_in_replace

        replace_in_replace = [-89999] * r_len
        e_idx = 0
        while e_idx != e_len:
            if example_in_replace[e_idx] >= 0:
                replace_in_replace[example_in_replace[e_idx]] = e_idx
            e_idx += 1

        e_idx = 0
        r_idx = 0
        replace = []
        period_start = -1
        period_end = -1
        while e_idx < e_len:
            if e_idx == 0:
                if example_in_replace[e_idx] == e_idx:
                    e_idx += 1
                    continue
                else:
                    period_start = e_idx
                    e_idx += 1
                    continue
            if example_in_replace[e_idx] - example_in_replace[e_idx - 1] == 1:
                if period_start != -1:
                    if period_start == 0:
                        replace.append(
                            ((period_start, e_idx - 1), (0, example_in_replace[e_idx - 1])))
                    else:
                        replace.append(
                            ((period_start, e_idx - 1),
                             (example_in_replace[period_start - 1] + 1, example_in_replace[e_idx - 1])))
                    period_start = -1
                e_idx += 1
                continue
            else:
                if period_start == -1:
                    period_start = e_idx
                e_idx += 1
                continue

        if period_start != -1:
            if period_start == 0:
                replace.append(
                    ((period_start, e_idx),
                     (0, example_in_replace[e_idx - 1] + 1 if example_in_replace[e_idx - 1] > 0 else r_len)))
            else:
                replace.append(
                    ((period_start, e_idx),
                     (example_in_replace[period_start - 1] + 1,
                      example_in_replace[e_idx - 1] + 1 if example_in_replace[e_idx - 1] > 0 else r_len)))
        self.replace = replace
        return replace

    def generate_replacement(self, replace: list[((int, int), (int, int))] = None) -> str:
        example_split = self.example.split()
        to_be_replaced_split = self.target.split()
        e_len = len(example_split)
        r_len = len(to_be_replaced_split)

        if replace is None:
            replace = self.replace

        to_return = ""
        replace_idx = 0
        replace_len = len(replace)
        r_idx = 0
        while r_idx < r_len:
            if replace_idx == replace_len:
                to_return += to_be_replaced_split[r_idx] + ' '
            elif r_idx < replace[replace_idx][1][0]:
                to_return += to_be_replaced_split[r_idx] + ' '
            else:
                tmp_example_idx = replace[replace_idx][0][0]
                while tmp_example_idx < replace[replace_idx][0][1]:
                    to_return += example_split[tmp_example_idx] + ' '
                    tmp_example_idx += 1
                r_idx = replace[replace_idx][1][1] - 1
                replace_idx += 1
            r_idx += 1
        return to_return

    def generate_replacement_and_show(self) -> str:
        to_return = ""
        example_split = self.example.split()
        hypothesis_split = self.target.split()
        # make hyp back to example, so use reversely
        d = WER_in_python.editDistance(hypothesis_split, example_split)
        # print(d)
        list = WER_in_python.getStepList(hypothesis_split, example_split, d)
        print(list)
        e_idx = 0
        h_idx = 0
        e_len = len(example_split)
        h_len = len(hypothesis_split)
        return_split = []
        list_len = len(list)
        list_idx = 0
        deleted = []
        added = []
        while list_idx < list_len:
            if list[list_idx] == 'e':
                return_split.append(hypothesis_split[h_idx])
                e_idx += 1
                h_idx += 1
            elif list[list_idx] == 'd':
                h_idx += 1
            elif list[list_idx] == 's':
                return_split.append(example_split[e_idx])
                e_idx += 1
                h_idx += 1
            else:                e_idx += 1
            list_idx += 1

        to_return = ' '.join(return_split)
        print(to_return)

        result = float(d[len(hypothesis_split)][len(example_split)]) / len(hypothesis_split) * 100
        result = str("%.2f" % result) + "%"
        WER_in_python.alignedPrint(list, hypothesis_split, example_split, result)
        # WER_in_python.wer(example_split, hypothesis_split)
        return to_return


def check_similar(example: str, hypothesis: str) -> bool:
    porter = PorterStemmer()
    catagories = wn.synsets(example)
    for cata in catagories:
        similars = [porter.stem(word) for word in wn.synset(cata.name()).lemma_names()]
        if porter.stem(hypothesis) in similars:
            return True
    return False


def main(example: str, to_be_replaced: str):
    to_return = ""
    example_split = example.split()
    hypothesis_split = to_be_replaced.split()
    d = WER_in_python.editDistance(hypothesis_split, example_split)
    list = WER_in_python.getStepList(hypothesis_split, example_split, d)
    e_idx = 0
    h_idx = 0
    e_len = len(example_split)
    h_len = len(hypothesis_split)
    return_split = []
    list_len = len(list)
    list_idx = 0
    delete_list = []
    while list_idx < list_len:
        if list[list_idx] == 'e':
            delete_list.clear()
            return_split.append(hypothesis_split[h_idx])
            e_idx += 1
            h_idx += 1
        elif list[list_idx] == 'd':
            delete_list.append(hypothesis_split[h_idx])
            h_idx += 1
        elif list[list_idx] == 's':
            delete_list.append(hypothesis_split[h_idx])
            flag = True
            for idx, deleted in enumerate(delete_list):
                if check_similar(example_split[e_idx], deleted):
                    return_split.append(deleted)
                    flag = False
                    delete_list = delete_list[idx + 1:]
            if flag:
                return_split.append(example_split[e_idx])
            e_idx += 1
            h_idx += 1
        else:
            return_split.append(example_split[e_idx])
            e_idx += 1
        list_idx += 1

    print(' '.join(return_split))
    to_return = ' '.join(return_split)

    result = float(d[len(hypothesis_split)][len(example_split)]) / len(hypothesis_split) * 100
    result = str("%.2f" % result) + "%"
    # WER_in_python.alignedPrint(list, hypothesis_split, example_split, result)
    # WER_in_python.wer(example_split, hypothesis_split)
    return to_return


def contain_digit(in_str) -> bool:
    for s in in_str:
        if s.isdigit():
            return True
    return False


def extract_digit(in_str) -> str:
    ret = ""
    for s in in_str:
        if s.isdigit():
            ret += s
    return ret


# things like a hundred might not be translated
def try_method(example: str, hypothesis: str, mode: str) -> str:
    hypothesis_replaced_split = []
    example_split = example.split()
    hypothesis_split = hypothesis.split()
    hypothesis_might_replace = []
    example_might_replace = []
    for idx, word in enumerate(example_split):
        if contain_digit(word):
            example_might_replace.append(extract_digit(word))

    hyp_len = len(hypothesis_split)
    hyp_idx = 0
    may_number = 0
    may_sub_number = 0
    number_start_idx = -1
    non_common_num_flag = False
    conj_flag = None
    pow_count = 99999
    sub_pow_count = 4
    point_flag = False
    point_str = None
    num_deal = False
    while hyp_idx < hyp_len:
        cur_word = hypothesis_split[hyp_idx]
        if hypothesis_split[hyp_idx] in number_map.keys():
            num_deal = True
            num = number_map[hypothesis_split[hyp_idx]]
            if point_flag:
                point_str += str(num)
            else:
                if not non_common_num_flag and may_sub_number != 0 and len(str(may_sub_number)) <= len(str(num)):
                    # treat as year or phone number
                    non_common_num_flag = True
                    sub_pow_count = len(str(num))
                if non_common_num_flag: # and len(str(num)) == sub_pow_count:
                    may_sub_number *= pow(10, len(str(num)))
                may_sub_number += num
        elif hypothesis_split[hyp_idx] in multiplier_map.keys():
            num_deal = True
            if point_flag:
                # TODO: cut .0?
                may_sub_number = float(str(may_sub_number) + point_str)
                point_flag = False
                point_str = None
            if may_sub_number == 0:
                may_sub_number = 1
            if pow_count > pow_map[hypothesis_split[hyp_idx]]:
                pow_count = pow_map[hypothesis_split[hyp_idx]]
                may_number += may_sub_number * multiplier_map[hypothesis_split[hyp_idx]]
            else:
                # here multiplier repeat usage, ignore numbers (grammar)
                may_number *= multiplier_map[hypothesis_split[hyp_idx]]
            may_sub_number = 0
        elif hypothesis_split[hyp_idx] in conj_set:
            if hypothesis_split[hyp_idx] == 'point' or hypothesis_split[hyp_idx] == 'dot':
                point_str = '.'
                point_flag = True
            conj_flag = hypothesis_split[hyp_idx]
            if not num_deal:
                hypothesis_replaced_split.append(hypothesis_split[hyp_idx])
        else:
            if num_deal:
                num_deal = False
                may_number += may_sub_number
                may_sub_number = 0
                may_number = str(may_number)
                if point_flag:
                    may_number += point_str
                hypothesis_might_replace.append(may_number)
                non_common_num_flag = False
                pow_count = -1
                point_flag = False
                point_str = None

                # if conj_flag is not None:
                #     hypothesis_replaced_split.append(conj_flag)
                #     conj_flag = None

                if mode == 'num':
                    hypothesis_replaced_split.append(str(may_number))
                else:
                    hypothesis_replaced_split.append(mode)
                may_number = 0
            hypothesis_replaced_split.append(hypothesis_split[hyp_idx])
        hyp_idx += 1
    if num_deal:
        may_number += may_sub_number
        may_number = str(may_number)
        if point_flag:
            may_number += point_str
        hypothesis_might_replace.append(may_number)
        if mode == 'num':
            hypothesis_replaced_split.append(str(may_number))
        else:
            hypothesis_replaced_split.append(mode)
    return ' '.join(hypothesis_replaced_split)


def try_method2(example: str, hypothesis: str) -> str:
    example_split = example.split()
    hypothesis_split = hypothesis.split()
    hypothesis_might_replace = []
    example_might_replace = []
    for idx, word in enumerate(example_split):
        if contain_digit(word):
            example_might_replace.append(word) #(extract_digit(word))
    hyp_idx = 0
    hyp_len = len(hypothesis_split)
    exp_idx = 0
    exp_len = len(example_might_replace)
    while hyp_idx < hyp_len:
        if hypothesis_split[hyp_idx] == '<unk>' and exp_idx < exp_len:
            hypothesis_split[hyp_idx] = str(example_might_replace[exp_idx])
            exp_idx += 1
        hyp_idx += 1
    return ' '.join(hypothesis_split)


if __name__ == "__main__":
    xxnum = 11
    # print(len(num))
    # text = word_tokenize("two thousand")
    # print(nltk.pos_tag(text))

    string = "This costs pp tt rr ss around $1000 rhser which is very hhtjt gwrh r expensive"
    # _to_be_replaced = "This costs about one thousand dollars grhgrst which is very expensive"
    _to_be_replaced = "one point two he"


    # hyp: I have one apple.
    # intermedite output: I have <unk> apple
    #
    # example: I have one apple

    # _to_be_replaced = "twenty fourteen"

    # _to_be_replaced = try_method(string, _to_be_replaced, 'num')

    new_to_be_replaced = try_method(string, _to_be_replaced, 'num')

    print("number translate generated: " + try_method2(string, new_to_be_replaced))

    nb = NumberReplace(string, _to_be_replaced)
    nb.make_index()
    nb.generate_replace_zone()
    converted1 = nb.generate_replacement()
    print("nb generated: " + converted1)

    nb.generate_replacement_and_show()
    converted = main(string, _to_be_replaced)
    print("main generated: " + converted)

    #
    # print(wn.synsets('motorcar')[0].name())
    # print(wn.synset(wn.synsets('motorcar')[0].name()).lemma_names())
