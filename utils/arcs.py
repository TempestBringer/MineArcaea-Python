import math

pi = 3.1415926


def arc_zero(startX, endX, startY, endY, zero_time_arc_play_dense=20):
    reses = []
    deltaX = (endX - startX) / zero_time_arc_play_dense
    deltaY = (endY - startY) / zero_time_arc_play_dense
    for i in range(zero_time_arc_play_dense):
        reses += [[i * deltaX + startX, i * deltaY + startY]]
    return reses


def arc_s(startTime, endTime, startX, endX, startY, endY, curTime):
    delta_time = endTime - startTime
    if delta_time == 0:
        return arc_zero(startX, endX, startY, endY)
    deltaX = (endX - startX) / delta_time
    deltaY = (endY - startY) / delta_time
    res = [(curTime - startTime) * deltaX + startX, (curTime - startTime) * deltaY + startY]
    return [res]


def arc_b(startTime, endTime, startX, endX, startY, endY, curTime):
    if (curTime < (startTime + endTime) / 2):
        return arc_soso(startTime, (startTime + endTime) / 2, startX, (startX + endX) / 2, startY,
                        (startY + endY) / 2, curTime)
    else:
        return arc_sisi((startTime + endTime) / 2, endTime, (startX + endX) / 2, endX, (startY + endY) / 2,
                        endY, curTime)


def arc_si(startTime, endTime, startX, endX, startY, endY, curTime):
    delta_time = endTime - startTime
    if delta_time == 0:
        return arc_zero(startX, endX, startY, endY)
    res = [startX + (endX - startX) * math.sin(0.5 * pi * (curTime - startTime) / delta_time), startY]
    return [res]


def arc_so(startTime, endTime, startX, endX, startY, endY, curTime):
    delta_time = endTime - startTime
    if delta_time == 0:
        return arc_zero(startX, endX, startY, endY)
    res = [startX + (endX - startX) * (1 - math.cos(0.5 * pi * (curTime - startTime) / delta_time)), startY]
    return [res]


def arc_sisi(startTime, endTime, startX, endX, startY, endY, curTime):
    delta_time = endTime - startTime
    if delta_time == 0:
        return arc_zero(startX, endX, startY, endY)
    res = [startX + (endX - startX) * math.sin(0.5 * pi * (curTime - startTime) / delta_time),
           startY + (endY - startY) * math.sin(0.5 * pi * (curTime - startTime) / delta_time)]
    return [res]


def arc_siso(startTime, endTime, startX, endX, startY, endY, curTime):
    delta_time = endTime - startTime
    if delta_time == 0:
        return arc_zero(startX, endX, startY, endY)
    res = [startX + (endX - startX) * math.sin(0.5 * pi * (curTime - startTime) / delta_time),
           startY + (endY - startY) * (1 - math.cos(0.5 * pi * (curTime - startTime) / delta_time))]
    return [res]


def arc_sosi(startTime, endTime, startX, endX, startY, endY, curTime):
    delta_time = endTime - startTime
    if delta_time == 0:
        return arc_zero(startX, endX, startY, endY)
    res = [startX + (endX - startX) * (1 - math.cos(0.5 * pi * (curTime - startTime) / delta_time)),
           startY + (endY - startY) * math.sin(0.5 * pi * (curTime - startTime) / delta_time)]
    return [res]


def arc_soso(startTime, endTime, startX, endX, startY, endY, curTime):
    delta_time = endTime - startTime
    if delta_time == 0:
        return arc_zero(startX, endX, startY, endY)
    res = [startX + (endX - startX) * (1 - math.cos(0.5 * pi * (curTime - startTime) / delta_time)),
           startY + (endY - startY) * (1 - math.cos(0.5 * pi * (curTime - startTime) / delta_time))]
    return [res]
