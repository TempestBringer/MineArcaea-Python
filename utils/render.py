from utils.arcs import arc_s, arc_b, arc_si, arc_so, arc_siso, arc_sosi, arc_sisi, arc_soso


def note_render(args, note, timings, song):
    # 命令队列
    commands = []
    # 帧间隔毫秒
    frame_time = 1000 / args['tps']
    # timings 指针
    timings_pointer = 0
    # 基础bpm，现在bpm/基础bpm*基础流速为当前流速
    bpm_base = song['bpm_base']
    # 定位到note到达判定线时的timing参数
    while timings[timings_pointer]['t'] < note['t']:
        timings_pointer += 1
        if timings_pointer == len(timings):
            break
    timings_pointer -= 1

    # 当前帧的毫秒。帧对齐，这一帧内会撞判定线
    cur_time = note['t'] - note['t'] % frame_time
    # 位移对齐
    cur_x = (note['t'] % frame_time) * timings[timings_pointer]['bpm'] * args[
        'default_speed_per_second'] / bpm_base / 1000
    # 逐帧反推，位置超出渲染界限的时候停止
    while args['track_x_upper_limit'] + args['ground_x'] > cur_x > args['track_x_lower_limit'] + args['ground_x']:
        # 上一帧时间和下一帧时间
        forward_frame = cur_time - frame_time
        # 获取两帧之间的所有timings并计算note位移
        start_timing = 0
        end_timing = 0
        for index in range(len(timings)):
            if index < len(timings) - 1:
                if timings[index]['t'] <= forward_frame <= timings[index + 1]['t']:
                    start_timing = index
                if timings[index]['t'] <= cur_time <= timings[index + 1]['t']:
                    end_timing = index
            else:
                # 最后一个timing
                if timings[index]['t'] < forward_frame:
                    start_timing = index
                    end_timing = index
        if start_timing == end_timing:  # 在同一个timing里面
            cur_x += frame_time * timings[start_timing]['bpm'] * args['default_speed_per_second'] / bpm_base / 1000
        else:  # 一帧横跨多个timing
            for index in range(start_timing, end_timing + 1):
                if index == start_timing:  # 区间第一个timing
                    cur_x += (timings[index + 1]['t'] - forward_frame) * timings[index]['bpm'] * args[
                        'default_speed_per_second'] / bpm_base / 1000
                elif index == end_timing:  # 区间最后一个timing
                    cur_x += (cur_time - timings[index]['t']) * timings[index]['bpm'] * args[
                        'default_speed_per_second'] / bpm_base / 1000
                else:  # 非区间最后一个timing
                    cur_x += (timings[index + 1]['t'] - timings[index]['t']) * timings[index]['bpm'] * args[
                        'default_speed_per_second'] / bpm_base / 1000

        # 位置推算完毕，开始绘制。note含有t和lane 0~5
        start_x = cur_x
        start_y = args['ground_y']
        start_z = args['ground_z'] + note['lane'] * args['ground_interval'] - 3
        end_z = args['ground_z'] + note['lane'] * args['ground_interval'] + 3
        command_base = "fill " + str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(start_z)) + " " + \
                       str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(end_z))
        command_cur_frame = command_base + " " + args['note_material'] + " \n"
        command_next_frame = command_base + " " + args['air_material'] + " \n"

        commands.append((int(forward_frame / frame_time), command_cur_frame))
        commands.append((int(cur_time / frame_time), command_next_frame))

        # 帧计算完毕，帧向前反推
        cur_time -= frame_time

    return commands


def arctap_render(args, arctap, timings, song, x, y):
    # 命令队列
    commands = []
    # 帧间隔毫秒
    frame_time = 1000 / args['tps']
    # timings 指针
    timings_pointer = 0
    # 基础bpm，现在bpm/基础bpm*基础流速为当前流速
    bpm_base = song['bpm_base']
    # 定位到note到达判定线时的timing参数
    while timings[timings_pointer]['t'] < arctap:
        timings_pointer += 1
        if timings_pointer == len(timings):
            break
    timings_pointer -= 1

    # 当前帧的毫秒。帧对齐，这一帧内会撞判定线
    cur_time = arctap - arctap % frame_time
    # 位移对齐
    cur_x = (arctap % frame_time) * timings[timings_pointer]['bpm'] * args[
        'default_speed_per_second'] / bpm_base / 1000
    # 逐帧反推，位置超出渲染界限的时候停止
    while args['track_x_upper_limit'] + args['ground_x'] > cur_x > args['track_x_lower_limit'] + args['ground_x']:
        # 上一帧时间和下一帧时间
        forward_frame = cur_time - frame_time
        # 获取两帧之间的所有timings并计算note位移
        start_timing = 0
        end_timing = 0
        for index in range(len(timings)):
            if index < len(timings) - 1:
                if timings[index]['t'] <= forward_frame <= timings[index + 1]['t']:
                    start_timing = index
                if timings[index]['t'] <= cur_time <= timings[index + 1]['t']:
                    end_timing = index
            else:
                # 最后一个timing
                if timings[index]['t'] < forward_frame:
                    start_timing = index
                    end_timing = index
        if start_timing == end_timing:  # 在同一个timing里面
            cur_x += frame_time * timings[start_timing]['bpm'] * args['default_speed_per_second'] / bpm_base / 1000
        else:  # 一帧横跨多个timing
            for index in range(start_timing, end_timing + 1):
                if index == start_timing:  # 区间第一个timing
                    cur_x += (timings[index + 1]['t'] - forward_frame) * timings[index]['bpm'] * args[
                        'default_speed_per_second'] / bpm_base / 1000
                elif index == end_timing:  # 区间最后一个timing
                    cur_x += (cur_time - timings[index]['t']) * timings[index]['bpm'] * args[
                        'default_speed_per_second'] / bpm_base / 1000
                else:  # 非区间最后一个timing
                    cur_x += (timings[index + 1]['t'] - timings[index]['t']) * timings[index]['bpm'] * args[
                        'default_speed_per_second'] / bpm_base / 1000

        # 位置推算完毕，开始绘制。note含有t和lane 0~5
        start_x = cur_x
        start_y = y * args['ground_interval'] * args['y_ratio'] + args['arc_raise']
        start_z = args['ground_z'] + 1.5 * args['ground_interval'] + x * 2 * args['ground_interval'] - 2
        end_z = args['ground_z'] + 1.5 * args['ground_interval'] + x * 2 * args['ground_interval'] + 2
        command_base = "fill " + str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(start_z)) + " " + \
                       str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(end_z))
        command_cur_frame = command_base + " " + args['arctap_material'] + " \n"
        command_next_frame = command_base + " " + args['air_material'] + " \n"

        commands.append((int(forward_frame / frame_time), command_cur_frame))
        commands.append((int(cur_time / frame_time), command_next_frame))

        # 帧计算完毕，帧向前反推
        cur_time -= frame_time

    return commands


# arc实体渲染
def arc_arc_render(args, arc_part, timings, song, x, y, color):
    # 命令队列
    commands = []
    # 帧间隔毫秒
    frame_time = 1000 / args['tps']
    # timings 指针
    timings_pointer = 0
    # 基础bpm，现在bpm/基础bpm*基础流速为当前流速
    bpm_base = song['bpm_base']
    # 定位到note到达判定线时的timing参数
    while timings[timings_pointer]['t'] < arc_part:
        timings_pointer += 1
        if timings_pointer == len(timings):
            break
    timings_pointer -= 1

    # 当前帧的毫秒。帧对齐，这一帧内会撞判定线
    cur_time = arc_part - arc_part % frame_time
    # 位移对齐
    cur_x = (arc_part % frame_time) * timings[timings_pointer]['bpm'] * args[
        'default_speed_per_second'] / bpm_base / 1000
    # 逐帧反推，位置超出渲染界限的时候停止
    while args['track_x_upper_limit'] + args['ground_x'] > cur_x > args['track_x_lower_limit'] + args['ground_x']:
        # 上一帧时间和下一帧时间
        forward_frame = cur_time - frame_time
        # 获取两帧之间的所有timings并计算note位移
        start_timing = 0
        end_timing = 0
        for index in range(len(timings)):
            if index < len(timings) - 1:
                if timings[index]['t'] <= forward_frame <= timings[index + 1]['t']:
                    start_timing = index
                if timings[index]['t'] <= cur_time <= timings[index + 1]['t']:
                    end_timing = index
            else:
                # 最后一个timing
                if timings[index]['t'] < forward_frame:
                    start_timing = index
                    end_timing = index
        if start_timing == end_timing:  # 在同一个timing里面
            cur_x += frame_time * timings[start_timing]['bpm'] * args['default_speed_per_second'] / bpm_base / 1000
        else:  # 一帧横跨多个timing
            for index in range(start_timing, end_timing + 1):
                if index == start_timing:  # 区间第一个timing
                    cur_x += (timings[index + 1]['t'] - forward_frame) * timings[index]['bpm'] * args[
                        'default_speed_per_second'] / bpm_base / 1000
                elif index == end_timing:  # 区间最后一个timing
                    cur_x += (cur_time - timings[index]['t']) * timings[index]['bpm'] * args[
                        'default_speed_per_second'] / bpm_base / 1000
                else:  # 非区间最后一个timing
                    cur_x += (timings[index + 1]['t'] - timings[index]['t']) * timings[index]['bpm'] * args[
                        'default_speed_per_second'] / bpm_base / 1000

        # 位置推算完毕，开始绘制。
        start_x = cur_x
        start_y = y * args['ground_interval'] * args['y_ratio'] + args['arc_raise']
        start_z = args['ground_z'] + 1.5 * args['ground_interval'] + x * 2 * args['ground_interval']

        command_base_x = "fill " + str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(start_z - 1)) + " " + \
                         str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(start_z + 1))
        command_base_y = "fill " + str(int(start_x)) + " " + str(int(start_y - 1)) + " " + str(int(start_z)) + " " + \
                         str(int(start_x)) + " " + str(int(start_y + 1)) + " " + str(int(start_z))
        if color == -1:
            # particle minecraft:dust 0.999 0 0 0.2 ~ ~1 ~ 0 0 0 10000 1 force
            command_cur_frame = "setblock " + str(int(start_x)) + " " + str(int(start_y)) + " " + str(
                int(start_z)) + " " + args['black_line_materials'] + " \n"
            commands.append((int(forward_frame / frame_time), command_cur_frame))
        elif color == -2:
            command_particle = "particle minecraft:dust 0.2 0.2 0.2 0.5 " + str(start_x)[0:6] + " " + str(start_y)[
                                                                                                      0:6] + " " + str(
                start_z)[0:6] + " 0 0 0 100 1 force \n"
            commands.append((int(forward_frame / frame_time), command_particle))
        elif color == 0:
            command_cur_frame_x = command_base_x + " " + args['blue_arc_material'] + " \n"
            commands.append((int(forward_frame / frame_time), command_cur_frame_x))
            command_cur_frame_y = command_base_y + " " + args['blue_arc_material'] + " \n"
            commands.append((int(forward_frame / frame_time), command_cur_frame_y))
        elif color == 1:
            command_cur_frame_x = command_base_x + " " + args['red_arc_material'] + " \n"
            commands.append((int(forward_frame / frame_time), command_cur_frame_x))
            command_cur_frame_y = command_base_y + " " + args['red_arc_material'] + " \n"
            commands.append((int(forward_frame / frame_time), command_cur_frame_y))
        elif color == 2:
            command_cur_frame_x = command_base_x + " " + args['green_arc_material'] + " \n"
            commands.append((int(forward_frame / frame_time), command_cur_frame_x))
            command_cur_frame_y = command_base_y + " " + args['green_arc_material'] + " \n"
            commands.append((int(forward_frame / frame_time), command_cur_frame_y))
        # 填充空气
        if color == -1:
            command_cur_frame = "setblock " + str(int(start_x)) + " " + str(int(start_y)) + " " + str(
                int(start_z)) + " " + args['air_material'] + " \n"
            commands.append((int(cur_time / frame_time), command_cur_frame))
        elif color in [0, 1, 2]:
            command_next_frame_x = command_base_x + " " + args['air_material'] + " \n"
            commands.append((int(cur_time / frame_time), command_next_frame_x))
            command_next_frame_y = command_base_y + " " + args['air_material'] + " \n"
            commands.append((int(cur_time / frame_time), command_next_frame_y))

        # 帧计算完毕，帧向前反推
        cur_time -= frame_time
    return commands


def arc_render(args, arc, timings, song):
    # 命令队列
    commands = []
    arctaps = arc['arctaps']
    for arctap in arctaps:
        if arc['easing'] == 's':
            result = arc_s(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], arctap)
        elif arc['easing'] == 'b':
            result = arc_b(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], arctap)
        elif arc['easing'] == 'si':
            result = arc_si(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], arctap)
        elif arc['easing'] == 'so':
            result = arc_so(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], arctap)
        elif arc['easing'] == 'sisi':
            result = arc_sisi(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], arctap)
        elif arc['easing'] == 'siso':
            result = arc_siso(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], arctap)
        elif arc['easing'] == 'sosi':
            result = arc_sosi(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], arctap)
        elif arc['easing'] == 'soso':
            result = arc_soso(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], arctap)
        for _result in result:
            commands = commands + arctap_render(args, arctap, timings, song, _result[0], _result[1])
    # 天键渲染完毕，开始渲染Arc
    # 确定渲染间隔
    frame_time = 1000 / args['tps']
    render_interval = args['default_speed_per_second']
    num_interval = (arc['t2'] - arc['t1']) * args['default_speed_per_second'] / 1000
    # 逐方块渲染
    if arc['skylineBoolean'] or len(arctaps) > 0:
        # 黑线
        if args['enable_blackline'] == 'False':
            print("跳过黑线绘制")
        else:
            print("正在绘制一条黑线")
            start_frame_time = arc['t1'] - arc['t1'] % frame_time
            cur_time = start_frame_time
            while cur_time < arc['t2']:
                if arc['easing'] == 's':
                    results = arc_s(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
                elif arc['easing'] == 'b':
                    results = arc_b(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
                elif arc['easing'] == 'si':
                    results = arc_si(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
                elif arc['easing'] == 'so':
                    results = arc_so(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
                elif arc['easing'] == 'sisi':
                    results = arc_sisi(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
                elif arc['easing'] == 'siso':
                    results = arc_siso(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
                elif arc['easing'] == 'sosi':
                    results = arc_sosi(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
                elif arc['easing'] == 'soso':
                    results = arc_soso(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
                if args['blackline_mode'] == 'block':
                    for _result in results:
                        commands = commands + arc_arc_render(args, cur_time, timings, song, _result[0], _result[1], -1)
                    cur_time += frame_time * args['tps'] / args['default_speed_per_second']
                elif args['blackline_mode'] == 'particle':
                    for _result in results:
                        commands = commands + arc_arc_render(args, cur_time, timings, song, _result[0], _result[1], -2)
                    cur_time += frame_time * args['tps'] / args['default_speed_per_second'] / args['particle_dense']
                else:
                    raise Exception("不存在的黑线处理方法")
    else:  # arc
        print("正在绘制一条arc")
        start_frame_time = arc['t1'] - arc['t1'] % frame_time
        cur_time = start_frame_time
        while cur_time < arc['t2']:
            if arc['easing'] == 's':
                result = arc_s(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
            elif arc['easing'] == 'b':
                result = arc_b(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
            elif arc['easing'] == 'si':
                result = arc_si(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
            elif arc['easing'] == 'so':
                result = arc_so(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
            elif arc['easing'] == 'sisi':
                result = arc_sisi(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
            elif arc['easing'] == 'siso':
                result = arc_siso(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
            elif arc['easing'] == 'sosi':
                result = arc_sosi(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
            elif arc['easing'] == 'soso':
                result = arc_soso(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], cur_time)
            for _result in result:
                commands = commands + arc_arc_render(args, cur_time, timings, song, _result[0], _result[1],
                                                     arc['color'])
            cur_time += frame_time * args['tps'] / args['default_speed_per_second']
    return commands


def hold_render(args, hold, timings, song):
    # 命令队列
    commands = []
    # 帧间隔毫秒
    frame_time = 1000 / args['tps']
    # timings 指针
    timings_pointer = 0
    # 基础bpm，现在bpm/基础bpm*基础流速为当前流速
    bpm_base = song['bpm_base']

    # hold头部拓展
    # 定位到note到达判定线时的timing参数
    while timings[timings_pointer]['t'] < hold['t1']:
        timings_pointer += 1
        if timings_pointer == len(timings):
            break
    timings_pointer -= 1
    # 当前帧的毫秒。帧对齐，这一帧内尾部会撞判定线
    cur_time1 = hold['t1'] - hold['t1'] % frame_time
    # 位移对齐
    cur_x1 = (hold['t2'] % frame_time) * timings[timings_pointer]['bpm'] * args[
        'default_speed_per_second'] / bpm_base / 1000
    # 逐帧反推，位置超出渲染界限的时候停止
    while args['track_x_upper_limit'] + args['ground_x'] > cur_x1 > args['track_x_lower_limit'] + args['ground_x']:
        # 上一帧时间和下一帧时间
        forward_frame = cur_time1 - frame_time
        end_x = cur_x1
        # 获取两帧之间的所有timings并计算note位移
        start_timing = 0
        end_timing = 0
        for index in range(len(timings)):
            if index < len(timings) - 1:
                if timings[index]['t'] <= forward_frame <= timings[index + 1]['t']:
                    start_timing = index
                if timings[index]['t'] <= cur_time1 <= timings[index + 1]['t']:
                    end_timing = index
            else:
                # 最后一个timing
                if timings[index]['t'] < forward_frame:
                    start_timing = index
                    end_timing = index  # + 1
        if start_timing == end_timing:  # 在同一个timing里面
            cur_x1 += frame_time * timings[start_timing]['bpm'] * args['default_speed_per_second'] / bpm_base / 1000
        else:  # 一帧横跨多个timing
            for index in range(start_timing, end_timing + 1):
                if index == start_timing:  # 区间第一个timing
                    cur_x1 += (timings[index + 1]['t'] - forward_frame) * timings[index]['bpm'] * args[
                        'default_speed_per_second'] / bpm_base / 1000
                elif index == end_timing:  # 区间最后一个timing
                    cur_x1 += (cur_time1 - timings[index]['t']) * timings[index]['bpm'] * args[
                        'default_speed_per_second'] / bpm_base / 1000
                else:  # 非区间最后一个timing
                    cur_x1 += (timings[index + 1]['t'] - timings[index]['t']) * timings[index]['bpm'] * args[
                        'default_speed_per_second'] / bpm_base / 1000

        # 位置推算完毕，开始绘制。note含有t和lane 0~5
        if end_x > args['track_x_upper_limit']:
            end_x = args['track_x_upper_limit']
        start_x = cur_x1
        if start_x > args['track_x_upper_limit']:
            start_x = args['track_x_upper_limit']
        start_y = args['ground_y']
        start_z = args['ground_z'] + hold['lane'] * args['ground_interval'] - 3
        end_z = args['ground_z'] + hold['lane'] * args['ground_interval'] + 3
        command_base = "fill " + str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(start_z)) + " " + \
                       str(int(end_x)) + " " + str(int(start_y)) + " " + str(int(end_z))
        command_centre = "fill " + str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(start_z + 3)) + " " + \
                         str(int(end_x)) + " " + str(int(start_y)) + " " + str(int(end_z - 3))
        command_cur_frame = command_base + " " + args['hold_side_material'] + " \n"
        command_cur_frame_centre = command_centre + " " + args['hold_centre_material'] + " \n"

        commands.append((int(forward_frame / frame_time), command_cur_frame))
        commands.append((int(forward_frame / frame_time), command_cur_frame_centre))
        # 帧计算完毕，帧向前反推
        cur_time1 -= frame_time

    # hold尾部清除
    # timings 指针
    timings_pointer = 0
    # 定位到note到达判定线时的timing参数
    while timings[timings_pointer]['t'] < hold['t2']:
        timings_pointer += 1
        if timings_pointer == len(timings):
            break
    timings_pointer -= 1

    # 当前帧的毫秒。帧对齐，这一帧内尾部会撞判定线
    cur_time2 = hold['t2'] - hold['t2'] % frame_time
    # 位移对齐
    cur_x2 = (hold['t2'] % frame_time) * timings[timings_pointer]['bpm'] * args[
        'default_speed_per_second'] / bpm_base / 1000
    # 逐帧反推，位置超出渲染界限的时候停止
    while args['track_x_upper_limit'] + args['ground_x'] > cur_x2 > args['track_x_lower_limit'] + args['ground_x']:
        # 上一帧时间和下一帧时间
        forward_frame = cur_time2 - frame_time
        end_x = cur_x2
        # 获取两帧之间的所有timings并计算note位移
        start_timing = 0
        end_timing = 0
        for index in range(len(timings)):
            if index < len(timings) - 1:
                if timings[index]['t'] <= forward_frame <= timings[index + 1]['t']:
                    start_timing = index
                if timings[index]['t'] <= cur_time2 <= timings[index + 1]['t']:
                    end_timing = index
            else:
                # 最后一个timing
                if timings[index]['t'] < forward_frame:
                    start_timing = index
                    end_timing = index
        if start_timing == end_timing:  # 在同一个timing里面
            cur_x2 += frame_time * timings[start_timing]['bpm'] * args['default_speed_per_second'] / bpm_base / 1000
        else:  # 一帧横跨多个timing
            for index in range(start_timing, end_timing + 1):
                if index == start_timing:  # 区间第一个timing
                    cur_x2 += (timings[index + 1]['t'] - forward_frame) * timings[index]['bpm'] * args[
                        'default_speed_per_second'] / bpm_base / 1000
                elif index == end_timing:  # 区间最后一个timing
                    cur_x2 += (cur_time2 - timings[index]['t']) * timings[index]['bpm'] * args[
                        'default_speed_per_second'] / bpm_base / 1000
                else:  # 非区间最后一个timing
                    cur_x2 += (timings[index + 1]['t'] - timings[index]['t']) * timings[index]['bpm'] * args[
                        'default_speed_per_second'] / bpm_base / 1000

        # 位置推算完毕，开始绘制。note含有t和lane 0~5
        if end_x > args['track_x_upper_limit']:
            end_x = args['track_x_upper_limit']
        start_x = cur_x2
        if start_x > args['track_x_upper_limit']:
            start_x = args['track_x_upper_limit']
        start_y = args['ground_y']
        start_z = args['ground_z'] + hold['lane'] * args['ground_interval'] - 3
        end_z = args['ground_z'] + hold['lane'] * args['ground_interval'] + 3
        command_base = "fill " + str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(start_z)) + " " + \
                       str(int(end_x)) + " " + str(int(start_y)) + " " + str(int(end_z))
        command_cur_frame = command_base + " " + args['air_material'] + " \n"
        commands.append((int(forward_frame / frame_time), command_cur_frame))

        # 帧计算完毕，帧向前反推
        cur_time2 -= frame_time

    return commands
