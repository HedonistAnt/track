import sys
import re
from pyexcel_ods import get_data
import json
import datetime
import pytz
import numpy as np
from calculate_pillar import calculate_pillar
from collections import OrderedDict


def static_positions(start_times_utc, end_times_utc, rtk_date_time, Pos, Q):
    Av_pos = []
    for i in range(len(start_times_utc)):
        error = False
        e = 0.
        n = 0
        sum_pos = np.array([0., 0., 0.], dtype=np.float64)
        disp = np.array([0., 0., 0.], dtype=np.float64)
        for j in range(len(rtk_date_time)):
            if (rtk_date_time[j] >= start_times_utc[i].replace(tzinfo=None) and rtk_date_time[j] <= end_times_utc[
                i].replace(tzinfo=None) and int(Q[j]) == 1):
                n += 1
                sum_pos = sum_pos + Pos[j]
            else:
                print(start_times_utc[i], "Q!=1")
                continue
            if n == 0:
                continue
            Av_pos.append(sum_pos / n)

    return Av_pos


def fmt_time(time_zone, date, local_time, start, stop):
    datetime_string = date + " " + str(local_time[0]) + ":" + str(local_time[1]) + ":" + str(local_time[2])
    print(datetime_string)
    naive_datetime = datetime.datetime.strptime(datetime_string, "%Y/%m/%d %H:%M:%S")
    local_datetime = time_zone.localize(naive_datetime, is_dst=None)
    utc_datetime = local_datetime.astimezone(pytz.utc) + datetime.timedelta(seconds=18)
    start_time_utc = utc_datetime + datetime.timedelta(minutes=start)
    end_time_utc = utc_datetime + datetime.timedelta(minutes=stop)
    return start_time_utc, end_time_utc


def validation(path_to_table, path_to_rtk, date):
    data = get_data(path_to_table)
    data = list(data.items())
    data = data[0][1]
    k = 0
    start_times = []
    end_times_utc = []
    time_zone = pytz.timezone("Europe/Moscow")
    start_times_utc = []
    oblique_start_times_utc = []
    oblique_end_times_utc = []
    L_h = []
    L_2 = []
    elevation = []
    name = "";
    Points = OrderedDict()
    Point = dict()

    for i in range(len(data)):
        if i % 12 == 0:
            Point = dict()
            name = data[i][0]
            name = name.split(sep="%")[1]
            name = name.split(" ")[0]
        if i % 12 == 1:
            start_times.append([data[i][0], data[i][1], data[i][2]])
            if i == 0:
                start_time_utc, end_time_utc = fmt_time(time_zone, date, data[i][0:3], 3, 5)
            else:
                start_time_utc, end_time_utc = fmt_time(time_zone, date, data[i][0:3], 1, 3)
            Point.update({"start_time": start_time_utc})
            Point.update({"end_time": end_time_utc})
            start_times_utc.append(start_time_utc)
            end_times_utc.append(end_time_utc)
            continue
        if i % 12 == 2:
            if i == 0:
                obl_start_time_utc, obl_end_time_utc = fmt_time(time_zone, date, data[i][0:3], 3, 5)
            else:
                obl_start_time_utc, obl_end_time_utc = fmt_time(time_zone, date, data[i][0:3], 1, 3)
            oblique_start_times_utc.append(obl_start_time_utc)
            oblique_end_times_utc.append(obl_end_time_utc)
            Point.update({"obl_start_time": obl_start_time_utc})
            Point.update({"obl_end_time": obl_end_time_utc})
            continue
        if i % 12 == 3:
            L_h = [data[i][0:3]]
            continue
        if i % 12 == 4:
            L_2 = [data[i][0:3]]
            continue
        if i % 12 == 5:
            elevation = [data[i][0:3]]
            continue
        if i % 12 == 6:
            L_h.append(data[i][0:3])
            Point.update({"L_h": L_h})
            continue
        if i % 12 == 7:
            L_2.append(data[i][0:3])
            Point.update({"L_2": L_2})
            continue
        if i % 12 == 8:
            elevation.append(data[i][0:3])
            Point.update({"elevation": elevation})
        if i % 12 == 10:
            upper_point = data[i][0:2]
            Point.update({"upper_point": upper_point})
            continue
        if i % 12 == 11:
            name1 = data[i][0].split(sep=" ")[1].split(",")[0]
            Point.update({"use_point": name1})
            max_dist = data[i][0].split(sep=" ")[3] == "MAX" and True
            Point.update({"max_dist": max_dist})
            Points.update({name: Point})
    with open(path_to_rtk) as f:
        rtk = f.readlines()

    rtk = rtk[27:len(rtk)]
    Q = []
    Pos = []
    rtk_date_time = []
    for l in rtk:
        lst = l.split()
        time = lst[0] + " " + lst[1]
        Q.append(lst[5])
        rtk_date_time.append(datetime.datetime.strptime(time, "%Y/%m/%d %H:%M:%S.%f"))
        Pos.append([lst[2], lst[3], lst[4]])

    Pos = np.array(Pos, dtype=np.float64)
    Av_pos = []
    nRMSE = []
    Disp = []
    min_dist = False
    Av_pos = static_positions(start_times_utc, end_times_utc, rtk_date_time, Pos, Q)
    Obl_av_pos = static_positions(oblique_start_times_utc, oblique_end_times_utc, rtk_date_time, Pos, Q)
    k = -1
    for P in Points.values():
        k += 1
        P.update({"Av_pos": Av_pos[k]})
        if len(Obl_av_pos) == 0:
            P.update({"Av_pos_obl": [0., 0., 0.]})
        else:
            P.update({"Av_pos_obl": Obl_av_pos[k]})
    l = np.pi * np.sqrt(0.180 ** 2 + 0.250 ** 2)
    for P in Points.values():
        name1 = P["use_point"]
        P_f = Points[name1]
        P_f = P_f["Av_pos_obl"]
        [center, height] = calculate_pillar(P["Av_pos"], P["Av_pos_obl"], P_f, P["L_h"][0], P["L_2"][0], l,
                                            P["elevation"][0], P["upper_point"], P["max_dist"])
        [center, height] = calculate_pillar(P["Av_pos"], P["Av_pos_obl"], P_f, P["L_h"][1], P["L_2"][1], l,
                                            P["elevation"][1], P["upper_point"], P["max_dist"])


if __name__ == "__main__":
    path_to_table = sys.argv[1]
    path_to_rtk = sys.argv[2]
    date = sys.argv[3]
    validation(path_to_table, path_to_rtk, date)
