import pickle
import multiprocessing
from python_structured import *
from sqlang_structured import *

# 多进程处理Python查询数据
def multipro_python_query(data_list):
    return [python_query_parse(line) for line in data_list]

# 多进程处理Python代码数据
def multipro_python_code(data_list):
    return [python_code_parse(line) for line in data_list]

# 多进程处理Python上下文数据
def multipro_python_context(data_list):
    result = []
    for line in data_list:
        if line == '-10000':
            result.append(['-10000'])
        else:
            result.append(python_context_parse(line))
    return result

# 多进程处理SQL查询数据
def multipro_sqlang_query(data_list):
    return [sqlang_query_parse(line) for line in data_list]

# 多进程处理SQL代码数据
def multipro_sqlang_code(data_list):
    return [sqlang_code_parse(line) for line in data_list]

# 多进程处理SQL上下文数据
def multipro_sqlang_context(data_list):
    result = []
    for line in data_list:
        if line == '-10000':
            result.append(['-10000'])
        else:
            result.append(sqlang_context_parse(line))
    return result

# 解析数据
def parse(data_list, split_num, context_func, query_func, code_func):
    pool = multiprocessing.Pool()  # 创建进程池
    split_list = [data_list[i:i + split_num] for i in range(0, len(data_list), split_num)]  # 将数据列表分割成小块
    results = pool.map(context_func, split_list)  # 并行处理上下文数据
    context_data = [item for sublist in results for item in sublist]  # 将结果展开成一维列表
    print(f'context条数：{len(context_data)}')

    results = pool.map(query_func, split_list)  # 并行处理查询数据
    query_data = [item for sublist in results for item in sublist]  # 将结果展开成一维列表
    print(f'query条数：{len(query_data)}')

    results = pool.map(code_func, split_list)  # 并行处理代码数据
    code_data = [item for sublist in results for item in sublist]  # 将结果展开成一维列表
    print(f'code条数：{len(code_data)}')

    pool.close()  # 关闭进程池
    pool.join()  # 等待所有子进程结束

    return context_data, query_data, code_data  # 返回处理后的数据

# 主函数
def main(lang_type, split_num, source_path, save_path, context_func, query_func, code_func):
    with open(source_path, 'rb') as f:
        corpus_lis = pickle.load(f)  # 从文件中加载数据

    context_data, query_data, code_data = parse(corpus_lis, split_num, context_func, query_func, code_func)  # 解析数据
    qids = [item[0] for item in corpus_lis]  # 获取问题ID列表

    total_data = [[qids[i], context_data[i], code_data[i], query_data[i]] for i in range(len(qids))]  # 组合处理后的数据

    with open(save_path, 'wb') as f:
        pickle.dump(total_data, f)  # 将处理后的数据保存到文件中

if __name__ == '__main__':
    split_num = 100  # 每个进程处理的数据量

    # Python数据处理
    staqc_python_path = '.ulabel_data/python_staqc_qid2index_blocks_unlabeled.txt'  # Python数据源文件路径
    staqc_python_save = '../hnn_process/ulabel_data/staqc/python_staqc_unlabled_data.pkl'  # 处理后的数据保存路径
    main(python_type, split_num, staqc_python_path, staqc_python_save, multipro_python_context, multipro_python_query, multipro_python_code)

    # SQL数据处理
    staqc_sql_path = './ulabel_data/sql_staqc_qid2index_blocks_unlabeled.txt'  # SQL数据源文件路径
    staqc_sql_save = './ulabel_data/staqc/sql_staqc_unlabled_data.pkl'  # 处理后的数据保存路径
    main(sqlang_type, split_num, staqc_sql_path, staqc_sql_save, multipro_sqlang_context, multipro_sqlang_query, multipro_sqlang_code)

    # 大型Python数据处理
    large_python_path = './ulabel_data/large_corpus/multiple/python_large_multiple.pickle'  # 大型Python数据源文件路径
    large_python_save = '../hnn_process/ulabel_data/large_corpus/multiple/python_large_multiple_unlable.pkl'  # 处理后的数据保存路径
    main(python_type, split_num, large_python_path, large_python_save, multipro_python_context, multipro_python_query, multipro_python_code)

    # 大型SQL数据处理
    large_sql_path = './ulabel_data/large_corpus/multiple/sql_large_multiple.pickle'  # 大型SQL数据源文件路径
    large_sql_save = './ulabel_data/large_corpus/multiple/sql_large_multiple_unlable.pkl'  # 处理后的数据保存路径
    main(sqlang_type, split_num, large_sql_path, large_sql_save, multipro_sqlang_context, multipro_sqlang_query, multipro_sqlang_code)
