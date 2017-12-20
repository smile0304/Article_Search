from moudels import Article_4houType,Article_anquankeType
from config import client
from datetime import datetime
import re

class elasticsearch_search(object):
    def __init__(self,type):
        self.s = type.search()
        if Article_anquankeType == type:
            self.index = "article_anquanke"
        elif Article_4houType == type:
            self.index = "teachnical_4hou"

    def return_fuzzing_search(self,key_words):
        """
        模糊查询,分词匹配
        :param key_words:
        :return:re_dates
        """
        re_dates = []
        if key_words:
            s = self.s.suggest("my_suggest", key_words, completion={
                "field": "suggest",
                "fuzzy": {
                    "fuzziness": 2
                },
                "size": 10
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_dates.append(source["title"])
        return re_dates

    def get_date(self,key_words,page):
        """
        从elasticsearch中获取数据
        :param key_words:
        :param page:
        :return: response
        :return : last_seconds
        """
        start_time = datetime.now()
        response = client.search(
            index = self.index,
            body = {
                "query":{
                    "multi_match":{
                        "query":key_words,
                        "fields":["tags","title","content"]
                    }
                },
                "from":(page-1)*10,
                "size":10,
                "highlight":{
                    "pre_tags":['<span class="keyWord">'],
                    "post_tags":['</span>'],
                    "fields":{
                        "title":{},
                        "content":{},
                    }
                }
            }
        )
        end_time = datetime.now()
        last_seconds = (end_time - start_time).total_seconds()
        return response,last_seconds

    def analyze_date(self,key_words,response):
        """
        返回分析后的数据列表集合
        :return:hit_list
        """
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            hit_dict["origin"] = self.get_origin(hit)
            if "highlight" in hit:
                if "title" in hit["highlight"]:
                    hit_dict["title"] = "".join(hit["highlight"]["title"])
                else:
                    hit_dict["title"] = hit["_source"]["title"]
                if "content" in hit["highlight"]:
                    hit_dict["content"] = self.filter_tags("".join(hit["highlight"]["content"])[:500])
                else:
                    hit_dict["content"] = self.filter_tags(hit["_source"]["content"][:500])
            else:
                hit_dict["title"] = hit["_source"]["title"]
                hit_dict["content"] = self.filter_tags(hit["_source"]["content"][:500])
            hit_dict["create_date"] = hit["_source"]["create_time"]
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = hit["_score"]
            replace_text = '<span class="keyWord">' + key_words + "</span>"
            words = "(?i)"+key_words
            hit_dict["content"] = re.sub(words,replace_text,hit_dict["content"])

            hit_list.append(hit_dict)
        return hit_list

    def get_origin(self,hit):
        """
        获取文章来源
        :return:index_name 来源名称
        """
        if "_index" in hit:
            if "teachnical_4hou" == hit["_index"]:
                origin = "嘶吼"
            elif "article_anquanke" == hit["_index"]:
                origin = "安全客"
        else:
            origin = "未知来源"
        return origin
    def filter_tags(self,htmlstr):
        """
        过滤HTML中的标签
        将HTML中标签等信息去掉
        :param htmlstr: HTML字符串
        :return:
        """
        # 先过滤CDATA
        re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
        re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
        re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
        re_br = re.compile('<br\s*?/?>')  # 处理换行
        re_h = re.compile('</?\w+[^>]*>')  # HTML标签
        re_comment = re.compile('<!--[^>]*-->')  # HTML注释
        re_stopwords = re.compile('\u3000')  # 去除无用的'\u3000'字符
        s = re_cdata.sub('', htmlstr)  # 去掉CDATA
        s = re_script.sub('', s)  # 去掉SCRIPT
        s = re_style.sub('', s)  # 去掉style
        s = re_br.sub('\n', s)  # 将br转换为换行
        s = re_h.sub('', s)  # 去掉HTML 标签
        s = re_comment.sub('', s)  # 去掉HTML注释
        s = re_stopwords.sub('', s)
        # 去掉多余的空行
        blank_line = re.compile('\n+')
        s = blank_line.sub('\n', s)
        s = self.replaceCharEntity(s)  # 替换实体
        return s

    def replaceCharEntity(self,htmlstr):
        """
        #替换常用HTML字符实体.
        使用正常的字符替换HTML中特殊的字符实体.
        你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
        :param htmlstr: HTML字符串
        :return: 这个return不重要
        """
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                         'lt': '<', '60': '<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"', '34': '"', }

        re_charEntity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_charEntity.search(htmlstr)
        while sz:
            entity = sz.group()  # entity全称，如&gt;
            key = sz.group('name')  # 去除&;后entity,如&gt;为gt
            try:
                htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
            except KeyError:
                # 以空串代替
                htmlstr = re_charEntity.sub('', htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
        return htmlstr

class elasticsearch_allsearch(elasticsearch_search):
    def __init__(self):
        self.s_a4hou = Article_4houType.search()
        self.s_anquanke = Article_anquankeType.search()
        self.all_hits = []

    def return_fuzzing_search(self,key_words):
        re_dates = []
        if key_words:
            s_4hou = self.s_a4hou.suggest("my_suggest", key_words, completion={
                "field": "suggest",
                "fuzzy": {
                    "fuzziness": 2
                },
                "size": 5
            })
            suggestions_4hou = s_4hou.execute_suggest()

            for match_4hou in suggestions_4hou.my_suggest[0].options:
                source_4hou = match_4hou._source
                re_dates.append(source_4hou["title"])
            s_anquanke = self.s_anquanke.suggest("my_suggest", key_words, completion={
                "field": "suggest",
                "fuzzy": {
                    "fuzziness": 2
                },
                "size": 10-len(re_dates)
            })

            suggestions_anquanke = s_anquanke.execute_suggest()

            for match_anquanke in suggestions_anquanke.my_suggest[0].options:
                source_anquanke = match_anquanke._source
                re_dates.append(source_anquanke["title"])

        return re_dates



    def return_datenum(self,key_words,page=1):
        #获取数据条数
        self.index = "teachnical_4hou"
        response_4hou ,times = self.get_date(key_words,init=0,size=1)
        self.index = "article_anquanke"
        response_anquanke,times = self.get_date(key_words,init=0,size=1)
        total_nums_4hou = response_4hou["hits"]["total"]
        total_nums_anquanke = response_anquanke["hits"]["total"]
        zipmin= min(total_nums_4hou,total_nums_anquanke)
        #获取数据个数处理
        response_and_time_list = self.get_zipdate(zipmin,total_nums_4hou,total_nums_anquanke,key_words,page,size=5)
        #对获取到的数据进行处理
        for response in response_and_time_list[:-1]:
            datalist = super().analyze_date(key_words,response)
            self.all_hits = self.all_hits + datalist
        last_seconds = response_and_time_list[-1]
        return self.all_hits,last_seconds,total_nums_4hou+total_nums_anquanke
    def get_zipdate(self,zipmin,nums_4hou,nums_anquanke,key_words,page,size):
        """
        :return:
        """
        init = (page - 1) * 5
        if init <= zipmin:
            self.index = "teachnical_4hou"
            response_4hou,time_4hou = self.get_date(key_words, init, size)
            self.index = "article_anquanke"
            response_anquanke,time_anquanke = self.get_date(key_words, init, size)
        else :
            if init >= nums_4hou:
                self.index = "article_anquanke"
                #init要变
                init = int(init/2) + (page - 1) * 5
                size = 10
                response_anquanke,time_anquanke = self.get_date(key_words,init,size)
                return response_anquanke,time_anquanke
            elif init >= nums_anquanke:
                self.index = "article_anquanke"
                init = int(init / 2) + (page - 1) * 5
                size = 10
                response_4hou,time_4hou = self.get_date(key_words,init,size)
                return response_4hou,time_4hou
        last_seconds = time_4hou + time_anquanke
        return [response_anquanke,response_4hou,last_seconds]





    def get_date(self,key_words,init,size):
        """
        从elasticsearch中获取数据
        :param key_words:
        :param page:
        :return: response
        :return : last_seconds
        """
        start_time = datetime.now()
        response = client.search(
            index = self.index,
            body = {
                "query":{
                    "multi_match":{
                        "query":key_words,
                        "fields":["tags","title","content"]
                    }
                },
                "from":init,
                "size":size,
                "highlight":{
                    "pre_tags":['<span class="keyWord">'],
                    "post_tags":['</span>'],
                    "fields":{
                        "title":{},
                        "content":{},
                    }
                }
            }
        )
        end_time = datetime.now()
        last_seconds = (end_time - start_time).total_seconds()
        return response,last_seconds

