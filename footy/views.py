from collections import Counter
import datetime
import json

from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    session,
    url_for,
    request,
    Response,
    g
)

footy_http = Blueprint('footy_http', __name__)

def jsonify_doc(data, **kwargs):
    """Like flask jsonify except takes a document"""
    return Response(
        json.dumps(data),
        mimetype='application/json',
        **kwargs
    )

@footy_http.route('/')
def index():
    return jsonify_doc({'status': 'OK'})
