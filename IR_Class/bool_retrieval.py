# -*- coding: utf-8 -*-
"""
@author: yaolinli
"""
import re
import argparse
from tqdm import tqdm
import os
import json
from index import read_stopwords,read_file

def load_json(filename):
    with open(filename) as f:
        index = json.load(f)
    return index

def process_query(query):
    #去除query中的停用词和不在dictionary中的单词
    stopwords = read_stopwords("停用词表.txt")
    dictionary = index.keys()
    query_words = [word for word in query.split() if word not in stopwords and word in dictionary]
    return query_words

def intersect(doc_list1,doc_list2):
    doc_list1 = set(doc_list1)
    doc_list2 = set(doc_list2)
    answer = list(doc_list1 & doc_list2)
    return answer

def cmp(x,y):
    if len(index[x])<len(index[y]):
        return -1
    if len(index[x])==len(index[y]):
        return 0
    else:
        return 1
    
def cmp_flag(x):
    return len(index[x])
    
def bool_retrieval(query):
    #将term按照出现在文档中的频率从小到大排序
    terms = query
    if len(query) > 1:
        terms = sorted(query,key = cmp_flag)
    answer = index[terms[0]]
    for i in range(1,len(terms)):
        answer = intersect(answer,index[terms[i]])
    num = len(answer)    
    return answer,num


    
if __name__ == '__main__':
    #读取所有文档集合
    docs,label = read_file("带标签短信.txt")
    #读取已经构建好的倒排索引
    global index
    index = load_json("倒排索引表.json")
    
    # 获得输入的query
    parser = argparse.ArgumentParser(description='Boolean query')
    parser.add_argument('query', help='words seperated by space')
    args = parser.parse_args()

    # 预处理输入的query
    
    query = args.query
    query = process_query(query)
    #print("processed query",query)
    #布尔查询
    result,num = bool_retrieval(query)
    
    #输出结果
    print("共检索到{}个相关文档".format(num))
    for i in result:
        print("-文档{}------------------------------------------------------------------------------\n".format(i+1),docs[i])