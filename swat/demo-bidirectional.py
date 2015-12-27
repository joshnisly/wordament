""" Note: This requires the following Apache directive:
        WSGIChunkedRequest On
"""
# pylint: disable=W9900

import httplib
import sys
import time

import sbi_path
from swat import wsgiserver
import swat

_HOST = '127.0.0.1'
_PORT = 8888
_DATA_LEN = 10
_NOOP = 'NOOP......'
assert len(_NOOP) == _DATA_LEN

def index(request):
    return swat.HttpResponse(comet(request), content_type='text/plain')

def comet(request):
    f = request.environ['wsgi.input']
    yield _NOOP #required to flush headers
    while True:
        yield '!' + f.read(_DATA_LEN)[1:]

def connect():
    conn = httplib.HTTPConnection(_HOST, _PORT)
    conn.request('POST', '/', headers={
        'Transfer-Encoding': 'chunked',
    })

    response = conn.getresponse()
    chunked_response = wsgiserver.ChunkedReader(response.fp)
    while True:
        for i in range(100):
            data = str(i).zfill(_DATA_LEN)
            conn.send('%s\r\n%s\r\n' % (hex(len(data))[2:], data))
            print '>>', data

            while True:
                response = chunked_response.read(_DATA_LEN)
                print '<<', response
                if response != _NOOP:
                    break

            time.sleep(1)
            print

URLS = (
    ('/', index),
)
application = swat.Application(URLS, send_500_emails=True, json_tracebacks=True)

def main():
    import threading
    t = threading.Thread(target=connect)
    
    if '--client-only' in sys.argv[1:]:
        t.start()
        t.join()
    else:
        t.daemon = True
        t.start()
        swat.run_standalone(
                    application, '%s:%s' % (_HOST, _PORT), should_reload=False)

if __name__ == '__main__':
    main()
