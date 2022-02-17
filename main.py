import math
import random

from flask import Flask,request,render_template,jsonify
from AutoComple import AutoComplete
from get_search_result import *
from AutoCorrecterr4Chinese import AutoCorrecter
from word_seg import Word_Segment
import Levenshtein
app = Flask(__name__)

@app.route('/')
def hellopage():
    # return  'index.html'
    return render_template('index.html')


@app.route('/qa' ,methods=['POST'])
def querycomplete():
    data = request.form
    query=data['word']

    words=ac.normal_complete(query)
    words+=ac.comprehensive_complete(query)
    # words=random.shuffle(words)[:10]
    print(words)
    # words=['as','him','tr']
    return jsonify({"success": 200, "words":words})

@app.route('/search/p',methods=['GET', 'POST'])
def search():

    if request.method == 'POST':
        data = request.form
    else:
        data = request.args

    pageId=1
    if data.get('page') is not None:
        pageId=int(data.get('page'))

    need_correct=False
    is_correct=True
    correct_phrase=""
    if data.get('cor') is None:
        need_correct=True

    query=data.get('q')
    original_query=query
    if need_correct:
        is_correct,correct_phrase=query_correct(query)
        if is_correct==False:
            query=correct_phrase

    results = get_result(query,index)
    result_list=[]
    page_list=[]

    news_per_page=10

    lower=(pageId-1)*news_per_page
    upper=min(pageId*news_per_page,len(results))
    for i in range(lower,upper):
        result={}
        result['title']=results[i]["title"]
        result['abstract']=results[i]["abs"][2:]
        result['href']='/news?id='+results[i]["id"][:-4]
        result_list.append(result)

    start=max(pageId-5,1)
    pages=10
    total_page=math.ceil(len(results)/news_per_page)
    for i in range(start,min(start+pages,total_page)):
        page_info={}
        page_info['id']=i
        page_info['href']='/search/p?q='+query+'&page='+str(start+i)
        page_list.append(page_info)

    parameter_dict={}
    parameter_dict['page']=1
    parameter_dict['result_list']=result_list
    parameter_dict['correct']=is_correct
    parameter_dict['correct_phrase']= correct_phrase
    parameter_dict['query']=original_query
    parameter_dict['page_list']=page_list

    return render_template('search.html',**parameter_dict)


@app.route('/news',methods=['GET'])
def show_news_content():

    data = request.args
    id=data.get("id")
    file_path='../dataset/'+id+'.txt'
    with open(file_path,'r',encoding="UTF-8") as f:
        content=f.read()
    paras=re.split(r"\n",content)
    para_dict={}
    para_dict["content"]=paras
    return render_template('shownews.html',**para_dict)

def query_correct(query):

    correct_phrase=autocorrecter.auto_correct_sentence(query, True)
    print('here')
    print(correct_phrase)

    is_correct=False
    if Levenshtein.ratio(query,correct_phrase)>0.8:
        is_correct=True
    # return True,correct_phrase
    return is_correct,correct_phrase






if __name__ == "__main__":

    global ac
    ac= AutoComplete('./resources/word_freq.json', './model/word2vec.model.bin')
    global index
    index = whoosh_text("index", "../sample_THUCNews/")

    index.create_searcher()
    global autocorrecter
    autocorrecter = AutoCorrecter(Word_Segment('./resources/stopwords.txt'))

    app.run(host='localhost', port=8888)