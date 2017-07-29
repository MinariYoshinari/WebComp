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

def create_graph(username="", rivalname="", tweet=False):
    input_ = username or rivalname
    me = User(username)
    rival = User(rivalname)
    if me.performances is None or (rival.performances is None and rival.id):
        graph = None
    else:
        graph = Graph(me, rival)
    if tweet:
        graph.tweet_img()
    return render_template('show_graph.html', input=input_, me=me, rival=rival, graph=graph)

@app.route('/')
def init_graph():
    return create_graph()

@app.route('/show_graph', methods=['GET'])
def show_graph():
    #return create_graph(request.form['username'], request.form['rivalname'])
    return create_graph(request.args.get('username'), request.args.get('rivalname'))

@app.route('/tweet_img', methods=['POST', 'GET'])
def tweet_img():
    return create_graph(request.args.get('username'), request.args.get('rivalname'), tweet=True)

if __name__ == '__main__':
    app.run()