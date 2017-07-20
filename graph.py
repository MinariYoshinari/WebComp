from collections import OrderedDict
import requests
import datetime
from user import User

class Graph:
    def __init__(self, *users):
        self.users = [user for user in users if user.performances is not None]
        self.dates = {}
        self.url = self.__generate_graph_url()

    def __generate_graph_url(self):
        
        def datetime_to_label(dt):
            return "{}-{}-{}".format(dt.year, dt.month, dt.day)

        max_ = (max(user.max for user in self.users) + 500) // 500 * 500
        min_ = min(user.min for user in self.users)
        upper_limit = (max_// 400 + 1) * 400
        lower_limit  = (min_ // 400  - 1) * 400
        colors = ("990000", "000099")
        # 将来4色対応するとき用に
        #, "519c4c", "7f5593")

        merged_performances = self.__merge_performances()
        min_date = min(merged_performances.keys())
        max_date = max(merged_performances.keys())
        stripe = 400 / max_
        print(max_)

        BASE_URL = "http://chart.apis.google.com/chart"
        params = {
            "chs": "400x300",   # グラフのサイズ
            "chd": "t:",    # データの中身
            "cht": "lxy",
            "chxt": "x,y",
            "chxr": "1,0,{}".format(max_), # 軸の値の範囲
            "chxl": "0:|{}|{}".format(datetime_to_label(self.dates[min_date]), datetime_to_label(self.dates[max_date])),
            "chds": "a",    # 目盛の自動調整
            "chdl": "|".join([user.id for user in self.users]),
            "chco": ",".join([colors[i] for i in range(len(self.users))]),
            "chf": "c,ls,90,bfbfbf,{0},d2b48c,{0},99ff99,{0},99ffff,{0},9999ff,{0},ffff99,{0},ffcc99,{0},ff9999,{1}".format(stripe, max(0, 1.0-stripe*7.0)) # 背景色
            }
        dates_url = ",".join([str(date_int) for date_int in merged_performances.keys()]) + "|"
        for i in range(len(self.users)):
            params["chd"] += dates_url
            for contest in merged_performances.values():
                params["chd"] += str(contest[i]/max_*100 if contest[i] != -1 else -1) + ","
            params["chd"] = params["chd"][:-1] + "|"
        params["chd"] = params["chd"][:-1]

        r = requests.get(BASE_URL, params=params)
        return r.url

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
            date_int = self.__timedelta_to_int(date-min_date)
            merged_performances[date_int] = results
            self.dates[date_int] = date;
        return merged_performances

    def __timedelta_to_int(self, timedelta):
        timedelta_str= str(timedelta)
        if 'day' in timedelta_str:
            return int(str(timedelta).split()[0])
        else:
            return 0
