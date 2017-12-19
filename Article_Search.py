from flask import Flask,render_template,request
from config import client
from moudels import Article_4houType,Article_anquankeType
from common import elasticsearch_fuzz_search,elasticsearch_fuzz_allsearch
import json
from datetime import datetime
app = Flask(__name__)


@app.route('/')
def search_index():
    return render_template("index.html")

@app.route('/suggest/')
def suggest():
    key_words = request.args.get('s','')
    type = request.args.get('s_type','')
    if "A4hou" == type:
        fuzzing = elasticsearch_fuzz_search(type=Article_4houType)
        re_dates = fuzzing.return_fuzzing_search(key_words=key_words)
    elif "anquanke" == type:
        fuzzing = elasticsearch_fuzz_search(type=Article_anquankeType)
        re_dates = fuzzing.return_fuzzing_search(key_words=key_words)
    else:
        fuzzing = elasticsearch_fuzz_allsearch()
        re_dates = fuzzing.return_fuzzing_search(key_words=key_words)
    return json.dumps(re_dates)

@app.route('/search/')
def search():
    #文章来源
    all_options = [["all","全部"],["A4hou","嘶吼"],["anquanke","安全客"]] #不明白为什么用字典会乱序
    key_words = request.args.get('q','')
    types = request.args.get('s_type','')
    page = request.args.get('p','1')
    try:
        page = int(page)
    except:
        page = 1


    # return render_template("result.html",
    #                        page=page,
    #                        all_hits=hit_list,
    #                        key_words=key_words,
    #                        total_nums=total_nums,
    #                        page_nums=page_nums,
    #                        last_seconds=last_seconds,
    #                        key_word = key_words,
    #                        type = types,
    #                        all_options = all_options
    #                        )

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True,port=8080)
