import score
from tables import Entrant, Game, Selection, EntrantSelection
from sqlalchemy import *

def rankings(session):
    entrants = session.query(Entrant).all()
    scored_entrants = []
    for entrant in entrants:
        tup = (entrant, score.score_entrant(session, entrant.id))
        scored_entrants.append(tup)
    scored_entrants.sort(key=lambda t: t[1], reverse=True)
    return scored_entrants

def print_rankings(session):
    total = score.total_points(session)
    entrants = rankings(session)
    for entrant, pts in entrants:
        print "{:30s}\t{} / {} pts".format(entrant.name, pts, total)

def selection_distribution(session, selection_id):
    ess = session.query(EntrantSelection.selection_value, func.count(1)).filter_by(selection_id=selection_id)
    ks = ess.group_by(EntrantSelection.selection_value).order_by(desc(func.count(1)))
    for pick, cnt in ks:
        print "{:20s}\t{}".format(pick, cnt)

def selection_distribution_multi(session, selection_ids):
    ess = session.query(EntrantSelection.selection_value, func.count(1)).filter(
        EntrantSelection.selection_id.in_(selection_ids))
    ks = ess.group_by(EntrantSelection.selection_value).order_by(desc(func.count(1)))
    for pick, cnt in ks:
        print "{:20s}\t{}".format(pick, cnt)



