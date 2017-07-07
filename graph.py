from collections import OrderedDict
from user import User

class Graph:
    def __init__(self, *users):
        self.users = users
        self.url = self.__generate_graph_url()

    def __generate_graph_url(self):
        max_ = max(user.max for user in self.users)
        min_ = min(user.min for user in self.users)
        upper_limit = (max_// 400 + 1) * 400
        lower_limit  = (min_ // 400  - 1) * 400

        merged_performances = self.__merge_performances()
        url = "http://chart.apis.google.com/chart?chs=300x300&chd=t:"
        for i in range(len(self.users)):
            for contest in merged_performances.values():
                url += str(float(contest[i] - lower_limit)/float(upper_limit - lower_limit) * 100.0) + ","
            url = url[:-1] + "|"
        url = url[:-1]
        url += "&cht=lc"
        return url

    def __merge_performances(self):
        dates = []
        for user in self.users:
            dates += list(user.performances.keys())
        dates.sort()

        merged_performances = OrderedDict()
        lasts = [-1 for _ in range(len(self.users))]
        for date in dates:
            results = []
            for i, user in enumerate(self.users):
                if date in user.performances:
                    results.append(user.performances[date])
                    lasts[i] = user.performances[date]
                else:
                    results.append(lasts[i])
            merged_performances[date] = results
    
        return merged_performances