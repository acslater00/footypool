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

from footy import db
from footy.tables import Entrant
from footy import analysis
from footy import score

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
    return render_template('index.html')


@footy_http.route('/_status')
def status():
    return jsonify_doc({'status': 'OK'})

GROUPED_SELECTIONS = {
    'A' : range(1,9),
    'B' : range(9,17),
    'C' : range(17,25),
    'D' : range(25,33),
    'E' : range(33,41),
    'F' : range(41,49),
    'G' : range(49,57),
    'H' : range(57,65),
}
def selection_id_to_group(selection_id):
    for g,v in GROUPED_SELECTIONS.items():
        if selection_id in v:
            return g
    return None

def outcome_value(selected, actual):
    if actual is None:
        return 0
    elif selected.lower() == actual.lower():
        return 1
    else:
        return -1


@footy_http.route('/picks/<int:entrant_id>')
def picks(entrant_id):
    entrant = db.session.query(Entrant).get(entrant_id)
    data = {
        'entrant_name' : entrant.name,
        'entrant_email' : entrant.email
    }

    es = entrant.entrant_selections
    es_by_selection_id = {es.selection_id : es for es in entrant.entrant_selections}

    group_picks = {}
    for group, selection_ids in GROUPED_SELECTIONS.items():
        pick_datas = []
        for sid in selection_ids:
            es = es_by_selection_id[sid]
            pick_data = {
                'description' : es.selection.description,
                'pick' : es.selection_value,
                'actual' : es.selection.actual_outcome,
                'outcome' : outcome_value(es.selection_value, es.selection.actual_outcome)
            }
            pick_datas.append(pick_data)
        group_picks[group] = pick_datas
    data['group_picks'] = group_picks

    points = score.score_entrant(db.session, entrant_id)
    data['total_points'] = points

    return render_template("picks.html", **data)

@footy_http.route('/standings')
def standings():
    data = {}
    total = score.total_points(db.session)
    entrants = analysis.rankings(db.session)
    data['total'] = total
    data['entrants'] = []
    for entrant, pts in entrants:
        data['entrants'].append({
            'name' : entrant.name,
            'link' : "/picks/{}".format(entrant.id),
            'points' : pts
        })
    return render_template("standings.html", **data)

