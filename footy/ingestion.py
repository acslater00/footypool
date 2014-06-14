import os
import datetime
import xlrd

def read_group(sheet, group_start_row):
    group_data = {
        'name' : None,
        'matches' : [],
        'winner' : None,
        'runnerup' : None
    }

    group_data['name'] = sheet.cell(group_start_row, 0).value
    group_data['winner'] = sheet.cell(group_start_row + 1, 8).value
    group_data['runnerup'] = sheet.cell(group_start_row + 2, 8).value

    for i in range(6):
        row_num = group_start_row + i + 2
        match_number = int(sheet.cell(row_num, 0).value)
        date = datetime.datetime(*xlrd.xldate_as_tuple(sheet.cell(row_num, 1).value, sheet.book.datemode))
        team_1 = sheet.cell(row_num,3).value
        team_2 = sheet.cell(row_num,4).value
        pick = sheet.cell(row_num, 6).value
        game = {
            'match_number' : match_number,
            'date' : date,
            'team_1' : team_1,
            'team_2' : team_2,
            'pick' : pick
        }
        group_data['matches'].append(game)
    return group_data

def read_group_sheet(sheet):
    """read in each group sheet"""
    # cell is 0 indexed, so A1 = (0,0) B2 = (1,1)
    # goes row col, so A2 = (1, 0) [strange]
    data = {
        'name' : sheet.cell(0,1).value,
        'email' : sheet.cell(1,1).value,
    }

    group_a = read_group(sheet, 3)
    group_b = read_group(sheet, 12)
    group_c = read_group(sheet, 21)
    group_d = read_group(sheet, 30)
    group_e = read_group(sheet, 39)
    group_f = read_group(sheet, 48)
    group_g = read_group(sheet, 57)
    group_h = read_group(sheet, 66)

    data['groups'] = [
        group_a,
        group_b,
        group_c,
        group_d,
        group_e,
        group_f,
        group_g,
        group_h
    ]

    return data

def read_knockout_game(sheet, row_num):
    """0 indexed row number"""
    match_number = int(sheet.cell(row_num, 0).value)
    date = datetime.datetime(*xlrd.xldate_as_tuple(sheet.cell(row_num, 1).value, sheet.book.datemode))
    team_1 = sheet.cell(row_num,4).value
    team_2 = sheet.cell(row_num,5).value
    pick = sheet.cell(row_num,6).value
    game = {
        'match_number' : match_number,
        'date' : date,
        'team_1' : team_1,
        'team_2' : team_2,
        'pick' : pick
    }
    return game

def read_knockout_sheet(sheet):

    # round of 16
    round_of_16 = [
        read_knockout_game(sheet, 4),
        read_knockout_game(sheet, 5),
        read_knockout_game(sheet, 6),
        read_knockout_game(sheet, 7),
        read_knockout_game(sheet, 8),
        read_knockout_game(sheet, 9),
        read_knockout_game(sheet, 10),
        read_knockout_game(sheet, 11)
    ]

    quarter_finals = [
        read_knockout_game(sheet, 15),
        read_knockout_game(sheet, 16),
        read_knockout_game(sheet, 17),
        read_knockout_game(sheet, 18),
    ]

    semi_finals = [
        read_knockout_game(sheet, 22),
        read_knockout_game(sheet, 23),
    ]

    third_place_match = [
        read_knockout_game(sheet, 27)
    ]

    final = [
        read_knockout_game(sheet, 31)
    ]

    tiebreakers = {
        'golden_ball' : sheet.cell(35, 2).value,
        'golden_boot' : sheet.cell(36, 2).value,
        'golden_glove' : sheet.cell(37, 2).value,
        'winner_score' : int(sheet.cell(40, 1).value),
        'loser_score' : int(sheet.cell(41, 1).value),
    }

    data = {
        'round_of_16' : round_of_16,
        'quarter_finals' : quarter_finals,
        'semi_finals' : semi_finals,
        'third_place_match' : third_place_match,
        'final' : final,
        'tiebreakers' : tiebreakers
    }
    return data

def read_entry(path):
    with xlrd.open_workbook(path) as book:
        group_sheet = book.sheets()[0]
        knockout_sheet = book.sheets()[1]

        group_data = read_group_sheet(group_sheet)
        knockout_data = read_knockout_sheet(knockout_sheet)

        return {
            'group' : group_data,
            'knockout' : knockout_data
        }

from tables import Entrant, Game, Selection, EntrantSelection
import db

def create_entrant(session, data):
    name  = data['group']['name']
    email = data['group']['email']
    entrant = session.query(Entrant).filter_by(email=email).first() or Entrant()
    entrant.name = name
    entrant.email = email
    session.merge(entrant)
    session.commit()

    # reread
    entrant = session.query(Entrant).filter_by(email=email).first()
    return entrant.id

def group_to_group_id(group_letter):
    if len(group_letter) != 1:
        group_letter = group_letter.lower().replace("group", "").strip()
    group_letter = group_letter.upper()
    return ord(group_letter) - ord('A') + 1

def create_knockout_games(session, data, stage_key, stage_name, stage_id):
    for match in data['knockout'][stage_key]:
        game = session.query(Game).filter_by(id=int(match['match_number'])).first() or Game()
        game.id = match['match_number']
        game.date = match['date']
        game.team1 = None
        game.team2 = None
        game.title = "{} - Match {}".format(stage_name, game.id)
        game.group_id = None
        game.stage_id = stage_id
        session.merge(game)

        # add selection as well
        selection = session.query(Selection).filter_by(game_id=game.id).first() or Selection()
        selection.game_id = game.id
        selection.stage_id = stage_id
        selection.description = "Winner of {} - Game {}".format(stage_name, game.id)
        session.merge(selection)

def create_tiebreaker_selections(session, data):

    s_golden_ball = session.query(Selection).filter_by(description="Golden Ball").first() or Selection()
    s_golden_ball.description = "Golden Ball"
    s_golden_ball.stage_id = 9
    session.merge(s_golden_ball)

    s_golden_boot = session.query(Selection).filter_by(description="Golden Boot").first() or Selection()
    s_golden_boot.description = "Golden Boot"
    s_golden_boot.stage_id = 9
    session.merge(s_golden_boot)

    s_golden_glove = session.query(Selection).filter_by(description="Golden Glove").first() or Selection()
    s_golden_glove.description = "Golden Glove"
    s_golden_glove.stage_id = 9
    session.merge(s_golden_glove)

    s_winner_score = session.query(Selection).filter_by(description="Winner Score").first() or Selection()
    s_winner_score.description = "Winner Score"
    s_winner_score.stage_id = 9
    session.merge(s_winner_score)

    s_loser_score = session.query(Selection).filter_by(description="Loser Score").first() or Selection()
    s_loser_score.description = "Loser Score"
    s_loser_score.stage_id = 9
    session.merge(s_loser_score)

def create_games(session, data):
    group_data = data['group']
    for group in group_data['groups']:
        for match in group['matches']:
            game = session.query(Game).filter_by(id=int(match['match_number'])).first() or Game()
            game.id = match['match_number']
            game.date = match['date']
            game.team1 = match['team_1']
            game.team2 = match['team_2']
            game.title = "{} vs {} (Match {})".format(game.team1.title(), game.team2.title(), game.id)
            game.group_id = group_to_group_id(group['name'])
            session.merge(game)

            # create a selection for this game
            selection = session.query(Selection).filter_by(game_id=game.id).first() or Selection()
            selection.game_id = game.id
            selection.description = "Winner of {} - Game {}".format(group['name'], game.id)
            selection.stage_id = 1
            session.merge(selection)

        # group winner / runner up selections
        description = "{} - Winner".format(group['name'])
        selection = session.query(Selection).filter_by(description=description).first() or Selection()
        selection.description = description
        selection.game_id = None
        selection.stage_id = 2
        session.merge(selection)

        description = "{} - Runner Up".format(group['name'])
        selection2 = session.query(Selection).filter_by(description=description).first() or Selection()
        selection2.description = description
        selection2.game_id = None
        selection2.stage_id = 10
        session.merge(selection2)

    session.commit()

    create_knockout_games(session, data, 'round_of_16', 'Round of 16', 3)
    create_knockout_games(session, data, 'quarter_finals', 'Quarter Finals', 4)
    create_knockout_games(session, data, 'semi_finals', 'Semi Finals', 5)
    create_knockout_games(session, data, 'final', 'Finals', 7)
    create_knockout_games(session, data, 'third_place_match', '3rd Place Match', 8)

    # tiebreaker statge selections
    create_tiebreaker_selections(session, data)

    session.commit()

def selection_id_for_group_winner(session, group_name):
    description = "{} - Winner".format(group_name)
    sid = session.query(Selection.id).filter_by(description=description).first()
    return sid.id

def selection_id_for_group_runnerup(session, group_name):
    description = "{} - Runner Up".format(group_name)
    sid = session.query(Selection.id).filter_by(description=description).first()
    return sid.id

def selection_id_for_tiebreaker(session, tiebreaker_name):
    description = tiebreaker_name.replace("_", " ").title()
    sid = session.query(Selection.id).filter_by(description=description).first()
    return sid.id

def selection_id_for_game_id(session, game_id):
    sid = session.query(Selection.id).filter_by(game_id=game_id).first()
    return sid.id

def create_entrant_selections(session, data, entrant_id):

    # for tiebreakers
    for key, val in data['knockout']['tiebreakers'].iteritems():
        selection_id = selection_id_for_tiebreaker(session, key)
        es = EntrantSelection()
        es.entrant_id = entrant_id
        es.selection_id = selection_id
        es.selection_value = val
        session.merge(es)
    session.commit()

    # for group stage winners / runners up
    for group in data['group']['groups']:
        group_name = group['name']
        winner_selection_id = selection_id_for_group_winner(session, group_name)
        es = EntrantSelection()
        es.entrant_id = entrant_id
        es.selection_id = winner_selection_id
        es.selection_value = group['winner']
        session.merge(es)

        runnerup_selection_id = selection_id_for_group_runnerup(session, group_name)
        es = EntrantSelection()
        es.entrant_id = entrant_id
        es.selection_id = runnerup_selection_id
        es.selection_value = group['runnerup']
        session.merge(es)
    session.commit()

    # add game selections for group stage
    for group in data['group']['groups']:
        for match in group['matches']:
            selection_id = selection_id_for_game_id(session, match['match_number'])
            es = EntrantSelection()
            es.entrant_id = entrant_id
            es.selection_id = selection_id
            es.selection_value = match['pick']
            session.merge(es)
    session.commit()

    # add game selections for knockout stage
    for key in ('round_of_16', 'quarter_finals', 'semi_finals', 'third_place_match', 'final'):
        for match in data['knockout'][key]:
            selection_id = selection_id_for_game_id(session, match['match_number'])
            es = EntrantSelection()
            es.entrant_id = entrant_id
            es.selection_id = selection_id
            es.selection_value = match['pick']
            session.merge(es)
    session.commit()


def save_entry(data):
    """given entry data (output of read_entry) save to db"""
    session = db.session

    # create entrant
    entrant = create_entrant(session, data)

    # create entrant selections
    create_entrant_selections(session, data, entrant)

def read_all_entries_for_directory(path):
    for filename in os.listdir(path):
        if "xlsx" in filename:
            full_path = os.path.join(path, filename)
            data = read_entry(full_path)
            print 'reading', data['group']['name'], data['group']['email']
            save_entry(data)

if __name__ == '__main__':

    # data = read_entry("/Users/adamc/Desktop/2014-world-adam-cohen.xlsx")
    # #create_games(db.session, data)
    # save_entry(data)

    read_all_entries_for_directory("/Users/adamc/Desktop/world-cup-entries")
