from tables import Entrant, Game, Selection, EntrantSelection

def match(v1, v2):
    if v1 is None or v2 is None:
        return False
    if v1.lower() == v2.lower():
        return True
    return False

def score_for_matching_value(session, entrant_id, stage_id, points_per_correct):
    accum = 0
    if entrant_id == 0:
        selections = session.query(Selection).filter(Selection.stage_id == stage_id)
        for selection in selections:
            if selection.actual_outcome:
                accum += points_per_correct
        return accum

    ses = session.query(Selection, EntrantSelection).filter(Selection.stage_id == stage_id).filter(
        EntrantSelection.entrant_id == entrant_id).filter(
        EntrantSelection.selection_id == Selection.id)

    accum = 0
    for selection, entrant_selection in ses:
        if match(selection.actual_outcome, entrant_selection.selection_value):
            accum += points_per_correct
    return accum

def score_for_feeder_stage(session, entrant_id, feeder_stage_id, points_per_correct):
    # example of championship round
    # championship round game is determined by the winners of the semifinal games
    # two potential winners in stage 5
    # two chosen winners in stage 5
    # how does it line up?

    if entrant_id == 0:
        selections = session.query(Selection).filter(Selection.stage_id == feeder_stage_id)
        winner_list = filter(None, [selection.actual_outcome for selection in selections])
        return len(winner_list) * points_per_correct

    ses = session.query(Selection, EntrantSelection).filter(Selection.stage_id == feeder_stage_id).filter(
        EntrantSelection.entrant_id == entrant_id).filter(
        EntrantSelection.selection_id == Selection.id)
    accum = 0
    winner_list = [t[0].actual_outcome for t in ses]
    chosen_list = [t[1].selection_value for t in ses]
    for chosen in chosen_list:
        valid = any([match(chosen, winner) for winner in winner_list])
        if valid:
            accum += points_per_correct
    return accum

def score_group_stage_matches(session, entrant_id):
    return score_for_matching_value(session, entrant_id, stage_id=1, points_per_correct=1)

def score_group_stage_winners(session, entrant_id):
    return score_for_matching_value(session, entrant_id, stage_id=2, points_per_correct=2)

def score_group_stage_runnerups(session, entrant_id):
    return score_for_matching_value(session, entrant_id, stage_id=10, points_per_correct=1)

def score_championship_round(session, entrant_id):
    return score_for_feeder_stage(session, entrant_id, feeder_stage_id = 5, points_per_correct=8)

def score_semifinal_round(session, entrant_id):
    return score_for_feeder_stage(session, entrant_id, feeder_stage_id = 4, points_per_correct=4)

def score_quarterfinal_found(session, entrant_id):
    return score_for_feeder_stage(session, entrant_id, feeder_stage_id = 3, points_per_correct=2)

def score_octofinal_round(session, entrant_id):
    return 0

def score_champion(session, entrant_id):
    return score_for_matching_value(session, entrant_id, stage_id=7, points_per_correct=16)

def score_third_place(session, entrant_id):
    return score_for_matching_value(session, entrant_id, stage_id=8, points_per_correct=4)

def score_entrant(session, entrant_id):
    group_stage_accum = 0
    group_stage_accum += score_group_stage_matches(session, entrant_id)
    group_stage_accum += score_group_stage_winners(session, entrant_id)
    group_stage_accum += score_group_stage_runnerups(session, entrant_id)

    knockout_stage_accum = 0
    knockout_stage_accum += score_octofinal_round(session, entrant_id)
    knockout_stage_accum += score_quarterfinal_found(session, entrant_id)
    knockout_stage_accum += score_semifinal_round(session, entrant_id)
    knockout_stage_accum += score_championship_round(session, entrant_id)
    knockout_stage_accum += score_champion(session, entrant_id)
    knockout_stage_accum += score_third_place(session, entrant_id)

    return group_stage_accum + knockout_stage_accum

def total_points(session):
    return score_entrant(session, 0)


