import argparse
import os
import re
import statistics

# ratingが2500以上かつ手数50手以上かつ投了で完了しているもののみ残す（それ以外は削除）
# 起動方法 python filter_csa.py /home/takemura/develop/python/shogi/data/2016/

parser = argparse.ArgumentParser()
parser.add_argument('dir', type=str)
args = parser.parse_args()

print("処理を開始します。dir={}".format(args.dir))

def find_all_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)

ptn_rate = re.compile(r"^'(black|white)_rate:.*:(.*)$")

kifu_count = 0
rates = []
for filepath in find_all_files(args.dir):
    # ディレクトリのファイル名でループ
    rate = {}
    move_len = 0
    toryo = False

    # ファイルオープン 手数と投了で終わっているかを調査 
    for line in open(filepath, 'r', encoding='utf-8'):
        line = line.strip()
        m = ptn_rate.match(line)
        if m:
            # whiteとblackのratingを格納
            rate[m.group(1)] = float(m.group(2))
        if line[:1] == '+' or line[:1] == '-':
            move_len += 1
        if line == '%TORYO':
            toryo = True
    # 投了で終わっていないか手数が50手以下だったりratingが2500以下の対局は削除する
    if not toryo or move_len <= 50 or len(rate) < 2 or min(rate.values()) < 2500:
        os.remove(filepath)
    else:
        kifu_count += 1
        # ratingを配列に追加
        rates.extend([_ for _ in rate.values()])

print('kifu count :', kifu_count)
print('rate mean : {}'.format(statistics.mean(rates)))
print('rate median : {}'.format(statistics.median(rates)))
print('rate max : {}'.format(max(rates)))
print('rate min : {}'.format(min(rates)))
