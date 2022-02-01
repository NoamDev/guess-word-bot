import os
import re
from flask import Flask, request, Response

import encryption_util

app = Flask(__name__)

word_regex = re.compile(r'^[a-z]+$')

@app.route('/prepare/<lang>/<word>', methods=['GET'])
def prepare(lang, word):
    if not word_regex.match(word):
        return Response('Bad Request', status=400)
    response = Response(encryption_util.encrypt(word, lang))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=int(os.environ['ENCRYPTION_SERVER_PORT']))
