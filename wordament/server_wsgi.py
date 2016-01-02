#!/usr/bin/python

import sys

import swat

import search


def index(request, initial=''):
    return swat.template_response(request, 'index.html', {
        'grid_size': search.GRID_SIZE,
        'initial_grid': initial
    })


@swat.json_request
def solve(request):
    grid = search.load_from_string(request.JSON['board'])
    results = search.find_words(grid, WORD_LIST)
    results.sort(key=lambda x: len(x[0]), reverse=True)
    return results


URLS = (
    ('/?initial=<s>', index),
    ('/solve/', solve),
)

WORD_LIST = None

application = swat.Application(URLS, send_500_emails=False)

if __name__ == '__main__':
    WORD_LIST = sorted(search.load_list_from_file(sys.argv[1]))
    swat.run_standalone(application, 'localhost:8081', should_reload=True)
