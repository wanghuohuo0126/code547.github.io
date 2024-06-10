import re
import sqlparse
import inflection
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

wnler = WordNetLemmatizer()
# 定义词性类别
ttypes = {0: "OTHER", 1: "FUNCTION", 2: "BLANK", 3: "KEYWORD", 4: "INTERNAL", 5: "TABLE", 6: "COLUMN", 7: "INTEGER",
          8: "FLOAT", 9: "HEX", 10: "STRING", 11: "WILDCARD", 12: "SUBQUERY", 13: "DUD", }

# 定义 sql 语句解析的regex 规则
scanner = re.Scanner([(r"\[[^\]]*\]", lambda scanner, token: token), (r"\+", lambda scanner, token: "REGPLU"),
                      (r"\*", lambda scanner, token: "REGAST"), (r"%", lambda scanner, token: "REGCOL"),
                      (r"\^", lambda scanner, token: "REGSTA"), (r"\$", lambda scanner, token: "REGEND"),
                      (r"\?", lambda scanner, token: "REGQUE"),
                      (r"[\.~``;_a-zA-Z0-9\s=:\{\}\-\\]+", lambda scanner, token: "REFRE"),
                      (r'.', lambda scanner, token: None), ])


# 定义代码的规则函数
def tokenizeRegex(s):
    results = scanner.scan(s)[0]
    return results


# 定义 SqlangParser 类
class SqlangParser():
    # 预处理 sql 语句，如统一小写、添加结束标记等
    @staticmethod
    def sanitizeSql(sql):
        s = sql.strip().lower()
        if not s[-1] == ";":
            s += ';'
        s = re.sub(r'\(', r' ( ', s)
        s = re.sub(r'\)', r' ) ', s)

        # 将指定单词结尾数字化
        words = ['index', 'table', 'day', 'year', 'user', 'text']
        for word in words:
            s = re.sub(r'([^\w])' + word + '$', r'\1' + word + '1', s)
            s = re.sub(r'([^\w])' + word + r'([^\w])', r'\1' + word + '1' + r'\2', s)
        s = s.replace('#', '')
        return s

    # 对 sql 语句中的字符串进行处理
    def parseStrings(self, tok):
        if isinstance(tok, sqlparse.sql.TokenList):
            for c in tok.tokens:
                self.parseStrings(c)
        elif tok.ttype == STRING:
            if self.regex:
                tok.value = ' '.join(tokenizeRegex(tok.value))
            else:
                tok.value = "CODSTR"

    # 改写 sql 语句中的标识符
    def renameIdentifiers(self, tok):
        if isinstance(tok, sqlparse.sql.TokenList):
            for c in tok.tokens:
                self.renameIdentifiers(c)
        elif tok.ttype == COLUMN:
            if str(tok) not in self.idMap["COLUMN"]:
                colname = "col" + str(self.idCount["COLUMN"])
                self.idMap["COLUMN"][str(tok)] = colname
                self.idMapInv[colname] = str(tok)
                self.idCount["COLUMN"] += 1
            tok.value = self.idMap["COLUMN"][str(tok)]
        elif tok.ttype == TABLE:
            if str(tok) not in self.idMap["TABLE"]:
                tabname = "tab" + str(self.idCount["TABLE"])
                self.idMap["TABLE"][str(tok)] = tabname
                self.idMapInv[tabname] = str(tok)
                self.idCount["TABLE"] += 1
            tok.value = self.idMap["TABLE"][str(tok)]
        elif tok.ttype == FLOAT:
            tok.value = "CODFLO"
        elif tok.ttype == INTEGER:
            tok.value = "CODINT"
        elif tok.ttype == HEX:
            tok.value = "CODHEX"

    # 在类中定义函数，进行sql解析
    def __hash__(self):  # 为对象提供hash值
        return hash(tuple([str(x) for x in self.tokensWithBlanks]))

    def __init__(self, sql, regex=False, rename=True):  # 类的初始化函数
        self.sql = SqlangParser.sanitizeSql(sql)  # sql是输入的sql文本
        self.idMap = {"COLUMN": {}, "TABLE": {}}
        self.idMapInv = {}
        self.idCount = {"COLUMN": 0, "TABLE": 0}
        self.regex = regex
        # 对输入的sql进行解析
        self.parse = sqlparse.parse(self.sql)
        self.parse = [self.parse[0]]
        self.removeWhitespaces(self.parse[0])
        self.identifyLiterals(self.parse[0])
        self.parse[0].ptype = SUBQUERY
        self.identifySubQueries(self.parse[0])
        self.identifyFunctions(self.parse[0])
        self.identifyTables(self.parse[0])

        self.parseStrings(self.parse[0])
        if rename:
            self.renameIdentifiers(self.parse[0])
        self.tokens = SqlangParser.getTokens(self.parse)

    def getTokens(parse):  # 定义解析sql中的Token
        flatParse = []
        for expr in parse:
            for token in expr.flatten():
                if token.ttype == STRING:
                    flatParse.extend(str(token).split(' '))
                else:
                    flatParse.append(str(token))
        return flatParse

    def removeWhitespaces(self, tok):  # 移除空白
        if isinstance(tok, sqlparse.sql.TokenList):  # 如果Token是Token序列
            tmpChildren = []
            for c in tok.tokens:
                if not c.is_whitespace:  # 如果Token不是空白
                    tmpChildren.append(c)
            tok.tokens = tmpChildren
            for c in tok.tokens:
                self.removeWhitespaces(c)

    # 在类中继续定义关于sql解析的函数
    def identifySubQueries(self, tokenList):  # 识别子查询
        isSubQuery = False
        for tok in tokenList.tokens:
            if isinstance(tok, sqlparse.sql.TokenList):  # 如果是Token序列
                subQuery = self.identifySubQueries(tok)  # 调用函数自身，识别子查询
                if (subQuery and isinstance(tok, sqlparse.sql.Parenthesis)):  # 如果有子查询，并且Token是一个带括号的expression
                    tok.ttype = SUBQUERY  # 则将此Token的类型设为SUBQUERY
                elif str(tok) == "select":  # 如果Token是"select"
                    isSubQuery = True  # 则启动子查询标记
        return isSubQuery  # 返回是否有子查询的标记

    def identifyLiterals(self, tokenList):
        # 定义空白标记和空白标记类型
        blankTokens = [sqlparse.tokens.Name, sqlparse.tokens.Name.Placeholder]
        blankTokenTypes = [sqlparse.sql.Identifier]

        # 遍历 tokenList 中的每个 token
        for tok in tokenList.tokens:
            # 如果当前 token 是 TokenList（子列表），则递归调用 identifyLiterals
            if isinstance(tok, sqlparse.sql.TokenList):
                tok.ptype = INTERNAL
                self.identifyLiterals(tok)
            # 如果当前 token 是关键字或者等于 "select"，则标记为关键字
            elif (tok.ttype == sqlparse.tokens.Keyword or str(tok) == "select"):
                tok.ttype = KEYWORD
            # 如果当前 token 是整数或者整数文字，则标记为整数
            elif (tok.ttype == sqlparse.tokens.Number.Integer or tok.ttype == sqlparse.tokens.Literal.Number.Integer):
                tok.ttype = INTEGER
            # 如果当前 token 是十六进制数或者十六进制数文字，则标记为十六进制数
            elif (
                    tok.ttype == sqlparse.tokens.Number.Hexadecimal or tok.ttype == sqlparse.tokens.Literal.Number.Hexadecimal):
                tok.ttype = HEX
            # 如果当前 token 是浮点数或者浮点数文字，则标记为浮点数
            elif (tok.ttype == sqlparse.tokens.Number.Float or tok.ttype == sqlparse.tokens.Literal.Number.Float):
                tok.ttype = FLOAT
            # 如果当前 token 是字符串符号、单引号字符串或者单引号字符串文字，则标记为字符串
            elif (
                    tok.ttype == sqlparse.tokens.String.Symbol or tok.ttype == sqlparse.tokens.String.Single or tok.ttype == sqlparse.tokens.Literal.String.Single or tok.ttype == sqlparse.tokens.Literal.String.Symbol):
                tok.ttype = STRING
            # 如果当前 token 是通配符，则标记为通配符
            elif (tok.ttype == sqlparse.tokens.Wildcard):
                tok.ttype = WILDCARD
            # 如果当前 token 是空白标记或者是空白标记类型中的一个，则标记为列
            elif (tok.ttype in blankTokens or isinstance(tok, blankTokenTypes[0])):
                tok.ttype = COLUMN

    def identifyFunctions(self, tokenList):
        # 遍历 tokenList 中的每个 token
        for tok in tokenList.tokens:
            # 如果当前 token 是函数，则设置解析树标志为 True
            if (isinstance(tok, sqlparse.sql.Function)):
                self.parseTreeSentinel = True
            # 如果当前 token 是括号，则设置解析树标志为 False
            elif (isinstance(tok, sqlparse.sql.Parenthesis)):
                self.parseTreeSentinel = False
            # 如果解析树标志为 True，则将当前 token 标记为函数
            if self.parseTreeSentinel:
                tok.ttype = FUNCTION
            # 递归调用 identifyFunctions 处理子列表
            if isinstance(tok, sqlparse.sql.TokenList):
                self.identifyFunctions(tok)

    def identifyTables(self, tokenList):
        # 如果 tokenList 的类型为子查询，则将 False 推入表堆栈
        if tokenList.ptype == SUBQUERY:
            self.tableStack.append(False)

        # 遍历 tokenList 中的每个 token
        for i in range(len(tokenList.tokens)):
            prevtok = tokenList.tokens[i - 1]
            tok = tokenList.tokens[i]

            # 如果当前 token 是 "."，并且前一个 token 是列，则将前一个 token 标记为表
            if (str(tok) == "." and tok.ttype == sqlparse.tokens.Punctuation and prevtok.ttype == COLUMN):
                prevtok.ttype = TABLE

            # 如果当前 token 是 "from"，则将表堆栈顶部的标志设置为 True
            elif (str(tok) == "from" and tok.ttype == sqlparse.tokens.Keyword):
                self.tableStack[-1] = True

            # 如果当前 token 是 "where"、"on"、"group"、"order" 或者 "union"，则将表堆栈顶部的标志设置为 False
            elif ((str(tok) == "where" or str(tok) == "on" or str(tok) == "group" or str(tok) == "order" or str(
                    tok) == "union") and tok.ttype == sqlparse.tokens.Keyword):
                self.tableStack[-1] = False

            # 如果当前 token 是 TokenList（子列表），则递归调用 identifyTables
            if isinstance(tok, sqlparse.sql.TokenList):
                self.identifyTables(tok)
            # 如果当前 token 是列，并且表堆栈顶部的标志为 True，则将当前 token 标记为表
            elif (tok.ttype == COLUMN):
                if self.tableStack[-1]:
                    tok.ttype = TABLE

        # 如果 tokenList 的类型为子查询，则从表堆栈中弹出一个元素
        if tokenList.ptype == SUBQUERY:
            self.tableStack.pop()

    # 返回 tokenList 中所有 token 的字符串表示形式，以空格分隔
    def __str__(self):
        return ' '.join([str(tok) for tok in self.tokens])

    # 解析 SQL 查询语句，返回所有 token 的字符串表示形式列表
    def parseSql(self):
        return [str(tok) for tok in self.tokens]


#############################################################################

#############################################################################
# 缩略词还原函数
def revert_abbrev(line):
    # 缩略词的正则表达式匹配模式
    pat_is = re.compile("(it|he|she|that|this|there|here)(\"s)", re.I)  # it's, he's, she's, etc.
    pat_s1 = re.compile("(?<=[a-zA-Z])\"s")  # 's
    pat_s2 = re.compile("(?<=s)\"s?")  # s
    pat_not = re.compile("(?<=[a-zA-Z])n\"t")  # not
    pat_would = re.compile("(?<=[a-zA-Z])\"d")  # would
    pat_will = re.compile("(?<=[a-zA-Z])\"ll")  # will
    pat_am = re.compile("(?<=[I|i])\"m")  # am
    pat_are = re.compile("(?<=[a-zA-Z])\"re")  # are
    pat_ve = re.compile("(?<=[a-zA-Z])\"ve")  # have

    # 替换缩略词
    line = pat_is.sub(r"\1 is", line)
    line = pat_s1.sub("", line)
    line = pat_s2.sub("", line)
    line = pat_not.sub(" not", line)
    line = pat_would.sub(" would", line)
    line = pat_will.sub(" will", line)
    line = pat_am.sub(" am", line)
    line = pat_are.sub(" are", line)
    line = pat_ve.sub(" have", line)

    return line

# 获取词性函数
def get_wordpos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None

# 处理句子函数
def process_nl_line(line):
    # 句子预处理
    line = revert_abbrev(line)  # 缩略词还原
    line = re.sub('\t+', '\t', line)
    line = re.sub('\n+', '\n', line)
    line = line.replace('\n', ' ')
    line = line.replace('\t', ' ')
    line = re.sub(' +', ' ', line)
    line = line.strip()
    # 骆驼命名转下划线
    line = inflection.underscore(line)

    # 去除括号里内容
    space = re.compile(r"\([^\(|^\)]+\)")  # 匹配括号及其内容
    line = re.sub(space, '', line)
    # 去除末尾.和空格
    line=line.strip()
    return line

# 处理句子的分词函数
def process_sent_word(line):
    # 找单词
    line = re.findall(r"[\w]+|[^\s\w]", line)
    line = ' '.join(line)

    # 替换小数
    decimal = re.compile(r"\d+(\.\d+)+")
    line = re.sub(decimal, 'TAGINT', line)
    # 替换字符串
    string = re.compile(r'\"[^\"]+\"')
    line = re.sub(string, 'TAGSTR', line)
    # 替换十六进制
    decimal = re.compile(r"0[xX][A-Fa-f0-9]+")
    line = re.sub(decimal, 'TAGINT', line)
    # 替换数字 56
    number = re.compile(r"\s?\d+\s?")
    line = re.sub(number, ' TAGINT ', line)
    # 替换字符 6c60b8e1
    other = re.compile(r"(?<![A-Z|a-z|_|])\d+[A-Za-z]+")  # 后缀匹配
    line = re.sub(other, 'TAGOER', line)
    cut_words= line.split(' ')
    # 全部小写化
    cut_words = [x.lower() for x in cut_words]
    # 词性标注
    word_tags = pos_tag(cut_words)
    tags_dict = dict(word_tags)
    word_list=[]
    for word in cut_words:
        word_pos = get_wordpos(tags_dict[word])
        if word_pos in ['a', 'v', 'n', 'r']:
            # 词性还原
            word = wnler.lemmatize(word, pos=word_pos)
        # 词干提取
        word = wordnet.morphy(word) if wordnet.morphy(word) else word
        word_list.append(word)
    return word_list


#############################################################################

def filter_all_invachar(line):
    # 去除非常用符号；防止解析有误
    line = re.sub('[^(0-9|a-z|A-Z|\-|_|\'|\"|\-|\(|\)|\n)]+', ' ', line)
    # 包括\r\t也清除了
    # 中横线
    line = re.sub('-+', '-', line)
    # 下划线
    line = re.sub('_+', '_', line)
    # 去除横杠
    line = line.replace('|', ' ').replace('¦', ' ')
    return line


def filter_part_invachar(line):
    #去除非常用符号；防止解析有误
    line= re.sub('[^(0-9|a-z|A-Z|\-|#|/|_|,|\'|=|>|<|\"|\-|\\|\(|\)|\?|\.|\*|\+|\[|\]|\^|\{|\}|\n)]+',' ', line)
    #包括\r\t也清除了
    # 中横线
    line = re.sub('-+', '-', line)
    # 下划线
    line = re.sub('_+', '_', line)
    # 去除横杠
    line = line.replace('|', ' ').replace('¦', ' ')
    return line

########################主函数：代码的tokens#################################
# 处理SQL代码中的词语函数
def sqlang_code_parse(line):
    # 过滤非法字符
    line = filter_part_invachar(line)
    # 合并多个点为一个点
    line = re.sub('\.+', '.', line)
    # 合并多个制表符为一个制表符
    line = re.sub('\t+', '\t', line)
    # 合并多个换行符为一个换行符
    line = re.sub('\n+', '\n', line)
    # 合并多个空格为一个空格
    line = re.sub(' +', ' ', line)
    # 去除多个连续的右尖括号
    line = re.sub('>>+', '', line)
    # 替换小数为 'number'
    line = re.sub(r"\d+(\.\d+)+", 'number', line)

    # 去除两端的换行符和空格
    line = line.strip('\n').strip()
    # 分词
    line = re.findall(r"[\w]+|[^\s\w]", line)
    line = ' '.join(line)

    try:
        # 解析SQL语句
        query = SqlangParser(line, regex=True)
        typedCode = query.parseSql()
        typedCode = typedCode[:-1]
        # 将驼峰命名转换为下划线命名，并分词
        typedCode = inflection.underscore(' '.join(typedCode)).split(' ')

        cut_tokens = [re.sub("\s+", " ", x.strip()) for x in typedCode]
        # 全部小写化
        token_list = [x.lower() for x in cut_tokens]
        # 去除空字符串
        token_list = [x.strip() for x in token_list if x.strip() != '']
        # 返回处理后的词语列表
        return token_list
    # 处理可能为空的情况
    except:
        return '-1000'

# 处理SQL查询语句中的词语函数
def sqlang_query_parse(line):
    # 过滤非法字符
    line = filter_all_invachar(line)
    # 处理自然语言句子
    line = process_nl_line(line)
    # 分词处理
    word_list = process_sent_word(line)
    # 去除括号
    for i in range(0, len(word_list)):
        if re.findall('[\(\)]', word_list[i]):
            word_list[i] = ''
    # 去除空字符串
    word_list = [x.strip() for x in word_list if x.strip() != '']
    # 返回处理后的词语列表
    return word_list

# 处理SQL上下文语境中的词语函数
def sqlang_context_parse(line):
    # 过滤非法字符
    line = filter_part_invachar(line)
    # 处理自然语言句子
    line = process_nl_line(line)
    # 分词处理
    word_list = process_sent_word(line)
    # 去除空字符串
    word_list = [x.strip() for x in word_list if x.strip() != '']
    # 返回处理后的词语列表
    return word_list


#######################主函数：句子的tokens##################################
if __name__ == '__main__':
    # 解析 SQL 代码并打印处理后的词语列表
    print(sqlang_code_parse('""geometry": {"type": "Polygon" , 111.676,"coordinates": [[[6.69245274714546, 51.1326962505233], [6.69242714158622, 51.1326908883821], [6.69242919794447, 51.1326955158344], [6.69244041615532, 51.1326998744549], [6.69244125953742, 51.1327001609189], [6.69245274714546, 51.1326962505233]]]} How to 123 create a (SQL  Server function) to "join" multiple rows from a subquery into a single delimited field?'))

    # 解析 SQL 查询语句并打印处理后的词语列表
    print(sqlang_query_parse("change row_height and column_width in libreoffice calc use python tagint"))
    print(sqlang_query_parse('MySQL Administrator Backups: "Compatibility Mode", What Exactly is this doing?'))

    # 解析 SQL 代码并打印处理后的词语列表
    print(sqlang_code_parse('>UPDATE Table1 \n SET Table1.col1 = Table2.col1 \n Table1.col2 = Table2.col2 FROM \n Table2 WHERE \n Table1.id =  Table2.id'))
    print(sqlang_code_parse("SELECT\n@supplyFee:= 0\n@demandFee := 0\n@charedFee := 0\n"))
    print(sqlang_code_parse('@prev_sn := SerialNumber,\n@prev_toner := Remain_Toner_Black\n'))
    print(sqlang_code_parse(' ;WITH QtyCTE AS (\n  SELECT  [Category] = c.category_name\n          , [RootID] = c.category_id\n          , [ChildID] = c.category_id\n  FROM    Categories c\n  UNION ALL \n  SELECT  cte.Category\n          , cte.RootID\n          , c.category_id\n  FROM    QtyCTE cte\n          INNER JOIN Categories c ON c.father_id = cte.ChildID\n)\nSELECT  cte.RootID\n        , cte.Category\n        , COUNT(s.sales_id)\nFROM    QtyCTE cte\n        INNER JOIN Sales s ON s.category_id = cte.ChildID\nGROUP BY cte.RootID, cte.Category\nORDER BY cte.RootID\n'))
    print(sqlang_code_parse("DECLARE @Table TABLE (ID INT, Code NVARCHAR(50), RequiredID INT);\n\nINSERT INTO @Table (ID, Code, RequiredID)   VALUES\n    (1, 'Physics', NULL),\n    (2, 'Advanced Physics', 1),\n    (3, 'Nuke', 2),\n    (4, 'Health', NULL);    \n\nDECLARE @DefaultSeed TABLE (ID INT, Code NVARCHAR(50), RequiredID INT);\n\nWITH hierarchy \nAS (\n    --anchor\n    SELECT  t.ID , t.Code , t.RequiredID\n    FROM @Table AS t\n    WHERE t.RequiredID IS NULL\n\n    UNION ALL   \n\n    --recursive\n    SELECT  t.ID \n          , t.Code \n          , h.ID        \n    FROM hierarchy AS h\n        JOIN @Table AS t \n            ON t.RequiredID = h.ID\n    )\n\nINSERT INTO @DefaultSeed (ID, Code, RequiredID)\nSELECT  ID \n        , Code \n        , RequiredID\nFROM hierarchy\nOPTION (MAXRECURSION 10)\n\n\nDECLARE @NewSeed TABLE (ID INT IDENTITY(10, 1), Code NVARCHAR(50), RequiredID INT)\n\nDeclare @MapIds Table (aOldID int,aNewID int)\n\n;MERGE INTO @NewSeed AS TargetTable\nUsing @DefaultSeed as Source on 1=0\nWHEN NOT MATCHED then\n Insert (Code,RequiredID)\n Values\n (Source.Code,Source.RequiredID)\nOUTPUT Source.ID ,inserted.ID into @MapIds;\n\n\nUpdate @NewSeed Set RequiredID=aNewID\nfrom @MapIds\nWhere RequiredID=aOldID\n\n\n/*\n--@NewSeed should read like the following...\n[ID]  [Code]           [RequiredID]\n10....Physics..........NULL\n11....Health...........NULL\n12....AdvancedPhysics..10\n13....Nuke.............12\n*/\n\nSELECT *\nFROM @NewSeed\n"))



