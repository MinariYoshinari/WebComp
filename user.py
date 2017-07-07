import requests
from bs4 import BeautifulSoup
import datetime
from collections import OrderedDict

class User:
    def __init__(self, id):
        self.id = id
        self.performances = self.__get_performances(id)
        if self.performances is None:
            self.message = 'The user name "{}" is wrong.'.format(id)
            return
        else:
            self.message = ""
            self.max = self.__get_max(self.performances)
            self.min = self.__get_min(self.performances)
    
    def __get_performances(self, id):
        request = requests.get('https://atcoder.jp/user/{}/history'.format(id))
        bs_obj = BeautifulSoup(request.text, 'html.parser')
        table = bs_obj.find('table', id='history')

        # 存在しないユーザだった場合
        if table is None:
            return None

        contests = table.findAll('tr')[1:]
        performances = OrderedDict()
        max_performance = 0
        for contest in contests:
            values = contest.findAll('td')
            
            date_str = values[0].text
            date = datetime.datetime.strptime(date_str, '%Y/%m/%d %H:%M')

            performance_str = values[3].text
            if performance_str != '-':
                performance = int(performance_str)
                performances[date] = performance
        return performances

    def __get_max(self, performances):
        return max(performance for performance in performances.values())

    def __get_min(self, performances):
        return min(performance for performance in performances.values())