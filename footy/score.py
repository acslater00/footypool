



def score_entrant(session, entrant_id):

    # user selections
    entrant_selections = session.query(EntrantSelection).filter_by(entrant_id=entrant_id)



