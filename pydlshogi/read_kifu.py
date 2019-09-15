import shogi
import shogi.CSA
import copy

from pydlshogi.features import *

# read kifu
# 棋譜ファイルリストから棋譜のファイルぱすを取得し棋譜を開いて盤面、持ち駒、指し手、勝敗データを
# 取得する
def read_kifu(kifu_list_file):
    positions = []
    with open(kifu_list_file, 'r') as f:
        for line in f.readlines():
            filepath = line.rstrip('\r\n')
            # 1棋譜ファイルからkifuオブジェクトを作成
            kifu = shogi.CSA.Parser.parse_file(filepath)[0]
            win_color = shogi.BLACK if kifu['win'] == 'b' else shogi.WHITE
            board = shogi.Board()
            # 指し手で回す
            for move in kifu['moves']:
                if board.turn == shogi.BLACK:
                    piece_bb = copy.deepcopy(board.piece_bb)
                    occupied = copy.deepcopy((board.occupied[shogi.BLACK], board.occupied[shogi.WHITE]))
                    pieces_in_hand = copy.deepcopy((board.pieces_in_hand[shogi.BLACK], board.pieces_in_hand[shogi.WHITE]))
                else:
                    # 後手は盤面を反転する
                    piece_bb = [bb_rotate_180(bb) for bb in board.piece_bb]
                    occupied = (bb_rotate_180(board.occupied[shogi.WHITE]), bb_rotate_180(board.occupied[shogi.BLACK]))
                    pieces_in_hand = copy.deepcopy((board.pieces_in_hand[shogi.WHITE], board.pieces_in_hand[shogi.BLACK]))

                # 指し手
                move_label = make_output_label(shogi.Move.from_usi(move), board.turn)

                # result
                win = 1 if win_color == board.turn else 0

                positions.append((piece_bb, occupied, pieces_in_hand, move_label, win))
                board.push_usi(move)
    return positions