import sys
import re
from pyexcel_ods import get_data
import json
import datetime
import pytz
import numpy as np

from pymap3d import ecef2enu, enu2ecef, ecef2geodetic, geodetic2ecef
def coordinates_on_track(Pos,L,H,D):
    lat,lon,alt = ecef2geodetic(Pos[0],Pos[1],Pos[2])
    H_res = np.sqrt(D**2 - L**2) + H
    alt-=H_res
    return [geodetic2ecef(lat,lon,alt), (lat, lon, alt)]


def static_positions(start_times_utc, end_times_utc, rtk_date_time, Pos, L, H, Dist, Q ):
    Av_pos = []
    for i in range(len(start_times_utc)):
        error = False
        e=0.
        n=0
        sum_pos = np.array([0.,0.,0.], dtype = np.float64)
        disp = np.array([0.,0.,0.], dtype = np.float64)
        for j in range(len(rtk_date_time)):
            if (rtk_date_time[j]>=start_times_utc[i].replace(tzinfo=None) and rtk_date_time[j]<=end_times_utc[i].replace(tzinfo=None) and  int(Q[j]) ==1):
                n+=1
                sum_pos = sum_pos + np.array(Pos[j],dtype = np.float64)
            else:
                error = True
                continue
        if n==0 :
            continue
        if error == True:
            continue
        Av_pos.append(coordinates_on_track(sum_pos/n,L,H,Dist[i]))
        print(start_times_utc[i], "ecef:", Av_pos[-1][0], "lla:",Av_pos[-1][1])
    return Av_pos

def fmt_time(time_zone, date, local_start_time, local_stop_time):
    naive_datetime_start = datetime.datetime.strptime(date + " " + str(local_start_time), "%Y/%m/%d %H:%M:%S")
    naive_datetime_stop = datetime.datetime.strptime(date + " " + str(local_stop_time), "%Y/%m/%d %H:%M:%S")
    local_datetime_start = time_zone.localize(naive_datetime_start, is_dst=None)
    local_datetime_stop = time_zone.localize(naive_datetime_stop, is_dst=None)


    start_time_utc = local_datetime_start.astimezone(pytz.utc) + datetime.timedelta(seconds=18)

    end_time_utc =local_datetime_stop.astimezone(pytz.utc) + datetime.timedelta(seconds=18)
    print(start_time_utc,end_time_utc)
    return start_time_utc,end_time_utc

def validation2(path_to_table, path_to_rtk, date) :
    data = get_data(path_to_table)
    data =list(data.items())
    data = data[0][1]
    print(data[0])
    print (data[1])
    L = np.double(data[0][7])
    H = np.double(data[0][10])

    Utc_time_start = []
    Utc_time_stop =[]
    Dist =[]
    time_zone = pytz.timezone("Europe/Moscow")
    Local_start_times = []
    for i in range (2, len(data)):
        start_time = data[i][3]
        Local_start_times.append(start_time)
        stop_time = data[i][4]
        Dist.append(data[i][5])
        start, stop = fmt_time(time_zone,date,start_time,stop_time)
        Utc_time_start.append(start)
        Utc_time_stop.append(stop)
    with open(path_to_rtk) as f:
        rtk = f.readlines()
    rtk = rtk[27:len(rtk)]
    Q = []
    rtk_date_time = []
    Pos = []
    for l in rtk:
        lst = l.split()
        time = lst[0] + " " + lst[1]
        Q.append(lst[5])
        rtk_date_time.append(datetime.datetime.strptime(time, "%Y/%m/%d %H:%M:%S.%f"))
        Pos.append([lst[2], lst[3], lst[4]])

    static_positions(Utc_time_start, Utc_time_stop, rtk_date_time,Pos,L,H, Dist, Q)
if __name__ == "__main__":
    validation2("/home/hedonistant/Documents/geospider_new/markers.ods", "/home/hedonistant/Documents/geospider_new/rover/pete2180.pos", "2020/08/05")