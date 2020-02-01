import numpy as np
import chainer
from chainer import serializers
from chainer import cuda, Variable
import chainer.functions as F
import shogi
import pydlshogi.features as FEATURES
from pydlshogi.network.policy import PolicyNetwork
from pydlshogi.model_data import get_model_file_path


class PolicyPlayer():
    """
    次の手を予測するだけの戦略のプレイヤー
    """

    def __init__(self,
                 model_file=None,
                 strategy="boltzmann",
                 debug_level=0):
        """
            Args:
                model_file トレーニング済みのモデルファイル


                strategy (str): 指し手戦略 
                    greedy:確率が最大の手を選ぶ
                    boltzmann:確率に応じて手を選ぶ(ソフトマックス戦略)

                debug_level(int) デバッグ出力
                    0:出力しない
                    1:指し手を出力
                    2:指し手予測確率を表示

        """

        if model_file is None:
            # モデルの指定がない場合は規定のモデルを使用
            _model_file = get_model_file_path('model_policy_value')
        else:
            _model_file = model_file

        print(f"ネットワーク初期化 model_file={_model_file}")

        self.board = shogi.Board()  # type:shogi.Board
        self.strategy = strategy
        self.debug_level = debug_level
        self.modelfile = _model_file
        self.model = PolicyNetwork()
        self.model.to_gpu()
        serializers.load_npz(self.modelfile, self.model)

    def check_legal_move(self, usi_str):
        leagaled = shogi.Move.from_usi(usi_str) in self.board.legal_moves
        return leagaled

    def move(self, usi):
        if self.check_legal_move(usi):
            if self.debug_level > 0:
                turn = "先手" if self.board.turn == shogi.BLACK else "後手"
                print(f"{turn} {usi} 手数:{self.board.move_number}")

            self.board.push_usi(usi)
            return True
        else:
            return False

    def is_game_over(self):
        if self.board.is_stalemate() or self.board.is_game_over():
            return True
        else:
            return False

    def which_win(self):
        if self.board.turn == shogi.WHITE:
            return "先手"
        else:
            return "後手"

    def print_board(self):
        print(self.board.kif_str())

    def predict(self):

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
            if self.debug_level > 1:
                print('info string {:5} : {:.5f}'.format(
                    move.usi(), probabilities[label]))

        selected_index = None
        if self.strategy == 'greedy':
            # 確率が最大の手を選ぶ(グリーディー戦略)
            selected_index = self.greedy(legal_logits)
        else:
            # 確率に応じて手を選ぶ(ソフトマックス戦略)
            selected_index = self.boltzmann(
                np.array(legal_logits, dtype=np.float32), 0.5)

        bestmove = legal_moves[selected_index]

        return bestmove.usi()

    def greedy(self, logits):
        # 確率が最大の手を選ぶ(グリーディー戦略)
        return logits.index(max(logits))

    def boltzmann(self, logits, temperature):
        # 確率に応じて手を選ぶ(ソフトマックス戦略)
        logits /= temperature
        logits -= logits.max()
        probabilities = np.exp(logits)
        probabilities /= probabilities.sum()
        return np.random.choice(len(logits), p=probabilities)
