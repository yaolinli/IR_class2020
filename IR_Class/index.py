# -*- coding: utf-8 -*-
"""
@author: yaolinli
"""
from tqdm import tqdm
import jieba
import os
import re
import json
from collections import OrderedDict
#按行读取文件，返回文件的行字符串列表
def read_file(filename):
    f = open(filename,"r",encoding='utf-8')
    docs = list()
    for line in f.readlines():
        line = line.strip()
        if not len(line):
            continue
        docs.append(line)
    f.close()
    #去除行末的换行符，否则会在停用词匹配的过程中产生干扰
    label = list()
    for i in range(len(docs)):
        doc = docs[i].rstrip("\n")
        label.append(doc[0])
        docs[i] = doc[2:]
    
    return docs,label


def read_stopwords(filename):
    f = open(filename,"r")
    words = list()
    for line in f.readlines():
        line = line.strip()
        if not len(line):
            continue
        words.append(line)
    f.close()
    for i in range(len(words)):
        words[i] = words[i].rstrip("\n")
    return words

def regex_change(line):
    #前缀的正则
    username_regex = re.compile(r"^\d+::")
    #过滤URL，为了防止对中文的过滤，所以使用[a-zA-Z0-9]而不是\w
    url_regex = re.compile(r"""
        (https?://)?
        ([a-zA-Z0-9]+)
        (\.[a-zA-Z0-9]+)
        (\.[a-zA-Z0-9]+)*
        (/[a-zA-Z0-9]+)*
    """, re.VERBOSE|re.IGNORECASE)
    #剔除日期
    data_regex = re.compile(u"""        #utf-8编码
        年 |
        月 |
        日 |
        (周一) |
        (周二) | 
        (周三) | 
        (周四) | 
        (周五) | 
        (周六)
    """, re.VERBOSE)
    #剔除所有数字
    decimal_regex = re.compile(r"[^a-zA-Z]\d+")
    #剔除空格
    space_regex = re.compile(r"\s+")

    line = username_regex.sub(r"", line)
    line = url_regex.sub(r"", line)
    line = data_regex.sub(r"", line)
    line = decimal_regex.sub(r"", line)
    line = space_regex.sub(r"", line)
    return line

def json_save(index_dict,filename):
    json_str = json.dumps(index_dict)
    with open(filename, 'w') as json_file:
        json_file.write(json_str)


if __name__ == '__main__':
    
    #读取数据文档, 800000条数据
    docs,label = read_file("带标签短信.txt")
    #通过匹配正则表达式，过滤掉文档中的url，数字，日期，电话号码
    for d in docs:
        d = regex_change(d)
    
    #读取停用词列表 
    stopwords = read_stopwords("停用词表.txt")
    
    #Jieba分词,创建倒排索引表
    index = OrderedDict()
    for i,doc in tqdm(enumerate(docs)):
        seg_list = jieba.cut_for_search(doc) #用搜索引擎模式分词
        #去除停用词、数字、标点符号
        words =  [word for word in seg_list if word not in stopwords]
        for w in words:
            if w not in index.keys():
                index[w] = list()
            index[w].append(i)
    #存储倒排索引表为json格式
    json_save(index,"倒排索引表.json")

        
        
