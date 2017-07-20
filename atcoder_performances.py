# all the imports
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

from user import User
from graph import Graph

# configuration
DEBUG = True
SECRET_KEY = 'development key'

# create our little application
app = Flask(__name__)
app.config.from_object(__name__)

def create_graph(username="", rivalname=""):
    input_ = username or rivalname
    me = User(username)
    rival = User(rivalname)
    if me.performances is None or (rival.performances is None and rival.id):
        graph = None
    else:
        graph = Graph(me, rival)
    return render_template('show_graph.html', input=input_, me=me, rival=rival, graph=graph)

@app.route('/')
def init_graph():
    return create_graph()

@app.route('/', methods=['POST'])
def show_graph():
    return create_graph(request.form['username'], request.form['rivalname'])

if __name__ == '__main__':
    app.run()