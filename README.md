# 软件工程实验
20211060076 王思琪

## 目录
- [一、项目概述](#一项目概述)
- [二、项目结构](#二项目结构)
- [三、文件说明](#三文件说明)
  - [3.1 embddings_process.py文件](#embddings_processpy文件)
  - [3.5 getStru2Vec.py文件](#getstru2vecpy文件)
  - [3.3 process_single_corpus.py文件](#process_single_corpuspy文件)
  - [3.4 python_structured.py文件](#python_structuredpy文件)
  - [3.5 sqlang_structured.py文件](#sqlang_structuredpy文件)
  - [3.6 word_dict.py文件](#word_dictpy文件)

## 一、项目概述
  此项目的python文件是对文本数据进行预测处理。通过给出python文件，对文件进行代码注释。
  
## 二、项目结构
```
├── hnn_preprocessing 
│   └── embddings_process.py  
│   └── getStru2Vec.py
│   └── process_single_corpus.py
│   └── python_structured.py
│   └── sqlang_structured.py
│   └── word_dict.py
```
## 三、文件说明

### embddings_process.py文件

#### 1 概述
  处理和序列化词向量和语料数据，以便后续的自然语言处理任务。

#### 2 具体功能描述

- `trans_bin(path1, path2)`：将文本格式的词向量文件转换并保存为二进制文件，以提高加载速度。
- `get_new_dict(type_vec_path, type_word_path, final_vec_path, final_word_path)`：根据给定的词向量文件和词典文件，构建新的词典和词向量矩阵，并保存为二进制文件。
- `get_index(type, text, word_dict)`:根据词典获取文本中每个词的位置索引。
- `serialization(word_dict_path, type_path, final_type_path)`:将语料数据序列化并保存为二进制文件。
- `主程序入口`:定义了各种文件路径，并调用上述函数进行词向量转换、词典构建和语料序列化。
---

### getStru2Vec.py文件

#### 1 概述
  并行处理Python和SQL的查询、代码和上下文数据。通过多进程处理，可以加快数据处理速度。

#### 2 具体功能描述

- `multipro_python_query(data_list)`：处理Python查询数据。
- `multipro_python_code(data_list)`：处理Python代码数据。
- `multipro_python_context(data_list)`:处理Python上下文数据。
- `multipro_sqlang_query(data_list)`:处理SQL查询数据。
- `multipro_sqlang_code(data_list)`:处理SQL代码数据。
- `multipro_sqlang_context(data_list)`:处理SQL上下文数据。
- `parse(data_list, split_num, context_func, query_func, code_func)`:使用多进程处理数据列表，并返回处理后的上下文、查询和代码数据。
- `main(lang_type, split_num, source_path, save_path, context_func, query_func, code_func)`:加载数据，调用解析函数处理数据，并将处理后的数据保存到文件中。
- `主程序入口`:定义了每个进程处理的数据量`split_num`，分别处理Python和SQL的Staqc数据和大型数据，并保存处理后的结果。
---

### process_single_corpus.py文件

#### 1 概述
  处理和拆分Python和SQL的查询数据，并将未标记的数据转换为带标签的数据。
  
#### 2 具体功能描述
- `load_pickle(filename)`:从文件中加载pickle格式的数据。
- `split_data(total_data, qids)`：根据问题ID的出现次数，将数据拆分为单个问题ID的数据和多个问题ID的数据。
- `data_staqc_processing(filepath, save_single_path, save_multiple_path)`:处理staqc格式的数据，将其拆分为单个和多个部分，并保存结果。
- `data_large_processing(filepath, save_single_path, save_multiple_path)`: 处理大型数据集，将其拆分为单个和多个部分，并保存结果。
- `single_unlabeled_to_labeled(input_path, output_path)`:将未标记的单个数据转换为带标签的数据，并保存结果。
- `主程序入口`:处理staqc格式的Python和SQL数据，处理大型Python和SQL数据，将未标记的单个数据转换为带标签的数据。
---

###  python_structured.py文件

#### 1 概述
  对数据进行处理和转换，包括加载数据、统计问题的单候选和多候选情况，将数据分为单候选和多候选部分，以及将有标签的数据生成为带有标签的形式。
  
#### 2 具体功能描述
- `repair_program_io(code)`：修复代码块中的输入输出标志，并返回修复后的代码和代码块列表。
- `get_vars(ast_root)`：提取代码中的变量，并返回排序后的变量集合。
- `get_vars_heuristics(code)`：使用启发式方法提取代码中的变量名。
- `PythonParser(code)`：解析Python代码，提取变量名，并对代码进行标记化处理。
- `revert_abbrev(line)`：使用正则表达式匹配并恢复常见的英语缩写形式。
- `get_wordpos(tag)`：根据词性标注的标签返回对应的词性。
- `process_nl_line(line)`：对句子进行预处理，包括恢复缩写、去除多余的制表符和换行符、去除括号内容、去除多余空格和骆驼命名转下划线。
- `process_sent_word(line)`：对句子进行分词处理，包括替换小数、字符串、十六进制、数字和特定字符，进行词性标注和词干提取。
- `filter_all_invachar(line)`：去除字符串中的非常用符号，包括制表符、换行符、连续的中横线和下划线，以及横杠。
- `filter_part_invachar(line)`：与`filter_all_invachar`类似，但保留部分符号。
- `python_code_parse(line)`：对Python代码进行预处理和解析，提取tokens。
- `python_query_parse(line)`：对自然语言查询进行预处理和解析，提取tokens。
- `python_context_parse(line)`：对自然语言上下文进行预处理和解析，提取tokens。
---

### sqlang_structured.py文件

#### 1 概述
  处理SQL代码和自然语言查询，提取tokens并进行预处理。
  
#### 2 具体功能描述
- `filter_all_invachar(line)`:去除字符串中的非常用符号，包括制表符、换行符、连续的中横线和下划线，以及横杠。
- `filter_part_invachar(line)`:与filter_all_invachar类似，但保留部分符号。
- `sqlang_code_parse(line)`:对SQL代码进行预处理和解析，提取tokens。
- `sqlang_query_parse(line)`:对自然语言查询进行预处理和解析，提取tokens。
- `sqlang_context_parse(line)对自然语言上下文进行预处理和解析，提取tokens。`:
- `revert_abbrev(line)`:使用正则表达式匹配并恢复常见的英语缩写形式。
- `get_wordpos(tag)`:根据词性标注的标签返回对应的词性。
- `process_nl_line(line)`:对句子进行预处理，包括恢复缩写、去除多余的制表符和换行符、去除括号内容、去除多余空格和骆驼命名转下划线。
- `process_sent_word(line)`:对句子进行分词处理，包括替换小数、字符串、十六进制、数字和特定字符，进行词性标注和词干提取。
- `filter_all_invachar(line)`:去除字符串中的非常用符号，包括制表符、换行符、连续的中横线和下划线，以及横杠。
- `filter_part_invachar(line)`:与`filter_all_invachar`类似，但保留部分符号。
- `sqlang_code_parse(line)`:对SQL代码进行预处理和解析，提取tokens。
- `sqlang_query_parse(line)`:对自然语言查询进行预处理和解析，提取tokens。
- `sqlang_context_parse(line)`:对自然语言上下文进行预处理和解析，提取tokens。
---

### word_dict.py文件

#### 1 概述
  从大词典中获取特定于于语料的词典；将数据处理成待打标签的形式
  
#### 2 具体功能描述
- `get_vocab(corpus1, corpus2)`:从两个语料库中提取词汇表，并返回词汇表。
- `load_pickle(filename)`:从文件中加载pickle格式的数据，并返回数据。
- `vocab_processing(filepath1, filepath2, save_path)`:从两个文件中加载数据，获取词汇表，排除不需要的词汇，并将处理后的词汇表保存到文件。
- `主程序入口`:定义了各种文件路径，调用了处理词汇表的函数`final_vocab_processing`。
---

