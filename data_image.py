import math
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# Remove the first type of exception and save it as an image
for i in range(4, 5):
    read_path = 'row_datas_15min/' + str(i+1) + '.csv'
    save_path = 'row_image_nolines/' + str(i+1) + '.jpg'
    df = pd.read_csv(read_path)
    wind_speed = df['Wspd']
    wind_power = df['Patv']
    ws = []
    wp = []

    for i_1 in range(len(wind_speed)):
        if math.isnan(wind_speed[i_1]) or math.isnan(wind_speed[i_1]):
            continue
        elif wind_speed[i_1] > 3 and wind_power[i_1] <= 0:
            continue
        else:
            ws.append(wind_speed[i_1])
            wp.append(wind_power[i_1])

    plt.scatter(ws, wp, alpha=0.5, s=1)

    plt.margins(x=0)
    plt.margins(y=0)

    plt.xticks([])
    plt.yticks([])

    plt.axis('off')
    plt.savefig(save_path, bbox_inches='tight', pad_inches=0)
    plt.clf()