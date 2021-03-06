﻿import numpy as np
import shogi
# import copy

import pydlshogi.common as common


def make_input_features(piece_bb, occupied, pieces_in_hand):
    # 駒ごとにチャンネルを作成する
    # チャンネル数= 104
    # 内訳 (駒の種類8 + 成り駒6 + 持ち駒) * 2

    features = []
    for color in shogi.COLORS:
        # 駒
        for piece_type in shogi.PIECE_TYPES_WITH_NONE[1:]:
            # 自分の各駒のbb (例えば自分の歩のある場所のマス)
            bb = piece_bb[piece_type] & occupied[color]
            feature = np.zeros(9*9)
            for pos in shogi.SQUARES:
                # 駒があったらフラグを立てる
                if bb & shogi.BB_SQUARES[pos] > 0:
                    feature[pos] = 1
            features.append(feature.reshape((9, 9)))

        # 持ち駒
        for piece_type in range(1, 8):
            for n in range(shogi.MAX_PIECES_IN_HAND[piece_type]):
                if piece_type in pieces_in_hand[color] and n < pieces_in_hand[color][piece_type]:
                    feature = np.ones(9*9)
                else:
                    feature = np.zeros(9*9)
                features.append(feature.reshape((9, 9)))

    return features


def make_input_features_from_board(board):
    if board.turn == shogi.BLACK:
        piece_bb = board.piece_bb
        occupied = (board.occupied[shogi.BLACK], board.occupied[shogi.WHITE])
        pieces_in_hand = (
            board.pieces_in_hand[shogi.BLACK],
            board.pieces_in_hand[shogi.WHITE])
    else:
        piece_bb = [common.bb_rotate_180(bb) for bb in board.piece_bb]
        occupied = (common.bb_rotate_180(board.occupied[shogi.WHITE]),
                    common.bb_rotate_180(
            board.occupied[shogi.BLACK]))
        pieces_in_hand = (
            board.pieces_in_hand[shogi.WHITE],
            board.pieces_in_hand[shogi.BLACK])

    return make_input_features(piece_bb, occupied, pieces_in_hand)


def make_output_label(move, color):
    # 指し手を返す

    move_to = move.to_square
    move_from = move.from_square

    # 白の場合盤を回転
    if color == shogi.WHITE:
        move_to = common.SQUARES_R180[move_to]
        if move_from is not None:
            move_from = common.SQUARES_R180[move_from]

    # move direction
    if move_from is not None:
        to_y, to_x = divmod(move_to, 9)
        from_y, from_x = divmod(move_from, 9)

        # 移動差
        dir_x = to_x - from_x
        dir_y = to_y - from_y

        if dir_y < 0 and dir_x == 0:
            move_direction = common.UP
        elif dir_y == -2 and dir_x == -1:
            move_direction = common.UP2_LEFT
        elif dir_y == -2 and dir_x == 1:
            move_direction = common.UP2_RIGHT
        elif dir_y < 0 and dir_x < 0:
            move_direction = common.UP_LEFT
        elif dir_y < 0 and dir_x > 0:
            move_direction = common.UP_RIGHT
        elif dir_y == 0 and dir_x < 0:
            move_direction = common.LEFT
        elif dir_y == 0 and dir_x > 0:
            move_direction = common.RIGHT
        elif dir_y > 0 and dir_x == 0:
            move_direction = common.DOWN
        elif dir_y > 0 and dir_x < 0:
            move_direction = common.DOWN_LEFT
        elif dir_y > 0 and dir_x > 0:
            move_direction = common.DOWN_RIGHT

        # promote
        if move.promotion:
            move_direction = common.MOVE_DIRECTION_PROMOTED[move_direction]
    else:
        # 持ち駒
        move_direction = len(common.MOVE_DIRECTION) + move.drop_piece_type - 1

    move_label = 9 * 9 * move_direction + move_to

    return move_label


def make_features(position):
    piece_bb, occupied, pieces_in_hand, move, win = position
    features = make_input_features(piece_bb, occupied, pieces_in_hand)

    return (features, move, win)
