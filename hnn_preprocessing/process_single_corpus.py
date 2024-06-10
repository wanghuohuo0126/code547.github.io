import pickle
from collections import Counter

# 从文件中加载pickle数据
def load_pickle(filename):
    with open(filename, 'rb') as f:
        data = pickle.load(f, encoding='iso-8859-1')  # 使用iso-8859-1编码加载数据
    return data

# 根据问题ID计数将数据拆分成单个和多个部分
def split_data(total_data, qids):
    result = Counter(qids)  # 统计问题ID的出现次数
    total_data_single = []  # 存储单个问题ID的数据
    total_data_multiple = []  # 存储多个问题ID的数据
    for data in total_data:  # 遍历所有数据
        if result[data[0][0]] == 1:  # 如果问题ID只出现一次
            total_data_single.append(data)  # 将数据添加到单个部分
        else:
            total_data_multiple.append(data)  # 否则将数据添加到多个部分
    return total_data_single, total_data_multiple  # 返回拆分后的数据

# 处理staqc格式的数据
def data_staqc_processing(filepath, save_single_path, save_multiple_path):
    with open(filepath, 'r') as f:
        total_data = eval(f.read())  # 读取并解析数据
    qids = [data[0][0] for data in total_data]  # 获取问题ID列表
    total_data_single, total_data_multiple = split_data(total_data, qids)  # 拆分数据
    with open(save_single_path, "w") as f:
        f.write(str(total_data_single))  # 将单个部分的数据保存到文件
    with open(save_multiple_path, "w") as f:
        f.write(str(total_data_multiple))  # 将多个部分的数据保存到文件

# 处理大型数据集
def data_large_processing(filepath, save_single_path, save_multiple_path):
    total_data = load_pickle(filepath)  # 加载pickle格式的数据
    qids = [data[0][0] for data in total_data]  # 获取问题ID列表
    total_data_single, total_data_multiple = split_data(total_data, qids)  # 拆分数据
    with open(save_single_path, 'wb') as f:
        pickle.dump(total_data_single, f)  # 将单个部分的数据保存为pickle格式
    with open(save_multiple_path, 'wb') as f:
        pickle.dump(total_data_multiple, f)  # 将多个部分的数据保存为pickle格式

# 将未标记的单个数据转换为带标签的数据
def single_unlabeled_to_labeled(input_path, output_path):
    total_data = load_pickle(input_path)  # 加载pickle格式的数据
    labels = [[data[0], 1] for data in total_data]  # 为每个数据添加标签
    total_data_sort = sorted(labels, key=lambda x: (x[0], x[1]))  # 按照问题ID对数据进行排序
    with open(output_path, "w") as f:
        f.write(str(total_data_sort))  # 将带标签的数据保存到文件

if __name__ == "__main__":
    # 处理staqc格式的Python数据
    staqc_python_path = './ulabel_data/python_staqc_qid2index_blocks_unlabeled.txt'
    staqc_python_single_save = './ulabel_data/staqc/single/python_staqc_single.txt'
    staqc_python_multiple_save = './ulabel_data/staqc/multiple/python_staqc_multiple.txt'
    data_staqc_processing(staqc_python_path, staqc_python_single_save, staqc_python_multiple_save)

    # 处理staqc格式的SQL数据
    staqc_sql_path = './ulabel_data/sql_staqc_qid2index_blocks_unlabeled.txt'
    staqc_sql_single_save = './ulabel_data/staqc/single/sql_staqc_single.txt'
    staqc_sql_multiple_save = './ulabel_data/staqc/multiple/sql_staqc_multiple.txt'
    data_staqc_processing(staqc_sql_path, staqc_sql_single_save, staqc_sql_multiple_save)

    # 处理大型Python数据
    large_python_path = './ulabel_data/python_codedb_qid2index_blocks_unlabeled.pickle'
    large_python_single_save = './ulabel_data/large_corpus/single/python_large_single.pickle'
    large_python_multiple_save = './ulabel_data/large_corpus/multiple/python_large_multiple.pickle'
    data_large_processing(large_python_path, large_python_single_save, large_python_multiple_save)

    # 处理大型SQL数据
    large_sql_path = './ulabel_data/sql_codedb_qid2index_blocks_unlabeled.pickle'
    large_sql_single_save = './ulabel_data/large_corpus/single/sql_large_single.pickle'
    large_sql_multiple_save = './ulabel_data/large_corpus/multiple/sql_large_multiple.pickle'
    data_large_processing(large_sql_path, large_sql_single_save, large_sql_multiple_save)

    # 转换未标记的单个数据为带标签的数据
    large_sql_single_label_save = './ulabel_data/large_corpus/single/sql_large_single_label.txt'
    large_python_single_label_save = './ulabel_data/large_corpus/single/python_large_single_label.txt'
    single_unlabeled_to_labeled(large_sql_single_save, large_sql_single_label_save)
    single_unlabeled_to_labeled(large_python_single_save, large_python_single_label_save)
