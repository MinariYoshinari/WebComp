from collections import OrderedDict
from itertools import islice
import os
import requests
import datetime
import time
import json
# import base64
from requests_oauthlib import OAuth1Session
from user import User

class Graph:
    def __init__(self, *users):
        self.users = [user for user in users if user.performances is not None]
        self.dates = {}
        self.response = None
        self.id = None
        self.url = self.__generate_url()

    def __generate_url(self):
        
        def datetime_to_label(dt):
            return "{}-{}-{}".format(dt.year, dt.month, dt.day)

        colors = ("990000", "000099")
        # 将来4色対応するとき用に
        #, "519c4c", "7f5593")

        merged_performances = self.__merge_performances()
        participation_count = len(merged_performances)
        if participation_count > 20:
            merged_performances = islice(
                merged_performances.items(), 
                participation_count-20, 
                None
                )
            merged_performances = OrderedDict(merged_performances)

        max_ = (max(user.max for user in self.users) + 500) // 500 * 500
        # min_ = (min(user.min for user in self.users) - 500) // 500 * 500
        min_date = min(merged_performances.keys())
        max_date = max(merged_performances.keys())
        stripe = 400 / max_
        BASE_URL = "http://chart.apis.google.com/chart"
        params = {
            "chs": "600x400",   # グラフのサイズ
            "chd": "t:",    # データの中身
            "cht": "lxy",
            "chxt": "x,y",
            "chxr": "0,{},{}|1,0,{}".format(min_date, max_date, max_), # 軸の値の範囲
            "chxl": "0:|{}|{}".format(datetime_to_label(self.dates[min_date]), datetime_to_label(self.dates[max_date])),
            "chxs": "0,666666,16|1,666666,16", # 軸のスタイル
            # "chds": "a",    # 目盛の自動調整
            "chdl": "|".join([user.id for user in self.users]),
            "chco": ",".join([colors[i] for i in range(len(self.users))]),
            "chf": "c,ls,90,bfbfbf,{0},d2b48c,{0},99ff99,{0},99ffff,{0},9999ff,{0},ffff99,{0},ffcc99,{0},ff9999,{1}".format(stripe, max(0, 1.0-stripe*7.0)) # 背景色
            }
        range_date = max_date-min_date
        dates_url = ",".join([str((date_int-min_date)/range_date*100.0) for date_int in merged_performances.keys()]) + "|"
        for i in range(len(self.users)):
            params["chd"] += dates_url
            for contest in merged_performances.values():
                params["chd"] += str(contest[i]/max_*100.0 if contest[i] != -1 else -1) + ","
            params["chd"] = params["chd"][:-1] + "|"
        params["chd"] = params["chd"][:-1]
        self.response = requests.post(BASE_URL, params=params)
        return self.response.url

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

    def tweet_img(self):
        CK = "xsLYwLySAkrxUkCupclsvdpQg"
        CS = "rYpyADgCK16kN86vJ8ya4tyn9s86UeKj2JXgMU1okl3ShfWzYB"
        AT = "2791735616-lJWzdz1RicKTuVck4IMy4Ihf3Ecd7jhXG99Dfj6"
        AS = "PxlmGhmVgsIbzQ8gdgISBF0K510YHgq0glkGN9KPWsV07"
        UPDATE_URL = "https://api.twitter.com/1.1/statuses/update.json"
        twitter = OAuth1Session(CK, CS, AT, AS)

        img_path = self.__save_img(self.response.content)
        self.__upload_img(twitter, img_path)
        status = "{}のパフォーマンスのグラフ {}".format(
            "と".join([user.id+"さん" for user in self.users]),
            "https://atcoder-performances.herokuapp.com/show_graph?username={}&rivalname={}".format(self.users[0].id, "" if len(self.users) == 1 else self.users[1].id)
            )
        params = {'status': status, "media_ids": [self.id]}
        tweet_response = twitter.post(UPDATE_URL, params = params)

    def __save_img(self, img):
        filename = str(int(time.time()* 10**5)) + '.png'
        fullpath = os.path.join('img', filename)

        with open(fullpath, 'wb') as f:
            f.write(img)
        
        return fullpath

    def __upload_img(self, twitter, img_path):
        UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"

        f = open(img_path, 'rb')
        files = {"media": f}
        upload_response = twitter.post(UPLOAD_URL, files=files)
        f.close()
        # uploadに失敗したらMedia idはNone
        if upload_response.status_code != 200:
            return

        self.id = json.loads(upload_response.text)['media_id_string']
        os.remove(img_path)
