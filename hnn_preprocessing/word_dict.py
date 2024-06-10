import pickle

# 获取词汇表
def get_vocab(corpus1, corpus2):
    word_vocab = set()  # 创建空集合，用于存储词汇表
    for corpus in [corpus1, corpus2]:  # 遍历语料库
        for i in range(len(corpus)):  # 遍历每个数据
            # 更新词汇表
            word_vocab.update(corpus[i][1][0])  # 更新问题文本的词汇
            word_vocab.update(corpus[i][1][1])  # 更新答案文本的词汇
            word_vocab.update(corpus[i][2][0])  # 更新代码文本的词汇
            word_vocab.update(corpus[i][3])  # 更新标签的词汇
    print(len(word_vocab))  # 打印词汇表大小
    return word_vocab  # 返回词汇表

# 加载pickle格式的数据
def load_pickle(filename):
    with open(filename, 'rb') as f:
        data = pickle.load(f)  # 使用pickle加载数据
    return data  # 返回数据

# 处理词汇表
def vocab_processing(filepath1, filepath2, save_path):
    with open(filepath1, 'r') as f:
        total_data1 = set(eval(f.read()))  # 读取并解析数据
    with open(filepath2, 'r') as f:
        total_data2 = eval(f.read())  # 读取并解析数据

    word_set = get_vocab(total_data2, total_data2)  # 获取词汇表

    excluded_words = total_data1.intersection(word_set)  # 找到需要排除的词汇
    word_set = word_set - excluded_words  # 从词汇表中去除需要排除的词汇

    print(len(total_data1))  # 打印原始词汇表大小
    print(len(word_set))  # 打印处理后的词汇表大小

    with open(save_path, 'w') as f:
        f.write(str(word_set))  # 将处理后的词汇表保存到文件

if __name__ == "__main__":
    # 定义文件路径
    python_hnn = './data/python_hnn_data_teacher.txt'
    python_staqc = './data/staqc/python_staqc_data.txt'
    python_word_dict = './data/word_dict/python_word_vocab_dict.txt'

    sql_hnn = './data/sql_hnn_data_teacher.txt'
    sql_staqc = './data/staqc/sql_staqc_data.txt'
    sql_word_dict = './data/word_dict/sql_word_vocab_dict.txt'

    new_sql_staqc = './ulabel_data/staqc/sql_staqc_unlabled_data.txt'
    new_sql_large = './ulabel_data/large_corpus/multiple/sql_large_multiple_unlable.txt'
    large_word_dict_sql = './ulabel_data/sql_word_dict.txt'

    final_vocab_processing(sql_word_dict, new_sql_large, large_word_dict_sql)  # 调用处理词汇表的函数
