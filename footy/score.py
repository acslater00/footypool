from tables import Entrant, Game, Selection, EntrantSelection

def match(v1, v2):
    if v1 is None or v2 is None:
        return False
    if v1.lower().strip() == v2.lower().strip():
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

def participants_and_correct_scores(session, entrant_id, stages):
    if isinstance(stages, int):
        stages = [stages]
    ses = session.query(Selection, EntrantSelection).filter(Selection.stage_id.in_(stages)).filter(
        EntrantSelection.entrant_id == entrant_id).filter(
        EntrantSelection.selection_id == Selection.id)
    chosen_list = [t[1].selection_value for t in ses]
    selection_objects = [s[0] for s in ses]
    ret = []
    for chosen in chosen_list:
        valid = -1
        all_null = True
        any_null = False
        for s in selection_objects:
            if match(s.game.team1, chosen) or match(s.game.team2, chosen):
                found = True
                if s.actual_outcome is None:
                    valid = 0
                elif match(s.actual_outcome, chosen):
                    valid = 1
                else:
                    valid = -1
            if s.game.team1 or s.game.team2:
                all_null = False
            if s.game.team1 is None or s.game.team2 is None:
                any_null = True
        if (all_null or any_null) and valid == -1:
            valid = 0
        ret.append((chosen, valid))
    return ret

def octofinal_participants_and_correct_values(session, entrant_id):
    ses = session.query(Selection, EntrantSelection).filter(Selection.stage_id.in_([2,10])).filter(
        EntrantSelection.entrant_id == entrant_id).filter(
        EntrantSelection.selection_id == Selection.id)
    chosen_list = [t[1].selection_value for t in ses]
    winner_list = [t[0].actual_outcome for t in ses]
    rets = []
    for c in chosen_list:
        if any([match(c, t) for t in winner_list]):
            rets.append((c, 1))
        else:
            rets.append((c, -1))
    return rets

def quarterfinal_participants_and_correct_values(session, entrant_id):
    return participants_and_correct_scores(session, entrant_id, 3)

def semifinal_participants_and_correct_values(session, entrant_id):
    return participants_and_correct_scores(session, entrant_id, 4)

def final_participants_and_correct_values(session, entrant_id):
    return participants_and_correct_scores(session, entrant_id, 5)

def champion(session, entrant_id):
    return participants_and_correct_scores(session, entrant_id, 7)

def third_place(session, entrant_id):
    return participants_and_correct_scores(session, entrant_id, 8)

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


