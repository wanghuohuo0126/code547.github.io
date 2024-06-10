# 软件工程实验
20211060076 王思琪

## 目录
- [一、项目概述](#一项目概述)
- [二、项目结构](#二项目结构)
- [三、文件说明](#三文件说明)
  - [3.1 process_single_corpus.py文件](#process_single_corpuspy文件)
  - [3.2 word_dict.py文件](#word_dictpy文件)
  - [3.3 python_structured.py文件](#python_structuredpy文件)
  - [3.4 sqlang_structured.py文件](#sqlang_structuredpy文件)
  - [3.5 getSru2Vec.py文件](#getsru2vecpy文件)
  - [3.6 embddings_process.py文件](#embddings_processpy文件)
- [四、总结](#四总结)

## 一、项目概述
  此项目的python文件是对文本数据进行预测处理。通过给出python文件，对文件进行代码注释。
  
## 二、项目结构
```
├── ulabel_data
│   └── embaddings_process.py  
│   └── getStru2Vec.py
│   └── process_single_corpus.py
│   └── python_structured.py
│   └── sqlang_structured.py
│   └── word_dirt.py
```
## 三、文件说明

### process_single_corpus.py文件

#### 1 概述
  把语料中的单候选和多候选分隔开

#### 2 具体功能描述

- `load_pickle(filename)`：读取pickle二进制文件。
- `single_list(arr, target)`：计算一个列表中指定元素的出现次数。arr为
- `data_staqc_prpcessing(filepath,single_path,mutiple_path)`:把语料中的单候选和多候选分隔开。
---

### word_dict.py文件

#### 1. 概述
该代码用于构建词典，通过遍历语料库中的数据，将所有单词添加到一个集合中，从而构建词汇表。在构建最终词汇表时，首先加载已有的词汇表，然后获取新的词汇表，并找到新的单词。最后，将新的单词保存到最终词汇表文件中。

#### 2. 具体功能
- `get_vocab`：根据给定的两个语料库，获取词汇表。该函数遍历语料库中的数据，并将所有单词添加到一个集合中，最终返回词汇表。
- `load_pickle`：从pickle文件中加载数据并返回。
- `vocab_processing`：用于处理语料库文件和保存词汇表的文件路径。该函数调用load_pickle()函数加载语料库数据，然后调用get_vocab()函数获取词汇表，并将词汇表保存到指定的文件路径中。
- `final_vocab_processing`：首先从文件中加载已有的词汇表，然后调用get_vocab()函数获取新的词汇表。将新的词汇表与已有词汇表进行比较，找到新的单词，并将其保存到指定的文件路径中。

### python_structured.py文件

#### 1 概述
  解析 Python 代码，修复代码中的变量命名问题；
  代码重构，添加变量名的注释。
  
#### 2 具体功能描述
- `format_io(code)`:修复 Python 程序中的标准输入/输出（I/O）格式。
- `get_vars(ast_root)`：获取变量名。
- `get_all_vars(code)`:一个具有启发式的解析器，旨在从 code 字符串中尽可能多地提取变量名。
- `PythonParser(code)`: 将代码字符串解析为Token 序列，并且执行变量解析。
 └──`first_trial(_code)`:尝试将该代码字符串解析为token令牌序列。
- `revert_abbrev(line)`:缩略词处理，将常见的英语缩写还原为它们的原始形式。
- `get_word_pos(tag)`:获取词性。
- `preprocess_sentence(line)`:对传入的一行文本进行处理预处理：空格，还原缩写，下划线命名，去括号，去除开头末尾空格。
- `process_words(line)`:对一个句子进行分词、词性标注、还原和提取词干的功能。
- `filter_all_invachar(line)`：过滤掉Python代码中不常用的字符，以减少解析时的错误。
- `filter_part_invachar(line)`:过滤掉Python代码中部分不常用的字符，以减少解析时的错误。
- `python_query_parse(line)`:解析 python 查询语句，进行文本预处理。
- `python_all_context_parse(line)`:将提供的文本进行标准化和归一化处理,除去所有特殊字符。
- `python_part_context_parse(line)`:将提供的文本进行标准化和归一化处理,除去部分特殊字符。
---

### sqlang_structured.py文件

#### 1 概述
  解析 SQL 代码，修复代码中的变量命名问题；
  代码重构，添加变量名的注释。
  
#### 2 具体功能描述
- `string_scanner(s)`:扫描字符串。
- `SqlParser()`: SQL语句处理。  
   └──`formatSql(sql)`:对输入的SQL语句进行清理和标准化。  
   └──`parseStringsTokens(self, tok)`:将输入的SQL解析为一个SQL令牌列表,并对其进行处理。    
   └──`renameIdentifiers(self, tok)`:重命名 SQL 语句中的标识符。  
   └──` _hash_(self)`:将 SQL 解析器对象哈希化。  
   └──`_init__(self, sql, regex=False, rename=True)`:初始化。  
   └──`getTokens(parse)`:获取令牌序列。  
   └──` removeWhitespaces(self, tok)`:删除多余空格。  
   └──`identifySubQueries(self, tokenList)`:识别 SQL 表达式中的子查询。  
   └──`identifyLiterals(self, tokenList)`:用于标识 SQL 解析器对象中的不同类型的文本字面量。  
   └──`identifyFunctions(self, tokenList)`:从给定的token列表中识别SQL语句中的函数并设置ttype类型。  
   └──`identifyTables(self, tokenList)`:标识SQL语句中的表（table）与列（column），并在token的ttype属性中记录信息来标识识别的结果。    
   └──`__str__(self)`:将SQL语句的tokens列表中的所有token连接成一个字符串。  
   └──`parseSql(self)`:返回SQL语句中所有token的字符串列表。
- `revert_abbrev(line)`:缩略词处理，将常见的英语缩写还原为它们的原始形式。
- `get_word_pos(tag)`:获取词性。
- `preprocess_sentence(line)`:对传入的一行文本进行处理预处理：空格，还原缩写，下划线命名，去括号，去除开头末尾空格。
- `process_words(line)`:对一个句子进行分词、词性标注、还原和提取词干的功能。
- `filter_all_invachar(line)`：过滤掉SQL代码中不常用的字符，以减少解析时的错误。
- `filter_part_invachar(line)`:过滤掉SQL代码中部分不常用的字符，以减少解析时的错误。
- `sql_query_parse(line)`:解析 SQL 查询语句，进行文本预处理。
- `sql_all_context_parse(line)`:将提供的文本进行标准化和归一化处理,除去所有特殊字符。
- `sqlpart_context_parse(line)`:将提供的文本进行标准化和归一化处理,除去部分特殊字符。

---

### getStru2Vec.py文件

#### 1 概述
  获取最终的python解析文本和SQL解析文本。
  
#### 2 具体功能描述
- `multipro_python_query(data_list)`:Python 查询解析方法。
- `multipro_python_code(data_list)`:Python 代码解析方法。
- `multipro_python_context(data_list)`:Python 上下文解析方法。
- `multipro_sql_query(data_list)`:SQL查询解析方法。
- `multipro_sql_code(data_list)`:SQL代码解析方法。
- `multipro_sql_context(data_list)`:SQL上下文解析方法。
- `python_parse_final(python_list,split_num)`:最终的python版解析函数。
- `sql_parse_final(sql_list,split_num)`:最终的sql版解析函数。
- `main(lang_type,split_num,source_path,save_path)`:将两个版本的解析集合到一个函数中，并保存解析结果。
- `test(path1,path2)`:测试文件是否保存成功。
---

### embaddings_process.py文件

#### 1 概述
  从大词典中获取特定于于语料的词典；将数据处理成待打标签的形式
  
#### 2 具体功能描述
- `trans_bin(word_path,bin_path)`:词向量文件保存成bin文件。t
- `get_new_dict(type_vec_path,type_word_path,final_vec_path,final_word_path)`:构建新的词典和词向量矩阵。
- `get_index(type,text,word_dict)`:得到词在词典中的位置。
- `Serialization(word_dict_path,type_path,final_type_path)`:将训练、测试、验证语料序列化。
- `get_new_dict_append(type_vec_path,previous_dict,previous_vec,append_word_path,final_vec_path,final_word_path)`:将文件`append_word_path`中包含的新词添加到词典中，并在原有的词向量词表中按顺序添加相应的词向量。函数会先加载类型为`word2vec`的词标签及其对应的词向量。
---

## 四、总结  
在本次实验中，学习并掌握了规范化代码。并且初步了解了npl项目如何进行文本数据的预处理与分析。

