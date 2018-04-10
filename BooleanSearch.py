import pandas as pd
import re
import argparse
from nltk import ngrams

def cut_word(source):
    og_string = source['content']
    tmp_1 = ''.join(re.split(r'[0-9]*', og_string))
    #print(tmp_1)
    english_words = list(filter(None, re.findall(r'[a-zA-z]+', tmp_1)))
    #print(english_words)
    tmp_2 = ''.join(re.split(r'[a-zA-z]+', tmp_1))
    #tmp_string = ''.join(re.split('[!|！|，|、|?|？|「|」|/|《|》|【|】|〈|〉|’|-|、|(|)|:|.|%]', tmp_2))
    string = ''.join(re.split(r'\s+', tmp_2))
    #print(string)

    words_list = []

    for grams in list(ngrams(string, 2)):
        words = ''.join(grams)
        words_list.append(words)

    for grams in list(ngrams(string, 3)):
        words = ''.join(grams)
        words_list.append(words)

    for word in english_words:
        words_list.append(word)
    #print(words_list)
    return words_list

def index(source):
    for word in source['words_list']:
        if word not in index_table:
            index_table[word] = []
            index_table[word].append(source['index'])
        else:
            index_table[word].append(source['index'])
    return True

def search(query_file):
    output_list = []

    with open(query_file, encoding='UTF-8') as qf:
        for q_line in qf:
            result_list = []
            tmp_list = []
            #print(q_line)
            q_line = q_line.rstrip()

            if 'or' in q_line:
                query_list = re.split(' or ', q_line)
                #print(query_list)
                for word in query_list:
                    tmp_list.extend(index_table[word])

                result_list = sorted(list(set(tmp_list)))
                #print(len(result_list))
                output_list.append(result_list)
                # print(len(output_dict[q_line]))

            elif 'and' in q_line:
                query_list = re.split(' and ', q_line)
                #print(query_list)

                for word in query_list:
                    tmp_list.extend(list(set(index_table[word])))

                for ind in tmp_list:
                    if tmp_list.count(ind) ==len(query_list):
                        result_list.append(ind)

                result_list = sorted(set(result_list))
                #print(len(result_list))
                output_list.append(result_list)
                # print(len(output_dict[q_line]))

            elif 'not' in q_line:
                query_list = re.split(' not ', q_line)
                #print(query_list)
                result_list = list(set(index_table[query_list[0]]))

                for i in range(1, len(query_list)):
                    for ind in list(set(index_table[query_list[i]])):
                        if ind in result_list:
                            result_list.remove(ind)

                result_list = sorted(set(result_list))
                #print(len(result_list))
                output_list.append(result_list)


    with open('output.txt', 'w') as output:
        for result in output_list[:-1]:
            if len(result) == 0:
                result_string = '0'
                output.write(result_string + "\n")
            else:
                result_string = ','.join(str(e) for e in result)
                output.write(result_string + "\n")

        if len(output_list[len(output_list) - 1]) == 0:
            result_string = '0'
            output.write(result_string)
        elif len(output_list[len(output_list) - 1]) != 0:
            result = output_list[len(output_list) - 1]
            result_string = ','.join(str(e) for e in result)
            output.write(result_string)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source',
                       default='source.csv',
                       help='input source data file name')
    parser.add_argument('--query',
                        default='query.txt',
                        help='query file name')
    parser.add_argument('--output',
                        default='output.txt',
                        help='output file name')

    args = parser.parse_args()
    source_csv = args.source
    query_file = args.query

    source = pd.read_csv(source_csv, header=None)
    col_names = ['index', 'content']
    source.columns = col_names

    index_table = {}
    source['words_list'] = source.apply(cut_word, axis=1)
    source.apply(index, axis=1)

    search(query_file)
