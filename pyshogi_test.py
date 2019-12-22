import shogi

board = shogi.Board()


def print_legal_moves():
    print(f'合法手数:{len(board.legal_moves)}')
    for move in board.legal_moves:
        print(convert_usi2normal(str(move)))


def check_legal_move(usi_str):
    leagaled = shogi.Move.from_usi(usi_str) in board.legal_moves
    return leagaled


def convert_char_normal2usi(normal_char):

    ret = normal_char.replace('a', '1') \
        .replace('1', 'a')\
        .replace('2', 'b')\
        .replace('3', 'c')\
        .replace('4', 'd')\
        .replace('5', 'e')\
        .replace('6', 'f')\
        .replace('7', 'g')\
        .replace('8', 'h')\
        .replace('9', 'i')
    return ret


def convert_char_usi2normal(usi_move_char):
    ret = usi_move_char.replace('a', '1') \
        .replace('a', '1')\
        .replace('b', '2')\
        .replace('c', '3')\
        .replace('d', '4')\
        .replace('e', '5')\
        .replace('f', '6')\
        .replace('g', '7')\
        .replace('h', '8')\
        .replace('i', '9')
    return ret


def convert_normal2usi(normal_move_str):
    ret = normal_move_str[0]
    ret = ret + convert_char_normal2usi(normal_move_str[1])
    ret = ret + normal_move_str[2]
    ret = ret + convert_char_normal2usi(normal_move_str[3])
    if len(normal_move_str) > 4:
        ret = ret + normal_move_str[4]

    return ret


def convert_usi2normal(usi_move_str):

    ret = usi_move_str[0]
    ret = ret + convert_char_usi2normal(usi_move_str[1])
    ret = ret + usi_move_str[2]
    ret = ret + convert_char_usi2normal(usi_move_str[3])
    if len(usi_move_str) > 4:
        ret = ret + usi_move_str[4]
    return ret


def move(normal_move_str):
    usi = convert_normal2usi(normal_move_str)
    if not check_legal_move(usi):
        print(f"合法手ではない。{normal_move_str}:{usi}")
        return
    board.push_usi(usi)
    turn = "先手" if board.turn else "後手"
    print(f"{turn} {normal_move_str} 手数:{board.move_number-1}")
    if board.is_stalemate():
        print("stalemate")

    if board.is_game_over():
        print("game_over")

    print(board.kif_str())
    print("\n" * 3)


print('対局開始')
# print(board.kif_str())
move('7776')
move('3334')
move('8822+')
move('9192')
move('2231')
move('6172')
move('3141')
move('5161')
move('B*42')
move('9394')
move('4251+')
