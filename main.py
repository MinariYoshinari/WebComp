import pprint
from user import User
from graph import Graph

me = User("Noimin")
rival = User("tourist")
pprint.pprint(rival.performances)
graph = Graph(me, rival)
print(graph.url)