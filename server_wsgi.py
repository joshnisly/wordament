#!/usr/bin/python

import flask
import json
import sys

import search


app = flask.Flask(__name__)


@app.route('/')
def index(initial=''):
    return flask.render_template('index.html', **{
        'grid_size': search.GRID_SIZE,
        'initial_grid': initial
    })


@app.route('/solve/', methods=['POST'])
def solve():
    grid = search.load_from_string(flask.request.form['board'])
    results = search.find_words(grid, WORD_LIST)
    results.sort(key=lambda x: len(x['word']), reverse=True)
    return json.dumps(results)


URLS = (
    ('/?initial=<s>', index),
    ('/solve/', solve),
)

WORD_LIST = None

if __name__ == '__main__':
    WORD_LIST = sorted(search.load_list_from_file(sys.argv[1]))
    app.run(host='localhost', port=8081, debug=True)
