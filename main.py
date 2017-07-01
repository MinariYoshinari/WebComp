import requests
from bs4 import BeautifulSoup
import datetime

request = requests.get('https://atcoder.jp/user/Noimin/history')
bs_obj = BeautifulSoup(request.text, 'html.parser')
table = bs_obj.find('table', id='history')
contests = table.findAll('tr')[1:]
performances = []
for contest in contests:
    values = contest.findAll('td')
    
    date_str = values[0].text
    date = datetime.datetime.strptime(date_str, '%Y/%m/%d %H:%M')

    performance_str = values[3].text
    if performance_str == '-':
        performances.append((date, None))
    else:
        performances.append((date, int(performance_str)))

print(performances)