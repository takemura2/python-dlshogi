from pydlshogi.player.policy_player_webapi import PolicyPlayer
import time

print("初期化開始")
start = time.time()
player = PolicyPlayer(strategy='boltzmann', debug_level=0)
elapsed_time = time.time() - start
print(f"初期化処理時間:{elapsed_time}秒")

# print("対局開始")
start = time.time()
while(not player.is_game_over()):
    usi = player.predict()
    print(f"{player.board.move_number}手目 {usi}")
    print(f"{player.board.sfen()}")
    if player.move(usi):
        # player.print_board()
        pass
    else:
        print(f"非合法手:{usi}")

elapsed_time = time.time() - start
print(f"対局終了 手数:{player.board.move_number} {player.which_win()}の勝ち")
print(f"処理時間:{elapsed_time}秒")
print(f"１手あたりの思考時間:{elapsed_time/player.board.move_number}")

player.print_board()
