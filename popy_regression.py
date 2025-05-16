import matplotlib.pyplot as plt
from tsmoothie.smoother import *
from tsmoothie.smoother import LowessSmoother
import pandas as pd
import math
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

def smooth(data):
    x = data[:, 0].reshape(1, -1)
    y = data[:, 1].reshape(1, -1)

    smoother = LowessSmoother(smooth_fraction=0.1, iterations=3)  # iterations=3
    smoother.smooth(y)

    smooth_data = smoother.smooth_data

    re_data = []
    for i in range(len(smooth_data[0])):
        re_data.append([x[0][i], smooth_data[0][i]])

    return re_data

# Mark normal data and abnormal data
def set_color(temp_image, data_path, i_th):
    length = temp_image.shape[1]
    width = temp_image.shape[0]
    df = pd.read_csv(data_path)
    wind_speed = df['Wspd']
    wind_power = df['Patv']

    # Eliminate the missing values
    windSpeed = np.array(wind_speed).reshape(len(df), 1)
    windPower = np.array(wind_power).reshape(len(df), 1)
    X_train = np.concatenate((windSpeed, windPower), axis=1)

    # Eliminate the missing values
    temp = []
    for i in range(len(X_train)):
        if np.isnan(X_train[i][0]) or np.isnan(X_train[i][1]):
            pass
        else:
            temp.append([X_train[i][0], X_train[i][1]])
    nonan_data = temp
    del temp

    nonan_data = np.array(nonan_data)
    power_old = nonan_data[:, 1]

    # Calculate the quartiles
    q1_old = np.percentile(power_old, 25)  # 第一四分位数
    q3_old = np.percentile(power_old, 75)  # 第三四分位数
    # Calculate the interquartile range
    iqr_old = q3_old - q1_old

    speed_old = nonan_data[:, 0]
    s1_old = np.percentile(speed_old, 25)  # 第一四分位数
    s3_old = np.percentile(speed_old, 75)  # 第三四分位数
    # Calculate the interquartile range
    isr_old = s3_old - s1_old

    ws = []
    wp = []

    type1 = []
    type2 = []
    type3 = []
    normal = []
    all_count = len(wind_speed)
    for i_1 in range(len(wind_speed)):
        if math.isnan(wind_speed[i_1]) or math.isnan(wind_power[i_1]):
            all_count = all_count - 1
            continue
        elif wind_speed[i_1] > 3 and wind_power[i_1] <= 0:
            type1.append([wind_speed[i_1], wind_power[i_1]])
            continue
        elif wind_speed[i_1] <= 3 and wind_power[i_1] <= 0:
            normal.append([wind_speed[i_1], wind_power[i_1]])
        elif wind_speed[i_1] > 10 and wind_power[i_1] > 1500:
            normal.append([wind_speed[i_1], wind_power[i_1]])
        ws.append(wind_speed[i_1])
        wp.append(wind_power[i_1])

    ws_min = min(ws)
    ws_max = max(ws)
    ws_dt = ws_max - ws_min
    wp_min = min(wp)
    wp_max = max(wp)
    wp_dt = wp_max - wp_min

    for ws_i in range(len(ws)):
        image_y = int((length * ws[ws_i]) / ws_dt) - 1
        image_x = int(width - (width * wp[ws_i]) / wp_dt) - 1
        if image_x < 0 or image_x > width - 1 or image_y < 0 or image_y > length - 1:
            continue
        if temp_image[image_x][image_y][0] == 0 and temp_image[image_x][image_y][1] == 0 and temp_image[image_x][image_y][2] == 255:   #红色——type3
            type3.append([ws[ws_i], wp[ws_i]])
        elif temp_image[image_x][image_y][0] == 255 and temp_image[image_x][image_y][1] == 0 and temp_image[image_x][image_y][2] == 0:   #蓝色——normal
            normal.append([ws[ws_i], wp[ws_i]])
        else:
            type2.append([ws[ws_i], wp[ws_i]])
    normal = np.array(normal)
    power_new = normal[:, 1]
    # Calculate the quartiles
    q1_new = np.percentile(power_new, 25)  # The first quartile
    q3_new = np.percentile(power_new, 75)  # The third quartile
    # Calculate the interquartile range
    iqr_new = q3_new - q1_new

    speed_new = normal[:, 0]
    s1_new = np.percentile(speed_new, 25)  # The first quartile
    s3_new = np.percentile(speed_new, 75)  # The third quartile
    # Calculate the interquartile range
    isr_new = s3_new - s1_new
    print('Quartile variation of wind peed:')
    print(isr_old, isr_new)
    print('Quartile variation of wind power:')
    print(iqr_old, iqr_new)
    type1 = np.array(type1)
    type2 = np.array(type2)
    type3 = np.array(type3)
    type1_count = type1.shape[0]
    type3_count = type3.shape[0]
    normal_count = normal.shape[0]
    type2_count = all_count - type1_count - type3_count - normal_count

    print('all_count:', all_count)
    print('normal_count:', normal_count)
    print('type1_count:', type1_count)
    print('type2_count:', type2_count)
    print('type3_count:', type3_count)
    print('Deletion rate R:')
    print((type1_count + type2_count + type3_count) / all_count)
    print('Wind curtailment rate:',  round((type3_count / all_count) * 100, 2))

    if len(type1) != 0:
        plt.scatter(type1[:, 0], type1[:, 1], c='aqua', s=1, label='Type I')
    if len(type2) != 0:
        plt.scatter(type2[:, 0], type2[:, 1], c='magenta', s=1, label='Type II')
    if len(type3) != 0:
        plt.scatter(type3[:, 0], type3[:, 1], c='dodgerblue', s=1, label='Type III')  #c='dodgerblue'
    plt.scatter(normal[:, 0], normal[:, 1], c='g', s=1, label='Normal data')
    plt.xlabel('Wind Speed（m/s）')
    plt.ylabel('Wind Power（kW）')
    plt.legend()
    plt.show()

    return all_count, type1_count, type2_count, type3_count, normal_count
