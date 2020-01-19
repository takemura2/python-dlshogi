import numpy as np
import chainer
from chainer import serializers
from chainer import cuda, Variable
import chainer.functions as F
import shogi
import pydlshogi.features as FEATURES
from pydlshogi.network.policy import PolicyNetwork


class PolicyPredictor():
    """
    次の手を予測するだけの戦略のプレイヤー
    """

    __singleton = None

    def __new__(cls, *args, **kwargs):
        """
        modelの初期化におよそ0.5秒かかるためオブジェクトをSingletonにする
        """
        if cls.__singleton is None:
            cls.__singleton = super(PolicyPredictor, cls).__new__(cls)
        return cls.__singleton

    def __init__(self,
                 strategy="boltzmann",
                 debug_level=0):
        """
            Args:
                strategy (str): 指し手戦略 
                    greedy:確率が最大の手を選ぶ
                    boltzmann:確率に応じて手を選ぶ(ソフトマックス戦略)

                debug_level(int) デバッグ出力
                    0:出力しない
                    1:指し手を出力
                    2:指し手予測確率を表示

        """
        self.strategy = strategy
        self.debug_level = debug_level
        self.modelfile = '/home/takemura/develop/python/shogi/python-dlshogi/model/model_policy'
        self.model = PolicyNetwork()
        self.model.to_gpu()
        serializers.load_npz(self.modelfile, self.model)

    def check_legal_move(self, board, usi_str):
        leagaled = shogi.Move.from_usi(usi_str) in self.board.legal_moves
        return leagaled

    def move(self, sfen, usi):
        board = shogi.Board(sfen=sfen)
        if self.check_legal_move(board, usi):
            if self.debug_level > 0:
                turn = "先手" if board.turn == shogi.BLACK else "後手"
                print(f"{turn} {usi} 手数:{board.move_number}")

            board.push_usi(usi)
            return True, board.sfen()
        else:
            return False

    def is_game_over(self, board):
        if board.is_stalemate() or board.is_game_over():
            return True
        else:
            return False

    def which_win(self, board):
        if board.turn == shogi.WHITE:
            return "先手"
        else:
            return "後手"

    def print_board(self):
        print(self.board.kif_str())

    def predict(self, sfen):
        """
        sfenで盤を初期化して次の手を予測しコンピュータの手を指す
        """
        board = shogi.Board(sfen=sfen)

        # 盤面からインプットを作成
        features = FEATURES.make_input_features_from_board(board)
        x = Variable(cuda.to_gpu(np.array([features], dtype=np.float32)))

        # 誤差逆伝播不要モードでフォワード実行
        with chainer.no_backprop_mode():
            y = self.model(x)

            logits = cuda.to_cpu(y.data)[0]
            probabilities = cuda.to_cpu(F.softmax(y).data)[0]

        # 全ての合法手について
        legal_moves = []
        legal_logits = []
        for move in board.legal_moves:
            # ラベルに変換
            label = FEATURES.make_output_label(move, board.turn)
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

        # 次の手
        usi = bestmove.usi()

        # 手を指す
        board.push_usi(usi)

        return usi, board.sfen()

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
