import cv2
import numpy as np
from popy_regression import  set_color, smooth
import time

parameter = []

alph_th = 180  #Adjustable parameters 1
line_th = 40    #Adjustable parameters 2
start = 4 # Wind turbine number - 1
end = 5 #Wind turbine number
up_down_lines_distance = 5
beita_for_curve = 5

#alpha threshold segmentation
def alph_Threshold(image):
    img_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    length = img_HSV.shape[0]
    width = img_HSV.shape[1]
    for i in range(length):
        for j in range(width):
            S = img_HSV[i][j][1]
            if S < alph_th:
                img_HSV[i][j][0] = 0
                img_HSV[i][j][1] = 0
                img_HSV[i][j][2] = 255

    img_hsvtorgb = cv2.cvtColor(img_HSV, cv2.COLOR_HSV2BGR)
    return img_hsvtorgb

#Extract the boundary
def get_edge(image):
    blurred = cv2.GaussianBlur(image, (11, 11), 0)
    gaussImg = cv2.Canny(blurred, 10, 70)
    return gaussImg

# Detect whether the single straight line is at the upper edge or the lower edge.
def detect_up_down_singlelines(edge_image, line):
    up_line = line - up_down_lines_distance
    down_line = line + up_down_lines_distance
    up_count = 0
    for i in range(up_line, line):
        for j in range(edge_image.shape[1]):
            if edge_image[i][j] == 255:
                up_count = up_count + 1

    down_count = 0
    for i in range(line + 1, down_line):
        for j in range(edge_image.shape[1]):
            if edge_image[i][j] == 255:
                down_count = down_count + 1

    if up_count > down_count:
        return up_line, line
    else:
        return line, down_line

# Detect the left endpoint of the straight line
def detect_leftpoint(edge_image, line):
    temp1 = 0
    temp2 = 0
    j = 0
    while j < edge_image.shape[1]:
        if edge_image[line][j][0] == 0 and edge_image[line][j][1] == 255 and edge_image[line][j][2] == 0:
            temp1 = j
            for k in range(j + 1, edge_image.shape[1]):
                if edge_image[line][k][0] == 0 and edge_image[line][k][1] == 255 and edge_image[line][k][2] == 0:
                    temp2 = k
                    if temp2 - temp1 > 10:   #if temp2 - temp1 > 20
                        start_point = temp2
                        return start_point
                    else:
                        break
        j = j + 1

# Detect the left endpoint of the straight line
def detect_leftpoint_edge_image(edge_image, line):
    j = 0
    while j < edge_image.shape[1]:
        if edge_image[line][j] == 255:
            temp1 = j
            for k in range(j + 1, edge_image.shape[1]):
                if edge_image[line][k] == 255:
                    temp2 = k
                    if temp2 - temp1 > 20:  #if temp2 - temp1 > 20
                        start_point = temp2
                        return start_point
                    else:
                        break
        j = j + 1

#Detect the horizontal lines and mark them on the boundary map
def edge_whole_lines(image, edge_image):
    hline = cv2.getStructuringElement(cv2.MORPH_RECT, (int((image.shape[1] / line_th)), 1), (-1, -1))  # 40 (-1, -1)

    dst = cv2.morphologyEx(image, cv2.MORPH_OPEN, hline)

    lines_index = []
    for i_1 in range(40, dst.shape[0] - 5):
        for j in range(dst.shape[1]):
            if dst[i_1][j] != 0:
                lines_index.append([i_1, j, [dst[i_1][j]]])

    edge_three = np.zeros((edge_image.shape[0], edge_image.shape[1], 3))
    edge_three[:, :, 0] = edge_image
    edge_three[:, :, 1] = edge_image
    edge_three[:, :, 2] = edge_image

    start_points = []
    start_points1 = []
    # Change from single line to double line
    single_lines_index = []
    if lines_index:
        temp = lines_index[-1][0]
        single_lines_index.append(temp)
        for i_2 in range(len(lines_index), 0, -1):
            if temp - lines_index[i_2 - 1][0] > 3:  # 处理直线重叠问题
                single_lines_index.append(lines_index[i_2 - 1][0])
                temp = lines_index[i_2 - 1][0]

        single_lines_index = single_lines_index[::-1]

        if len(single_lines_index) % 2 == 1:
            temp_true = []
            temp_false = []
            index = 0
            while index < len(single_lines_index):
                if index + 1 == len(single_lines_index):
                    temp_false.append(index)
                    break
                if single_lines_index[index + 1] - single_lines_index[index] > 3 and single_lines_index[index + 1] - \
                        single_lines_index[index] < 10:
                    temp_true.append([index, index + 1])
                    index = index + 2
                else:
                    temp_false.append(index)
                    index = index + 1

            # Complete the upper or lower line
            for line in temp_false:
                up_lines, down_lines = detect_up_down_singlelines(edge_image, single_lines_index[line])
                single_lines_index.insert(line, up_lines)
                single_lines_index[line + 1] = down_lines

        # Obtain the starting point of the third type of anomaly (the left intersection point of the straight line)
        for line in single_lines_index:
            start_point = detect_leftpoint_edge_image(edge_image, line)
            start_points.append([line, start_point])

    for star_i in range(len(start_points)):
        if start_points[star_i][1] ==None:
            if star_i % 2 == 0:
                start_points[star_i][1] = start_points[star_i + 1][1]
            else:
                start_points[star_i][1] = start_points[star_i - 1][1]

    left_points = []
    right_points = []
    for i_3 in range(0, edge_image.shape[0] - 1, beita_for_curve):
        for j in range(edge_image.shape[1]):
            if edge_image[i_3][j] == 255:
                left_points.append([i_3, j])
                break
        flag = True
        for start_i in range(1, len(start_points), 2):
            if i_3 > start_points[start_i - 1][0] and i_3 < start_points[start_i][0]:
                right_points.append([i_3, start_points[start_i - 1][1]])
                flag = False
                break
        if flag:
            for k in range(edge_image.shape[1] - 1, 0, -1):
                if edge_image[i_3][k] == 255:  # k - j < 50 and k - j > 20
                    right_points.append([i_3, k])
                    break

    left_points = np.array(left_points)
    right_points = np.array(right_points)

    left_points = smooth(left_points)
    right_points = smooth(right_points)

    for left_i in range(1, len(left_points)):
        cv2.line(edge_three, (left_points[left_i - 1][1], left_points[left_i - 1][0]),
                 (left_points[left_i][1], left_points[left_i][0]), (0, 255, 0), 1)
    for right_i in range(1, len(right_points)):
        cv2.line(edge_three, (right_points[right_i - 1][1], right_points[right_i - 1][0]),
                 (right_points[right_i][1], right_points[right_i][0]), (0, 255, 0), 1)

    # Obtain the starting point of the third type of anomaly (the left intersection point of the straight line)
    for line in single_lines_index:
        start_point = detect_leftpoint(edge_three, line)
        start_points1.append([line, start_point])

    for star_i in range(len(start_points1)):
        if start_points1[star_i][1] ==None:
            if star_i % 2 == 0:
                start_points1[star_i][1] = start_points1[star_i + 1][1]
            else:
                start_points1[star_i][1] = start_points1[star_i - 1][1]
    for point in start_points1:
        for k in range(point[1], edge_three.shape[1]):
            edge_three[point[0]][k][0] = 0
            edge_three[point[0]][k][1] = 0
            edge_three[point[0]][k][2] = 255

    return edge_three, left_points, right_points, start_points1

#Detect the horizontal line - Mark it on the original image
def detect_whole_lines(show_image, left_points, right_points, start_points, data_path, i_th):

    for left_i in range(1, len(left_points)):
        cv2.line(show_image, (left_points[left_i - 1][1], left_points[left_i - 1][0]),
                 (left_points[left_i][1], left_points[left_i][0]), (0, 255, 0), 1)
    for right_i in range(1, len(right_points)):
        cv2.line(show_image, (right_points[right_i - 1][1], right_points[right_i - 1][0]),
                 (right_points[right_i][1], right_points[right_i][0]), (0, 255, 0), 1)

    left_j = []
    right_j = []
    for im_i in range(show_image.shape[0]):
        for im_j in range(show_image.shape[1]):
            if show_image[im_i][im_j][0] == 0 and show_image[im_i][im_j][1] == 255 and show_image[im_i][im_j][2] == 0:
                left_j.append([im_i, im_j])
                break
        for im_k in range(show_image.shape[1]-1, 0, -1):
            if show_image[im_i][im_k][0] == 0 and show_image[im_i][im_k][1] == 255 and show_image[im_i][im_k][2] == 0:
                right_j.append([im_i, im_k])
                break
    temp_image = np.zeros_like(show_image)
    for im_i in range(len(left_j)):   #The normal data is set to blue
        for im_j in range(left_j[im_i][1], right_j[im_i][1]):
            temp_image[left_j[im_i][0]][im_j][0] = 255
            temp_image[left_j[im_i][0]][im_j][1] = 0
            temp_image[left_j[im_i][0]][im_j][2] = 0

    if start_points:  #The third type of abnormal data is set to red
        for point_i in range(1, len(start_points), 2):
            upl_x = start_points[point_i - 1][0]
            downl_x = start_points[point_i][0]
            for x_i in range(upl_x, downl_x):
                for x_j in range(temp_image.shape[1]-1, 0, -1):
                    if temp_image[x_i][x_j][0] == 255 and \
                            temp_image[x_i][x_j][1] == 0 and \
                            temp_image[x_i][x_j][2] == 0:
                        break
                    else:
                        temp_image[x_i][x_j][0] = 0
                        temp_image[x_i][x_j][1] = 0
                        temp_image[x_i][x_j][2] = 255

    all_count, type1_count, type2_count, type3_count, normal_count = set_color(temp_image, data_path, i_th)

    return show_image, all_count, type1_count, type2_count, type3_count, normal_count


for i in range(start, end):
    print('Turb_', i+1)
    time_start = time.time()
    read_path = 'row_image_nolines/' + str(i + 1) + '.jpg'
    data_path = 'row_datas_15min/' + str(i + 1) + '.csv'

    image = cv2.imread(read_path)

    image_alph = alph_Threshold(image)

    image_edge = get_edge(image_alph)

    edge_line, left_points, right_points, start_points = edge_whole_lines(image_edge, image_edge)

    image_lines, all_count, type1_count, type2_count, type3_count, normal_count = detect_whole_lines(image, left_points, right_points, start_points, data_path, i + 1)

    time_end = time.time()

    print("run time:", time_end - time_start, 's')