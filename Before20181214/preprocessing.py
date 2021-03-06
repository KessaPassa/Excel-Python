import pandas as pd
import numpy as np
import env

ROOT_DIR_PATH = 'C:/Users/admin/Documents/Scenargie/2018_Graduate/case/'

ROOT_DIR_NAME = 'map1_add_census'
CHILD_DIR = 'mobility-seed_'
CSV_FILE_NAME = 'log.csv'

MAX_AREA_COUNT = 36
MAX_TIME_COUNT = 6
TIME_PER_SPLIT = 3600
COLUMNS = ['id', 'type', 'time', 'road', 'x', 'y']

X_ZERO_AREA_POS = -8700
Y_ZERO_AREA_POS = -9250
# ZERO_MESH_POS = (-8700, -9250)
AREA_RANGE = 2000
RADIUS = AREA_RANGE / 2

# class Areaを格納する配列
area = []


class Area:
    id = -1
    x = -1
    y = -1

    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    @property
    def get_id(self):
        return self.id

    @property
    def get_x(self):
        return self.x

    @property
    def get_y(self):
        return self.y


# ファイルパスを返す
def get_read_path(_dir, _seed):
    return ROOT_DIR_PATH + ROOT_DIR_NAME + '/' + _dir + '/' + CHILD_DIR + _seed + '/' + CSV_FILE_NAME


def get_write_path():
    return ROOT_DIR_PATH + ROOT_DIR_NAME + '/'


# area0を左下起点にメッシュ範囲を作成
def make_area_mesh():
    one_side = np.sqrt(MAX_AREA_COUNT)
    for index in range(MAX_AREA_COUNT):
        x = X_ZERO_AREA_POS + AREA_RANGE * (index % one_side)
        y = Y_ZERO_AREA_POS + AREA_RANGE * (index // one_side)
        area.append(Area(index, x, y))
        # print(vars(area[index]))


# 到着時間も含まれているので1時間ごとの時間に補間する
def interpolate_time(time):
    times_list = [3600 * (i + 1) for i in range(6)]

    times = []
    is_arrived = True

    if time in times_list:
        times = time
        is_arrived = False
    elif 0 < time < times_list[0]:
        times = times_list[0]
    elif times_list[0] < time < times_list[1]:
        times = times_list[1]
    elif times_list[1] < time < times_list[2]:
        times = times_list[2]
    elif times_list[2] < time < times_list[3]:
        times = times_list[3]
    elif times_list[3] < time < times_list[4]:
        times = times_list[4]
    elif times_list[4] < time < times_list[5]:
        times = times_list[5]

    return pd.Series([times, is_arrived])

# # エリア番号を線形的な数から、iとjで回した数のようにする
# def convert_area_to_contour(area_id):
#     area_id = int(area_id)
#     contour_id = str(area_id // 6)
#     contour_id += str(area_id % 6) + '0'
#
#     return contour_id


# 新しく作成したareaカラムにメッシュ番号を入力する
def set_area_id(df):
    """
    :type df: pd.DataFrame
    """
    df['area'] = -1
    for index in range(MAX_AREA_COUNT):
        df.loc[
            (area[index].get_x - RADIUS <= df['x']) & (df['x'] <= area[index].get_x + RADIUS) &
            (area[index].get_y - RADIUS <= df['y']) & (df['y'] <= area[index].get_y + RADIUS),
            'area'] = area[index].get_id


# Scenargieのoutput dataがあるPCで実行すること
if __name__ == '__main__':
    make_area_mesh()

    dir_list = ['2_8', '4_6', '6_4', '8_2']
    seed_list = [str(123 + i) for i in range(env.MAX_SEED_COUNT)]

    for _dir in dir_list:
        for _seed in seed_list:
            # ただのshift-jisではダメ
            df = pd.read_csv(get_read_path(_dir, _seed), names=COLUMNS, encoding='Shift_JISx0213')

            # 上書きしないようにコピーする
            reader = df.copy()
            # 新しくarea列を追加
            set_area_id(reader)

            # メッシュ番号が-1以外、つまり範囲外の行を削除(範囲内のみ抽出)
            reader = reader[reader['area'] != -1]

            # 到着したときに取得したのなら == 1時間ごとの時間以外なら: Trueとなるgit
            reader['is_arrived'] = False

            # time列を補間
            reader[['time', 'is_arrived']] = reader['time'].apply(interpolate_time)

            # 出力 *道路交通センサスにはjupyterで整形するので基本形のみでおけ
            reader.to_csv(get_write_path() + 'logs/' + _dir + 'seed' + _seed + '.csv',
                          index=None,
                          encoding='Shift_JISx0213')
            print(_dir + 'seed' + _seed + '.csv')

            # # roadにcensusがついている行のみ抽出
            # reader = reader[reader['road'].str.contains('census')]
            # # 道路交通センサス用に出力
            # reader.to_csv(get_write_file_path() + 'logs/census' + dir_list + '_' + 'seed' + str(seed) + '.csv',
            #               index=None,
            #               encoding='Shift_JISx0213')
