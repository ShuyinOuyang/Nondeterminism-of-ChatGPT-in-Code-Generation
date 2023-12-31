import json
import re
import numpy as np
import scipy.stats as stats
import os
import openpyxl
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def ratio_of_worst(list, target):
    # calculating the ratio of worst cases happened in dataset
    # sepecially for test pass rate, OER, OER_ow
    count = 0
    for case in list:
        if case == target:
            count += 1

    # print(dataset)
    # print(temperature)
    # print(count/len(list))
    return (count/len(list))

def semantic_syntactic_structural_similarity():
    # get all measurement of semantic, syntactic, and structural similarity
    # where all the file_path could be modified directly with line 'with open(x) as f:'

    # get semantic similarity and syntactic similarity
    if dataset != 'code_contest':
        if request_way == 'R1':
            with open(file_path + '/%s_%s_%s/intermediate_result_among5.json' % (dataset, model, temperature), 'r') as f:
                intermediate_result = json.load(f)
        else:
            with open(file_path + '/%s_%s_%s/intermediate_result_top0_5.json' % (dataset, model, temperature), 'r') as f:
                intermediate_result = json.load(f)
    else:
        if request_way == 'R1':
            with open(file_path + '/%s_%s_%s/intermediate_result_among5.json' % ('CodeContests', model, temperature), 'r') as f:
                intermediate_result = json.load(f)
        else:
            with open(file_path + '/%s_%s_%s/intermediate_result_top0_5.json' % ('CodeContests', model, temperature), 'r') as f:
                intermediate_result = json.load(f)

    test_case_pass_rate = []
    OER = []
    OER_ow = []
    LCS = []
    Levenshieten = []

    # if request_way == 'R1':
    #     Levenshieten.append(intermediate_result['syntatic_similarity']['Levenshtein_edit_distance'])
    for case in intermediate_result:
        # if request_way == 'R1':
        #     OER.append(intermediate_result[case]['syntatic_similarity']['same_output_between_5'])
        #     OER_ow.append(intermediate_result[case]['syntatic_similarity']['same_output_between_5_correct'])
        # else:
        OER.append(intermediate_result[case]['syntatic_similarity']['same_output_between_5'])
        OER_ow.append(intermediate_result[case]['syntatic_similarity']['same_output_between_5_correct'])
        Levenshieten.append(intermediate_result[case]['syntatic_similarity']['Levenshtein_edit_distance'])
        test_case_pass_rate.append(intermediate_result[case]['test_case_pass_rate'])
        LCS.append(intermediate_result[case]['LCS'])

    # get structural similarity
    if dataset == 'code_contest':
        if request_way == 'R1':
            with open(file_path + '/structural_similarity/%s_%s_structual_similarity_among5.json' % ('CodeContests', temperature), 'r') as f:
                problem_dic = json.load(f)
        else:
            with open(file_path + '/structural_similarity/%s_%s_structual_similarity_top0_5.json' % ('CodeContests', temperature), 'r') as f:
                problem_dic = json.load(f)
    else:
        if request_way == 'R1':
            with open(file_path + '/structural_similarity/%s_%s_structual_similarity_among5.json' % (dataset, temperature), 'r') as f:
                problem_dic = json.load(f)
        else:
            with open(file_path + '/structural_similarity/%s_%s_structual_similarity_top0_5.json' % (dataset, temperature), 'r') as f:
                problem_dic = json.load(f)

    tmp = {'structual_similarity_UnifiedDiff': [], 'structual_similarity_TreeDiff': []}
    for key in problem_dic:
        a = problem_dic[key]['structual_similarity']['structual_similarity_UnifiedDiff']
        if a != [-1, -1, -1, -1] and a != [-2, -2, -2, -2] and a != [-3, -3, -3, -3]:
            tmp['structual_similarity_UnifiedDiff'].append(a)
        else:
            tmp['structual_similarity_UnifiedDiff'].append([[0],[0],[0],[0]])
        a = problem_dic[key]['structual_similarity']['structual_similarity_TreeDiff']
        if a != [-1, -1, -1, -1] and a != [-2, -2, -2, -2] and a != [-3, -3, -3, -3]:
            tmp['structual_similarity_TreeDiff'].append(a)
        else:
            tmp['structual_similarity_TreeDiff'].append([[0],[0],[0],[0]])
    United_Diff = tmp['structual_similarity_UnifiedDiff']
    Tree_Diff = tmp['structual_similarity_TreeDiff']

    return test_case_pass_rate, OER, OER_ow, Levenshieten, LCS, United_Diff, Tree_Diff

def get_correlation():
    # store all the fine-grained measurement in the dic named correlation (for later draw the heatmap)

    test_pass_rate, OER, OER_ow, Levenshieten, LCS, United_Diff, Tree_Diff = semantic_syntactic_structural_similarity()
    correlation = {'problem': [],
                   'test pass rate mean': [],
                   'test pass rate variance': [],
                   'test pass rate max diff': [],
                   'description length': [],
                   'difficulty': [],
                   'time_limit': [],
                   'cf_rating': []
                   }

    test_pass_rate_var = [np.var(i) for i in test_pass_rate]
    test_pass_rate_var_avg = np.mean(test_pass_rate_var)
    test_pass_rate_max_diff = [max(i) - min(i) for i in test_pass_rate]
    test_pass_rate_max_diff_avg = np.mean(test_pass_rate_max_diff)

    for i in range(len(problem_list)):
        problem = problem_list[i]


        if dataset == 'HumanEval':
            correlation['problem'].append(problem['task_id'])
            correlation['description length'].append(len(problem['prompt']))

        elif dataset == 'APPS':
            correlation['problem'].append(problem['name'])
            correlation['description length'].append(len(problem['description']))
        else:
            correlation['problem'].append(problem['name'])
            correlation['description length'].append(len(problem['description']))
            correlation['difficulty'].append(problem['difficulty'])

            pattern = re.compile(r'(?<=seconds:=)*\d+')
            time_limit = pattern.findall(problem['time_limit'].split('\n')[0])[0]
            if 'seconds' in problem['time_limit']:
                correlation['time_limit'].append(int(time_limit))
            else:
                correlation['time_limit'].append(3)
            correlation['cf_rating'].append(problem['cf_rating'])

        correlation['test pass rate mean'].append(np.mean(test_pass_rate[i]))
        correlation['test pass rate variance'].append(np.var(test_pass_rate[i]))
        correlation['test pass rate max diff'].append(max(test_pass_rate[i])-min(test_pass_rate[i]))

    correlation['OER'] = OER
    correlation['OER_ow'] = OER_ow

    correlation['LCS mean'] = []
    # correlation['LCS variance'] = []
    correlation['LCS min'] = []

    correlation['LED mean'] = []
    # correlation['Levenshieten variance'] = []
    correlation['LED max'] = []

    correlation['United_Diff mean'] = []
    # correlation['United_Diff variance'] = []
    correlation['United_Diff min'] = []

    correlation['Tree_Diff mean'] = []
    # correlation['Tree_Diff variance'] = []
    correlation['Tree_Diff min'] = []

    for case in LCS:
        correlation['LCS mean'].append(np.mean(case))
        # correlation['LCS variance'].append(np.var(case))
        correlation['LCS min'].append(min(case))

    for case in Levenshieten:
        correlation['LED mean'].append(np.mean(case))
        # correlation['Levenshieten variance'].append(np.var(case))
        correlation['LED max'].append(max(case))

    for case in United_Diff:
        correlation['United_Diff mean'].append(np.mean([i[0] for i in case]))
        # correlation['United_Diff variance'].append(np.var([i[0] for i in case]))
        correlation['United_Diff min'].append(min([i[0] for i in case]))

    for case in Tree_Diff:
        correlation['Tree_Diff mean'].append(np.mean([i[0] for i in case]))
        # correlation['Tree_Diff variance'].append(np.var([i[0] for i in case]))
        correlation['Tree_Diff min'].append(min([i[0] for i in case]))

    return correlation

def store_data_in_xlsx(correlation):
    # store in .xlsx
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    data = [[]]
    data[0].append(np.mean(correlation['test pass rate mean']))
    data[0].append(np.mean(correlation['test pass rate variance']))
    data[0].append(np.mean(correlation['test pass rate max diff']))
    data[0].append(ratio_of_worst(correlation['test pass rate mean'], 1))
    data[0].append(np.mean(correlation['OER']))
    data[0].append(ratio_of_worst(correlation['OER'], 0))
    data[0].append(np.mean(correlation['OER_ow']))
    data[0].append(ratio_of_worst(correlation['OER_ow'], 0))
    data[0].append(np.mean(correlation['LCS mean']))
    data[0].append(np.mean(correlation['LCS min']))
    data[0].append(np.mean(correlation['LED mean']))
    data[0].append(np.mean(correlation['LED max']))
    data[0].append(np.mean(correlation['United_Diff mean']))
    data[0].append(np.mean(correlation['United_Diff min']))
    data[0].append(np.mean(correlation['Tree_Diff mean']))
    data[0].append(np.mean(correlation['Tree_Diff min']))

    for row in data:
        sheet.append(row)
    workbook.save('data.xlsx')

def draw_heatmap(correlation, save_dir):
    correlation_rank = []
    high_relavent = []
    problem_features = ['description length', 'difficulty', 'time_limit', 'cf_rating']
    for case in correlation_rank:
        if (case[0] in problem_features or case[1] in problem_features) and case[2][1] < 0.05:
            high_relavent.append(case)
            # print('%s & %s\'s correlation: %s' % (list(correlation.keys())[i],
            #                                       list(correlation.keys())[j],
            #                                       stats.pearsonr(correlation[list(correlation.keys())[i]], correlation[list(correlation.keys())[j]])
            #                                       )
            #       )
    correlation_list = []
    # test pass rate
    correlation_list.append(correlation['test pass rate mean'])
    correlation_list.append(correlation['test pass rate variance'])
    correlation_list.append(correlation['test pass rate max diff'])
    # output equivalence rate
    correlation_list.append(correlation['OER'])
    correlation_list.append(correlation['OER_ow'])
    # LCS
    correlation_list.append(correlation['LCS mean'])
    # correlation_list.append(correlation['LCS variance'])
    correlation_list.append(correlation['LCS min'])
    # Levenshieten
    correlation_list.append(correlation['LED mean'])
    # correlation_list.append(correlation['Levenshieten variance'])
    correlation_list.append(correlation['LED max'])
    # United_Diff
    correlation_list.append(correlation['United_Diff mean'])
    # correlation_list.append(correlation['United_Diff variance'])
    correlation_list.append(correlation['United_Diff min'])
    # Tree_Diff
    correlation_list.append(correlation['Tree_Diff mean'])
    # correlation_list.append(correlation['Tree_Diff variance'])
    correlation_list.append(correlation['Tree_Diff min'])
    # problem features
    correlation_list.append(correlation['description length'])
    if dataset == 'code_contest':
        correlation_list.append(correlation['difficulty'])
        correlation_list.append(correlation['time_limit'])
        correlation_list.append(correlation['cf_rating'])

    if dataset == 'code_contest':
        column_names = ['TPR mean value',
                        'TPR mean variance',
                        'TPR mean max diff',

                        'OER mean',
                        'OER (no ex.) mean',

                        'LCS mean',
                        'LCS worst',

                        'LED mean',
                        'LED worst',

                        'United_Diff mean',
                        'United_Diff worst',

                        'Tree_Diff mean',
                        'Tree_Diff worst',

                        'description length',
                        'difficulty',
                        'time_limit',
                        'cf_rating'
                        ]
    else:
        column_names = ['TPR mean value',
                        'TPR mean variance',
                        'TPR mean max diff',

                        'OER mean',
                        'OER_ow mean',

                        'LCS mean',
                        'LCS worst',

                        'LED mean',
                        'LED worst',

                        'United_Diff mean',
                        'United_Diff worst',

                        'Tree_Diff mean',
                        'Tree_Diff worst',

                        'description length'
                        ]

    p_values = []
    correlation_values = []
    empty_values = []
    for i in range(len(column_names)):
        p_tmp = []
        c_tmp = []
        e_tmp = []
        for j in range(len(column_names)):
            p_tmp.append(stats.pearsonr(correlation_list[i], correlation_list[j])[1])
            c_tmp.append(stats.pearsonr(correlation_list[i], correlation_list[j])[0])
            e_tmp.append(0)
        p_values.append(p_tmp)
        correlation_values.append(c_tmp)
        empty_values.append(e_tmp)

    for i in range(len(column_names)):
        for j in range(len(column_names)):
            if p_values[i][j] > 0.05:
                empty_values[i][j] = '-'
            else:
                empty_values[i][j] = round(correlation_values[i][j], 2)


    fig, ax = plt.subplots(figsize=(20, 20))
    fig.subplots_adjust(top=0.98, bottom=0.18, left=0.18)
    p1 = sns.heatmap(correlation_values, annot=empty_values, cmap='Greys',
                     xticklabels=column_names, yticklabels=column_names, annot_kws={"fontsize": 18}, fmt='')

    cbar = p1.collections[0].colorbar
    # Set the font size of the color bar labels
    cbar.ax.tick_params(labelsize=20)
    #
    p1.set_xticklabels(p1.get_xticklabels(), fontsize=25)
    p1.tick_params(axis='y', labelsize=25)

    # plt.show()
    plt.savefig(save_dir + 'heatmap_metric.pdf')

if __name__ == "__main__":
    # config (change to apply)
    dataset_ = ['code_contest', 'APPS', 'HumanEval']
    dataset = dataset_[2]
    # dataset_0 = 'CodeContests'
    request_way_ = ['R1', 'R2']
    request_way = request_way_[1]
    temperature_ = [0, 1, 2]
    temperature = temperature_[0]
    problem_list = []
    # customized
    file_path = './result_data'
    # gpt-3.5-turbo or gpt-4
    model = 'gpt-4'

    if dataset == 'code_contest':
        # with open('./tmp2/code_contests_test.json', 'r') as f:
        with open('./dataset/code_contests_test.json', 'r') as f:
            problem_list = json.load(f)
    elif dataset == 'HumanEval':
        with open('./HumanEval/HumanEval.jsonl', 'r') as f:
            for line in f.readlines():
                problem_list.append(json.loads(line))
    elif dataset == 'APPS':
        path = './APPS/test/'
        for dirpath, dirnames, filenames in os.walk(path):
            # iterating for every problem
            for dirname in dirnames[:500]:
                # description
                with open(path + dirname + '/question.txt', 'r', encoding='utf-8') as f:
                    description = f.read()
                problem_list.append({'name': dirname, 'description': description})

    correlation = get_correlation()
    store_data_in_xlsx(correlation)
    draw_heatmap(correlation, './')
