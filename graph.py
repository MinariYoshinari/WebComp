from collections import OrderedDict
from user import User

class Graph:
    def __init__(self, *users):
        self.users = [user for user in users if user.performances is not None]
        self.url = self.__generate_graph_url()

    def __generate_graph_url(self):
        max_ = max(user.max for user in self.users)
        min_ = min(user.min for user in self.users)
        upper_limit = (max_// 400 + 1) * 400
        lower_limit  = (min_ // 400  - 1) * 400
        colors = ("377BA8", "a74737")
        # 将来4色対応するとき用に
        #, "519c4c", "7f5593")

        merged_performances = self.__merge_performances()
        url = "http://chart.apis.google.com/chart?chs=400x300&chd=t:"
        max_date = max(merged_performances.keys())
        dates_url = ",".join([str(int(date_int/max_date * 100.0)) for date_int in merged_performances.keys()]) + "|"
        for i in range(len(self.users)):
            url += dates_url
            for contest in merged_performances.values():
                url += str(float(contest[i] - lower_limit)/float(upper_limit - lower_limit) * 100.0) + ","
            url = url[:-1] + "|"
        url = url[:-1]
        url += "&cht=lxy"
        url += "&chxt=x,y"
        url += "&chdl=" + "|".join([user.id for user in self.users])
        url += "&chco=" + ",".join([colors[i] for i in range(len(self.users))])
        # 将来4色対応するとき用
        # url += "&chco=" + ",".join([colors[i % len(colors)] for i in range(len(self.users))])
        # url += "&chf=bg,s,eeeeee|c,ls,90,99ffff,0.1,ffff99,0.1"
        
        return url

    def __merge_performances(self):
        dates = []
        for user in self.users:
            dates += list(user.performances.keys())
        dates.sort()
        min_date = min(dates)

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
            merged_performances[self.__timedelta_to_int(date-min_date)] = results
        import pprint; pprint.pprint(merged_performances)
        return merged_performances

    def __timedelta_to_int(self, timedelta):
        timedelta_str= str(timedelta)
        if 'day' in timedelta_str:
            return int(str(timedelta).split()[0])
        else:
            return 0
