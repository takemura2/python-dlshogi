﻿import numpy as np
import chainer
from chainer import serializers
from chainer import cuda, Variable
import chainer.functions as F

# import shogi

# import pydlshogi.common as COMMON
import pydlshogi.features as FEATURES
from pydlshogi.network.policy import PolicyNetwork
from pydlshogi.player.base_player import BasePlayer


def greedy(logits):
    # 確率が最大の手を選ぶ(グリーディー戦略)
    return logits.index(max(logits))


def boltzmann(logits, temperature):
    # 確率に応じて手を選ぶ(ソフトマックス戦略)
    logits /= temperature
    logits -= logits.max()
    probabilities = np.exp(logits)
    probabilities /= probabilities.sum()
    return np.random.choice(len(logits), p=probabilities)


class PolicyPlayer(BasePlayer):
    def __init__(self):
        super().__init__()
        self.modelfile = '/home/takemura/develop/python/shogi/python-dlshogi/model/model_policy'
        self.model = None

    def usi(self):
        print('id name policy_player')
        print('option name modelfile type string default ' + self.modelfile)
        print('usiok')

    def setoption(self, option):
        if option[1] == 'modelfile':
            self.modelfile = option[3]

    def isready(self):
        if self.model is None:
            self.model = PolicyNetwork()
            self.model.to_gpu()
        serializers.load_npz(self.modelfile, self.model)
        print('readyok')

    def go(self):
        if self.board.is_game_over():
            print('bestmove resign')
            return

        # 盤面からインプットを作成
        features = FEATURES.make_input_features_from_board(self.board)
        x = Variable(cuda.to_gpu(np.array([features], dtype=np.float32)))

        # 誤差逆伝播不要モードでフォワード実行
        with chainer.no_backprop_mode():
            y = self.model(x)

            logits = cuda.to_cpu(y.data)[0]
            probabilities = cuda.to_cpu(F.softmax(y).data)[0]

        # 全ての合法手について
        legal_moves = []
        legal_logits = []
        for move in self.board.legal_moves:
            # ラベルに変換
            label = FEATURES.make_output_label(move, self.board.turn)
            # 合法手とその指し手の確率(logits)を格納
            legal_moves.append(move)
            legal_logits.append(logits[label])
            # 確率を表示
            print('info string {:5} : {:.5f}'.format(
                move.usi(), probabilities[label]))

        # 確率が最大の手を選ぶ(グリーディー戦略)
        selected_index = greedy(legal_logits)
        # 確率に応じて手を選ぶ(ソフトマックス戦略)
        # selected_index = boltzmann(np.array(legal_logits, dtype=np.float32), 0.5)
        bestmove = legal_moves[selected_index]

        print('bestmove', bestmove.usi())
