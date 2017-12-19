from elasticsearch_dsl import DocType, Date, Nested, Boolean, analyzer, InnerObjectWrapper, Completion, Keyword, Text, Integer
from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class Article_4houType(DocType):
    suggest = Completion(analyzer=ik_analyzer)  #搜索建议
    image_local = Keyword()
    title = Text(analyzer="ik_max_word")
    url_id = Keyword()
    create_time = Date()
    url = Keyword()
    author = Keyword()
    tags = Text(analyzer="ik_max_word")
    watch_nums = Integer()
    comment_nums = Integer()
    praise_nums = Integer()
    content = Text(analyzer="ik_max_word")

    class Meta:
        index = "teachnical_4hou"
        doc_type = "A_4hou"

class Article_anquankeType(DocType):
    suggest = Completion(analyzer=ik_analyzer)  #搜索建议
    id = Integer()
    url = Keyword()
    title = Text(analyzer="ik_max_word")
    create_time = Date()
    cover_local = Keyword()
    watch_num = Integer()
    comment_num = Integer()
    tags = Text(analyzer="ik_max_word")
    author = Keyword()
    content = Text(analyzer="ik_max_word")

    class Meta:
        index = "article_anquanke"
        doc_type = "anquanke"