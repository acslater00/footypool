import score
from tables import Entrant, Game, Selection, EntrantSelection

def rankings(session):
    entrants = session.query(Entrant).all()
    scored_entrants = []
    for entrant in entrants:
        tup = (entrant.name.title(), score.score_entrant(session, entrant.id))
        scored_entrants.append(tup)
    scored_entrants.sort(key=lambda t: t[1], reverse=True)
    return scored_entrants


