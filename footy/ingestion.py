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
        date = xlrd.xldate_as_tuple(sheet.cell(row_num, 1).value, sheet.book.datemode)
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
    match_number = sheet.cell(row_num, 0)
    date = xlrd.xldate_as_tuple(sheet.cell(row_num, 1).value, sheet.book.datemode)
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
        'golden_ball' : sheet.cell(35, 2),
        'golden_boot' : sheet.cell(36, 2),
        'golden_glove' : sheet.cell(37, 2),
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
    book = xlrd.open_workbook(path)
    group_sheet = book.sheets()[0]
    knockout_sheet = book.sheets()[1]

    group_data = read_group_sheet(group_sheet)
    knockout_data = read_knockout_sheet(knockout_sheet)


