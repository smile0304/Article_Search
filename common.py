from moudels import Article_4houType,Article_anquankeType

class elasticsearch_fuzz_search(object):
    def __init__(self,type):
        self.s = type.search()

    def return_fuzzing_search(self,key_words):
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

class elasticsearch_fuzz_allsearch(elasticsearch_fuzz_search):
    def __init__(self):
        self.s_a4hou = Article_4houType.search()
        self.s_anquanke = Article_anquankeType.search()

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
            s_anquanke = self.s_anquanke.suggest("my_suggest", key_words, completion={
                "field": "suggest",
                "fuzzy": {
                    "fuzziness": 2
                },
                "size": 5
            })
            suggestions_4hou = s_4hou.execute_suggest()
            suggestions_anquanke = s_anquanke.execute_suggest()

            for match_4hou,match_anquanke in zip(suggestions_4hou.my_suggest[0].options,suggestions_anquanke.my_suggest[0].options):
                source_4hou = match_4hou._source
                source_anquanke = match_anquanke._source
                re_dates.append(source_4hou["title"])
                re_dates.append(source_anquanke["title"])

        return re_dates


