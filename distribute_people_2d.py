import os
import pandas as pd
import numpy as np
import env
import time


def get_read_path():
    return env.ROOT_DIR() + 'Origin/'


def get_write_path():
    path = env.ROOT_DIR() + '2D/'
    if not os.path.isdir(path):
        os.makedirs(path)

    return path


# エリアと時間別に人数を+1ずつしていく
def distribute_people(base, read):
    """
    :type base: pd.DataFrame
    :type read: pd.DataFrame
    """
    df_new = pd.DataFrame()

    # グルーピングすることでforが回る数を減らし高速化
    group_list = read.groupby(['time'])
    for _name, _group in group_list:
        # 同じ時間帯のみコピーで取り出す
        tmp = base.loc[base['time'] == _name].copy()
        for g in np.asanyarray(_group):
            # {id, type, is_arrived, time, road, x, y, area}
            # 3はtime, 7はarea
            tmp.loc[tmp['area'] == g[-1], 'people'] += 1
        df_new = pd.concat([df_new, tmp])

    return df_new


# 出力するフォーマットのベースを作る
def create_people_dataframe():
    people_dataframe = np.zeros((env.MAX_TIME_COUNT() * env.MAX_AREA_COUNT(), 3))
    people_dataframe = pd.DataFrame(people_dataframe, columns=['time', 'area', 'people'])

    index = 0
    for time in range(env.MAX_TIME_COUNT()):
        for area in range(env.MAX_AREA_COUNT()):
            people_dataframe.loc[index, ['time', 'area']] = [[3600 * (time + 1), area]]
            index += 1

    return people_dataframe


def main(args):
    df_read = pd.read_csv(get_read_path() + env.get_file_name(args),
                          encoding='Shift_JISx0213',
                          dtype=None,
                          delimiter=',')

    start = time.time()

    output = distribute_people(df_base.copy(), df_read)
    output.to_csv(get_write_path() + env.get_file_name(args),
                  index=False)
    print(env.get_file_name(args))

    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")


if __name__ == '__main__':
    df_base = create_people_dataframe()
    env.for_default(main, ['mobile', 'census'])
