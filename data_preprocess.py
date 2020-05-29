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
from sklearn.model_selection import train_test_split
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
    f = open(filename,"r",encoding='utf-8')
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
    special = re.compile("[a-zA-Z0-9’!\"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》（）？“”‘’！[\\]^_`{|}~]+")
    
    line = special.sub(r"",line)
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

def save_data(path,data,label):
    with open(path,'w',encoding='utf-8') as f:
        for i in range(len(data)):
            sentence = ''
            for j,d in enumerate(data[i]):
                if j != 0:
                    sentence += ' '
                sentence += d
            f.writelines(sentence+'\t'+str(label[i])+'\n')
    
    
if __name__ == '__main__':
    
    #读取数据文档, 800000条数据
    docs,str_label = read_file("data.txt")
    label = [int(l) for l in str_label]
    spam_num = len([i for i in label if i == 1])
    normal_num = len([i for i in label if i == 0])
    print("垃圾短信数量",spam_num)
    print("正常短信数量",normal_num)
    #通过匹配正则表达式，过滤掉文档中的url，数字，日期，电话号码
    for d in docs:
        d = regex_change(d)
    
    #读取停用词列表 
    stopwords = read_stopwords("stop_words.txt")
    stopwords.append(' ')
    stopwords.append('\ue310')
    stopwords.append('\ue006')
    stopwords.append('\ue319')
    stopwords.append('\ue415')
    print("stop words num:",len(stopwords))
    
    #对每个句子进行分词+清洗预处理
    data = []
    vocab = []
    for i,doc in tqdm(enumerate(docs)):
        if i > 50:
            break
        seg_list = jieba.lcut(doc) #用精确模式分词
        #去除停用词、数字、标点符号
        words =  [word for word in seg_list if word not in stopwords]
        data.append(words)
        vocab.extend(words)
    vocab = set(vocab)
    print("词典大小：",len(vocab))
    
    
    #划分数据集 train:valid:test
    split = ['train','test','dev']
    x = {}
    y = {}
    x_train,x_test, y_train, y_test = train_test_split(data,label[0:len(data)],test_size=2/80, random_state=0)
    x['train'] = x_train
    y['train'] = y_train
    x['dev'], x['test'], y['dev'], y['test'] = train_test_split(x_test,y_test,test_size=0.5, random_state=0)
    
    for s in split:
        print(s, len(x[s]))
        spam_num = len([i for i in y[s] if i == 1])
        normal_num = len([i for i in y[s] if i == 0])
        print("垃圾短信数量",spam_num)
        print("正常短信数量",normal_num)
        split_path = s+'.txt'
        save_data(split_path,x[s],y[s])
    
    save_data("messages.txt",data,label)
    
    

        
        
