import sys
import os
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh.qparser import MultifieldParser
from jieba.analyse.analyzer import ChineseAnalyzer
import datetime
import random
import shutil
class whoosh_text():
    def __init__(self, index_path, file_path):
        self.schema = Schema(type=TEXT(stored=True), title=TEXT(stored=True), id=TEXT(stored=True), text=TEXT(stored=True, analyzer=ChineseAnalyzer()))
        self.index_path = index_path
        # 创建索引
        # 创建索引存储目录
        if not os.path.exists(index_path):
            os.mkdir(index_path)

        # self.deal_file(index_path)
        # 创建新索引
        self.ix = create_in("index", self.schema, 'my_index')
        # content = get_dbtext(db)
        # 新建writer
        writer = self.ix.writer()
        # 遍历数据库, 插入doc
        count = 0
        res = self.read_file(file_path)
        for blog in res:
            type = blog["type"]
            title = blog["title"]
            content = blog["content"]
            id = blog["id"]
            writer.add_document(type=u'%s' % type, title=u'%s' % title, id=u'%s' % id, text=u'%s' % content)
            count += 1
            # print('第', count, '篇blog添加成功...')
        writer.commit()
        # print("aaa")

    def create_searcher(self):
        # 建立搜索对象
        # ixr = open_dir("./"+self.index_path + "/my_indexing.tmp")
        ixr = self.ix
        # with ixr.searcher(weighting=scoring.BM25F()) as searcher:
        self.searcher = ixr.searcher(weighting=scoring.BM25F()) # 没有close，可能会内存泄露，记得关服务器。
        # 建立解析器(使用多字段查询解析器)
        self.parser = MultifieldParser(['title', 'text'], schema=self.schema)

    def deal_file(self, path):

        res = os.listdir(path)
        for temp in res:
            shutil.rmtree("./" + path + "/" + temp)
            # for temp_temp in temp:
            os.remove("./" + path + "/" + temp)

    # 按照索引查询
    def search_document(self, query, limit_=10000):
        searcher = self.searcher
        parser = self.parser
        q = parser.parse(query)
        results = searcher.search(q, limit=limit_)
        return results

    def read_file(self, file_path):
        res = []
        dirpath, dirs, files = list(os.walk(file_path))[0]
        # select_dir = random.sample(dirs, number)
        select_dir = dirs
        print(select_dir)
        for each_dir in select_dir:
            each_dir_path = file_path + each_dir + "/"
            temp_dirpath, temp_dirs, temp_files = list(os.walk(each_dir_path))[0]
            # select_file = random.sample(temp_files, sample_number)
            select_file = temp_files
            for each_file in select_file:
                each_file_path = each_dir_path + each_file
                with open(each_file_path, "r", encoding="utf-8") as f:
                    content_dict = {}
                    title_flag = False
                    for line in f:
                        if not title_flag:
                            content_dict["type"] = each_dir
                            content_dict["title"] = line.strip()
                            content_dict["content"] = []
                            content_dict["id"] = each_file
                            title_flag = True
                        else:
                            content_dict["content"].append(line.strip() + "\n")
                    content_dict["content"] = "".join(content_dict["content"])
                    res.append(content_dict)
        return res

def get_abs(query, text, length):
    index = text.find(query)
    start = 0
    end = len(text)
    if index - length >= 0:
        start = index - length
    if index + length <= len(text):
        end = index + length
    return text[start:end]

def get_result(query,index):

    length = 50

    results = index.search_document(query)
    res = []

    if results is not None:
        for i in range(len(results)):
            content = {}
            content["title"] = results[i]["title"]
            content["score"] = results[i].score
            content["text"] = results[i]['text']
            content["id"] = results[i]["id"]
            content["abs"] = get_abs(query, content["text"], length)
            res.append(content)
    else:
        print('未查询到结果')

    return res



# if __name__ == "__main__":
#     # index = whoosh_text("index", "../THUCNews/", 5, 10)
#     index = whoosh_text("index", "../sample_THUCNews/")
#     index.create_searcher()
#     length = 50
#     while(1):
#         i = 1
#         print('Please input the query:')
#         query = input()
#         time1 = datetime.datetime.now()
#         results = index.search_document(query)
#         time2 = datetime.datetime.now()
#         res = []
#
#         if results is not None:
#             for i in range(len(results)):
#                 content = {}
#                 content["tpye"] = results[i]['type']
#                 content["title"] = results[i]["title"]
#                 content["score"] = results[i].score
#                 content["text"] = results[i]['text']
#                 content["id"] = results[i]["id"]
#                 content["abs"] = get_abs(query, content["text"], length)
#                 res.append(content)
#                 print()
#             else:
#                 print('未查询到结果')
#         print("aaa")
#         print(time2-time1)
