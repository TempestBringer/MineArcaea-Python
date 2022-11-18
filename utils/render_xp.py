import math
from utils.arcs import arc_s, arc_b, arc_si, arc_so, arc_siso, arc_sosi, arc_sisi, arc_soso, arc_zero


def sky_input(args, sky_input_scene_ctrls):
    '''使用所有timing group做出对sky input的调整'''
    # print(sky_input_scene_ctrls)
    commands = []
    frame_time = 1000 / args['tps']
    frame_num = int(args['t_max'] / frame_time)
    # 读取含enwidencamera的语句
    enwide = []
    for line in sky_input_scene_ctrls:
        if line['type'] == 'enwidencamera':
            enwide.append(line)
    enwide.sort(key=lambda x:x['t'])
    # 是否处于enwidencamera情况
    flag_enwiden_camera = False
    frame_count = 0
    scene_ctrl_pointer = 0

    x = args['ground_x'] + 0.5
    z = args['ground_z'] + 2.5 * args['ground_interval']
    normal_height = 1 * args['ground_interval'] * args['y_ratio'] + args['arc_raise']
    enwiden_camera_height = args['enwidencamera_y_increase_ratio'] * args['ground_interval'] * args['y_ratio'] + args['arc_raise']

    command_head = "particle minecraft:end_rod " + str(x) + " "
    command_tail = " " + str(z) + " 0 0 " + str(args['sky_input_particle_length']) + " 0 " + str(args['sky_input_particle_dense']) +" force\n"


    # frame = []
    # height = []
    # for wide in enwide:
    #     enwide_command_start_time = wide['t']
    #     cur_time = enwide_command_start_time
    #     if wide['param2'] == False:
    #         while cur_time<enwide_command_start_time+wide['param1']:
    #
    #             cur_time+=frame_time
    #
    #     elif wide['param2'] == True:
    #         height = normal_height + (enwiden_camera_height-normal_height)* (frame_count*frame_time-enwide[scene_ctrl_pointer]['t'])/enwide[scene_ctrl_pointer]['param1']
    #
    #     else:
    #         raise Exception("不支持的enwidecamera参数2")



    while frame_count<frame_num:
        if scene_ctrl_pointer < len(enwide):
            # 需要处理新的enwiden_camera语句
            if frame_count*frame_time > enwide[scene_ctrl_pointer]['t']:
                while frame_count*frame_time < enwide[scene_ctrl_pointer]['t']+enwide[scene_ctrl_pointer]['param1']:
                    height = 0
                    if enwide[scene_ctrl_pointer]['param2'] == 1:
                        # 抬升
                        height = normal_height + (enwiden_camera_height-normal_height)* (frame_count*frame_time-enwide[scene_ctrl_pointer]['t'])/enwide[scene_ctrl_pointer]['param1']
                        flag_enwiden_camera = True
                    elif enwide[scene_ctrl_pointer]['param2'] == 0:
                        # 落下
                        height = enwiden_camera_height - (enwiden_camera_height - normal_height) * (
                                    frame_count * frame_time - enwide[scene_ctrl_pointer]['t']) / \
                                 enwide[scene_ctrl_pointer]['param1']
                        flag_enwiden_camera = False
                    cmd = command_head + str(round(height, 3)) + command_tail
                    commands.append((frame_count, cmd))
                    frame_count += 1
                scene_ctrl_pointer += 1
            else:
                if flag_enwiden_camera==False:
                    cmd = command_head+str(normal_height)+command_tail
                else:
                    cmd = command_head+str(enwiden_camera_height)+command_tail
                commands.append((frame_count, cmd))
                frame_count += 1
        else:
            # 最后一个语句之后
            if flag_enwiden_camera == False:
                cmd = command_head + str(normal_height) + command_tail
            else:
                cmd = command_head + str(enwiden_camera_height) + command_tail
            commands.append((frame_count, cmd))
            frame_count += 1
    return commands


def hide_group(args, frame, scenecontrols):
    '''

    :param args: 配置参数
    :param frame: 帧编号
    :param scenecontrols:
    :return:
    '''
    # 是否隐藏
    hide_flag = 'False'
    closest_frame = 0
    # 帧间隔 毫秒
    frame_time = 1000 / args['tps']
    for index in range(len(scenecontrols)):
        if scenecontrols[index]['type'] == "hidegroup":
            scene_frame = int(scenecontrols[index]['t'] / frame_time)
            if closest_frame <= scene_frame <= frame:
                closest_frame = scene_frame
                if scenecontrols[index]['param2'] == 1:
                    hide_flag = 'True'
                elif scenecontrols[index]['param2'] == 0:
                    hide_flag = 'False'
                else:
                    print(scenecontrols[index])
                    raise Exception("非法的hidegroup数值")

    return hide_flag


def scenecontrols_render(args, scenecontrols):
    frame_time = 1000 / args['tps']
    commands = []
    # if(len(scenecontrols)>0):
    #     print(scenecontrols)
    for line in scenecontrols:
        # 附加轨道
        if line['type'] == 'enwidenlanes':
            # 对齐到帧
            start_frame = int(line['t'] / frame_time)
            end_frame = int((line['t'] + line['param1']) / frame_time)
            interval_num = int(end_frame - start_frame)
            interval_block = (args['track_x_upper_limit'] - args['track_x_lower_limit']) / interval_num
            if line['param1'] < 0:
                raise Exception("非法的enwidenlanes参数1：需要为正值")
            if line['param2'] == 1:
                for i in range(interval_num+1):
                    cur_frame = start_frame + i
                    start_x = max(args['track_x_upper_limit'] - i * interval_block, args['track_x_lower_limit'])
                    low_z_slide = args['ground_z'] - args['ground_interval'] * 0.5
                    high_z_slide = args['ground_z'] + args['ground_interval'] * 5.5
                    command_draw_left_line = "fill " + str(int(start_x)) + " " + str(int(args['ground_y'] - 1)) + " " + \
                                             str(int(low_z_slide)) + " " + str(int(args['track_x_upper_limit'])) + " " + \
                                             str(int(args['ground_y'] - 1)) + " " + str(int(low_z_slide)) + " " + \
                                             args['extend_track_slide_material'] + " keep\n"
                    command_draw_right_line = "fill " + str(int(start_x)) + " " + str(int(args['ground_y'] - 1)) + " " + \
                                              str(int(high_z_slide)) + " " + str(
                                              int(args['track_x_upper_limit'])) + " " + \
                                              str(int(args['ground_y'] - 1)) + " " + str(int(high_z_slide)) + " " + \
                                              args['extend_track_slide_material'] + " keep\n"
                    command_draw_left_block = "fill " + str(int(start_x)) + " " + str(int(args['ground_y'] - 1)) + " " + \
                                              str(int(low_z_slide + 1)) + " " + str(
                                              int(args['track_x_upper_limit'])) + " " + \
                                              str(int(args['ground_y'] - 1)) + " " + str(
                                              int(low_z_slide + args['ground_interval'] - 1)) + " " + \
                                              args['extend_track_center_material'] + " keep\n"
                    command_draw_right_block = "fill " + str(int(start_x)) + " " + str(
                        int(args['ground_y'] - 1)) + " " + \
                                               str(int(high_z_slide - 1)) + " " + str(
                        int(args['track_x_upper_limit'])) + " " + \
                                               str(int(args['ground_y'] - 1)) + " " + str(
                        int(high_z_slide - args['ground_interval'] + 1)) + " " + \
                                               args['extend_track_center_material'] + " keep\n"
                    commands.append((cur_frame, command_draw_right_block))
                    commands.append((cur_frame, command_draw_left_block))
                    commands.append((cur_frame, command_draw_right_line))
                    commands.append((cur_frame, command_draw_left_line))
                    # 追加延长判定线
                    line_x = args['ground_x']
                    line_y = args['ground_y'] - 1
                    if start_x < args['ground_x']:
                        command_extend_left_line = 'fill ' + str(int(line_x)) + " " + str(int(line_y)) + " " + \
                                                   str(int(low_z_slide))+ " " + str(int(line_x)) + " " + \
                                                   str(int(line_y)) + " " + str(int(low_z_slide + args['ground_interval'] - 1)) + \
                                                   " " + args['extend_track_slide_material'] + "\n"
                        command_extend_right_line = 'fill ' + str(int(line_x)) + " " + str(int(line_y)) + " " + \
                                                   str(int(high_z_slide)) + " " + str(int(line_x)) + " " + \
                                                   str(int(line_y)) + " " + str(int(high_z_slide - args['ground_interval'] + 1)) + \
                                                   " " + args['extend_track_slide_material'] + "\n"
                        commands.append((cur_frame, command_extend_left_line))
                        commands.append((cur_frame, command_extend_right_line))
            elif line['param2'] == 0:
                for i in range(interval_num + 1):
                    cur_frame = start_frame + i
                    start_x = max(args['track_x_upper_limit'] - i * interval_block, args['track_x_lower_limit'])
                    low_z_slide = args['ground_z'] - args['ground_interval'] * 0.5
                    high_z_slide = args['ground_z'] + args['ground_interval'] * 5.5
                    command_kill_left = "fill " + str(int(start_x)) + " " + str(int(args['ground_y'] - 1)) + " " + str(
                        int(low_z_slide)) + " " + \
                                        str(int(args['track_x_upper_limit'])) + " " + str(
                        int(args['ground_y'] - 1)) + " " + str(int(low_z_slide + args['ground_interval'] - 1)) + " " + \
                                        args['air_material'] + "\n"
                    command_kill_right = "fill " + str(int(start_x)) + " " + str(int(args['ground_y'] - 1)) + " " + str(
                        int(high_z_slide)) + " " + \
                                         str(int(args['track_x_upper_limit'])) + " " + str(
                        int(args['ground_y'] - 1)) + " " + str(int(high_z_slide - args['ground_interval'] + 1)) + " " + \
                                         args['air_material'] + "\n"
                    commands.append((cur_frame, command_kill_left))
                    commands.append((cur_frame, command_kill_right))
            else:
                raise Exception("非法的enwidenlanes参数2：仅能为0或1")
    return commands
        # # Sky Input移动
        # if line['type'] == 'enwidencamera':
        #     # 对齐到帧
        #     start_frame = line['t'] - line['t'] % frame_time
        #     end_frame = (line['t']+line['param1']) % frame_time
        #     interval_num = end_frame - start_frame
        #     interval_block = args['track_x_upper_limit'] / interval_num


def position_infer(args, song, timings, time):
    # 帧间隔 毫秒
    frame_time = 1000 / args['tps']
    x_s = []
    # timings 指针
    timings_pointer = 0
    # 基础bpm，现在bpm/基础bpm*基础流速为当前流速
    bpm_base = song['bpm_base']
    # 定位到note到达判定线时的timing参数
    while timings[timings_pointer]['t'] <= time:
        timings_pointer += 1
        if timings_pointer == len(timings):
            break
    timings_pointer -= 1

    # 当前帧的毫秒。帧对齐，这一帧内会撞判定线
    cur_time = time - time % frame_time
    # cur_time = time
    # 位移对齐
    cur_x = (time % frame_time) * timings[timings_pointer]['bpm'] * args[
        'default_speed_per_second'] / bpm_base / 1000 + args['ground_x']
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
        x_s.append((int(forward_frame / frame_time), cur_x))
        # 帧计算完毕，帧向前反推
        cur_time -= frame_time
    return x_s


def sky_ground_double_key_line_render(args, song, timings, notes, arcs, timing_group_args):
    lines = []  # (地键，arc)
    commands = []
    # 对于noinput的timinggroup，不渲染天地双押线
    # print(timings)
    # print(notes)
    # print(timing_group_args)
    if timing_group_args == 'noinput':
        print("跳过该timinggroup对天地双押的渲染")
        # input()
        return commands
    # 帧间隔 毫秒
    frame_time = 1000 / args['tps']
    # 添加所有的天地线组合
    for note in notes:
        for arc in arcs:
            for arctap in arc['arctaps']:
                if note['t'] == arctap:
                    # print(note)
                    # print(arc)
                    # input()
                    lines.append([note, arc])
    print("生成了" + str(len(lines)) + "条双押线")
    # 对于每一组双押线
    for line in lines:
        arc = line[1]
        # 时间序列推理
        x_s = position_infer(args, song, timings, line[0]['t'])
        # 得到天键中心点
        result = arc_s(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], line[0]['t'])
        start_x = args['ground_z'] + line[0]['lane'] * args['ground_interval']
        start_y = args['ground_y']
        end_x = get_z(args, result[0][0])
        end_y = get_y(args, result[0][1])
        dense = int(math.sqrt((end_x - start_x) * (end_x - start_x) + (end_y - start_y) * (end_y - start_y)) / args[
            'sky_ground_double_key_line_dense'])
        double_lines = arc_zero(start_x, end_x, start_y, end_y, zero_time_arc_play_dense=dense)
        # 对于线的每一个时刻
        for x in x_s:
            # 对于该时刻的每一个点
            for double_line in double_lines:
                # command_particle = "particle minecraft:dust 0.384 0.588 0.717 2 " + str(x[1])[0:6] + " " + str(
                #     double_line[1])[0:6] + " " + str(double_line[0])[0:6] + " 0 0 0 100 1 force\n"
                command_particle = "particle minecraft:end_rod " + str(x[1])[0:6] + " " + str(
                    double_line[1])[0:6] + " " + str(double_line[0])[0:6] + " 0 0 0 999999 1 force\n"
                commands.append((x[0], command_particle))

    return commands


def note_render(args, note, timings, song, scenecontrols):
    # 命令队列
    commands = []
    x_s = position_infer(args, song, timings, note['t'])
    for x in x_s:
        hide = hide_group(args, int(x[0]), scenecontrols)
        if hide != 'True':
            # 位置推算完毕，开始绘制。note含有t和lane 0~5
            start_x = x[1]
            start_y = args['ground_y']
            start_z = get_track_z(args, note['lane']) - 3
            end_z = get_track_z(args, note['lane']) + 3
            command_base = "fill " + str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(start_z)) + " " + \
                           str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(end_z))
            command_cur_frame = command_base + " " + args['note_material'] + " \n"
            command_next_frame = command_base + " " + args['air_material'] + " \n"
            commands.append((int(x[0]), command_cur_frame))
            commands.append((int(x[0] + 1), command_next_frame))
        else:
            print("被隐藏的地键")
    return commands


def arctap_render(args, arctap, timings, song, x, y, scenecontrols):
    # 命令队列
    commands = []
    x_s = position_infer(args, song, timings, arctap)
    for x_one in x_s:
        hide = hide_group(args, x_one[0], scenecontrols)
        if hide != 'True':
            # 位置推算完毕，开始绘制arctap
            start_x = x_one[1]
            start_y = get_y(args, y)
            start_z = get_z(args,x) - 2
            end_z = get_z(args,x) + 2
            command_base = "fill " + str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(start_z)) + " " + \
                           str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(end_z))
            command_cur_frame = command_base + " " + args['arctap_material'] + " \n"
            command_next_frame = command_base + " " + args['air_material'] + " \n"
            commands.append((int(x_one[0]), command_cur_frame))
            commands.append((int(x_one[0] + 1), command_next_frame))
        else:
            print("被隐藏的天键")
    return commands


# arc实体渲染
def arc_arc_render(args, arc_part, timings, song, x, y, color, scenecontrols):
    # 命令队列
    commands = []
    # 帧间隔毫秒
    x_s = position_infer(args, song, timings, arc_part)
    for x_one in x_s:
        # 位置推算完毕，开始绘制。
        hide = hide_group(args, int(x_one[0]), scenecontrols)
        if hide != 'True':
            start_x = x_one[1]
            start_y = get_y(args, y)
            start_z = get_z(args, x)

            command_base_x = "fill " + str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(start_z - 1)) + " " + \
                             str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(start_z + 1))
            command_base_y = "fill " + str(int(start_x)) + " " + str(int(start_y + 1)) + " " + str(int(start_z)) + " " + \
                             str(int(start_x)) + " " + str(int(start_y + 1)) + " " + str(int(start_z))
            command_centre = "fill " + str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(start_z)) + " " + \
                             str(int(start_x)) + " " + str(int(start_y)) + " " + str(int(start_z))
            if color == -1:
                # particle minecraft:dust 0.999 0 0 0.2 ~ ~1 ~ 0 0 0 10000 1 force
                command_cur_frame = "setblock " + str(int(start_x)) + " " + str(int(start_y)) + " " + str(
                    int(start_z)) + " " + args['black_line_material'] + " \n"
                commands.append((int(x_one[0]), command_cur_frame))
            elif color == -2:
                # command_particle = "particle minecraft:dust 0.533 0.533 0.776 0.8 " + str(start_x)[0:6] + " " + str(
                #     start_y)[0:6] + " " + str(start_z)[0:6] + " 0 0 0 100 1 force\n"
                command_particle = "particle minecraft:end_rod " + str(start_x)[0:6] + " " + str(
                    start_y)[0:6] + " " + str(start_z)[0:6] + " 0 0 0 999999 1 force\n"
                commands.append((int(x_one[0]), command_particle))
            elif color == 0:
                command_cur_frame_x = command_base_x + " " + args['blue_arc_material'] + " \n"
                commands.append((int(x_one[0]), command_cur_frame_x))
                command_cur_frame_y = command_base_y + " " + args['blue_arc_material'] + " \n"
                commands.append((int(x_one[0]), command_cur_frame_y))
                command_cur_frame_centre = command_centre + " " + args['blue_arc_centre_material'] + " \n"
                commands.append((int(x_one[0]), command_cur_frame_centre))
            elif color == 1:
                command_cur_frame_x = command_base_x + " " + args['red_arc_material'] + " \n"
                commands.append((int(x_one[0]), command_cur_frame_x))
                command_cur_frame_y = command_base_y + " " + args['red_arc_material'] + " \n"
                commands.append((int(x_one[0]), command_cur_frame_y))
                command_cur_frame_centre = command_centre + " " + args['red_arc_centre_material'] + " \n"
                commands.append((int(x_one[0]), command_cur_frame_centre))
            elif color == 2:
                command_cur_frame_x = command_base_x + " " + args['green_arc_material'] + " \n"
                commands.append((int(x_one[0]), command_cur_frame_x))
                command_cur_frame_y = command_base_y + " " + args['green_arc_material'] + " \n"
                commands.append((int(x_one[0]), command_cur_frame_y))
            # 填充空气
            if color == -1:
                command_cur_frame = "setblock " + str(int(start_x)) + " " + str(int(start_y)) + " " + str(
                    int(start_z)) + " " + args['air_material'] + " \n"
                commands.append((int(x_one[0] + 1), command_cur_frame))
            elif color in [0, 1, 2]:
                command_next_frame_x = command_base_x + " " + args['air_material'] + " \n"
                commands.append((int(x_one[0] + 1), command_next_frame_x))
                command_next_frame_y = command_base_y + " " + args['air_material'] + " \n"
                commands.append((int(x_one[0] + 1), command_next_frame_y))
    return commands


def arc_render(args, arc, timings, song, scenecontrols):
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
        else:
            print(arc)
            raise Exception("不支持的arc种类:" + arc['easing'])
        for _result in result:
            commands = commands + arctap_render(args, arctap, timings, song, _result[0], _result[1], scenecontrols)
    # 天键渲染完毕，开始渲染Arc
    # 确定渲染间隔
    frame_time = 1000 / args['tps']
    # 逐方块渲染
    if arc['skylineBoolean'] or len(arctaps) > 0:
        # 黑线
        if args['enable_blackline'] == 'False':
            print("跳过黑线绘制")
        else:
            print("正在绘制一条黑线")
            start_frame_time = arc['t1'] - arc['t1'] % frame_time
            # start_frame_time = arc['t1']
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
                else:
                    print(arc)
                    raise Exception("不支持的arc种类：" + arc['easing'])
                if args['blackline_mode'] == 'block':
                    for _result in results:
                        commands = commands + arc_arc_render(args, cur_time, timings, song, _result[0], _result[1], -1, scenecontrols)
                    cur_time += frame_time * args['tps'] / args['default_speed_per_second']
                elif args['blackline_mode'] == 'particle':
                    for _result in results:
                        commands = commands + arc_arc_render(args, cur_time, timings, song, _result[0], _result[1], -2, scenecontrols)
                    cur_time += frame_time * args['tps'] / args['default_speed_per_second'] / args['particle_dense']
                else:
                    raise Exception("不存在的黑线处理方法")
    else:  # arc
        print("正在绘制一条arc")
        start_frame_time = arc['t1'] - arc['t1'] % frame_time
        # start_frame_time = arc['t1']
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
                                                     arc['color'], scenecontrols)
            cur_time += frame_time * args['tps'] / args['default_speed_per_second']
    return commands


# def hold_part_render(args, hold_part, timings, song, lane, scenecontrols):
#     commands = []
#     poses = position_infer(args, song, timings, hold_part)
#     for i in range(len(poses)-1):
#         frame = poses[i][0]
#         hide = hide_group(args, int(frame), scenecontrols)
#         if hide != 'True':
#             x_low = poses[i][1]
#             x_high = poses[i+1][1]
#             y = args['ground_y']
#             start_z = args['ground_z'] + lane * args['ground_interval'] - 3
#             mid_z = args['ground_z'] + lane * args['ground_interval']
#             end_z = args['ground_z'] + lane * args['ground_interval'] + 3
#             command_base = "fill " + str(int(x_low)) + " " + str(int(y)) + " " + str(int(start_z)) + " " + \
#                            str(int(x_high)) + " " + str(int(y)) + " " + str(int(end_z))
#             command_cur_frame_1 = command_base + " " + args['hold_side_material'] + " \n"
#             command_cur_frame_2 = "fill " + str(int(x_low)) + " " + str(int(y)) + " " + str(int(mid_z)) + " " + \
#                                   str(int(x_high)) + " " + str(int(y)) + " " + str(int(mid_z)) + " " + \
#                                   args['hold_centre_material'] + "\n"
#             command_next_frame = command_base + " " + args['air_material'] + " \n"
#             commands.append((int(frame), command_cur_frame_1))
#             commands.append((int(frame), command_cur_frame_2))
#             commands.append((int(frame + 1), command_next_frame))
#     return commands
#
# def hold_render(args, hold, timings, song, scenecontrols):
#     # 命令队列
#     commands = []
#     # 确定渲染间隔
#     frame_time = 1000 / args['tps']
#     # start_frame_time = hold['t1'] - hold['t1'] % frame_time
#     start_frame_time = hold['t1']
#     cur_time = start_frame_time
#     # while cur_time < hold['t2']:
#     while cur_time < hold['t2']+frame_time:
#         commands = commands + hold_part_render(args, cur_time, timings, song, hold['lane'], scenecontrols)
#         cur_time += frame_time * args['tps'] / args['default_speed_per_second']
#     return commands

def hold_render(args, hold, timings, song, scenecontrols):
    commands = []
    x_front = position_infer(args, song, timings, hold['t1'])
    x_tail = position_infer(args, song, timings, hold['t2'])
    # 分离frame字段
    x_front_start_frames = x_front[-1][0]
    x_front_end_frames = x_front[0][0]
    x_tail_start_frames = x_tail[-1][0]
    x_tail_end_frames = x_tail[0][0]
    if len(scenecontrols)>0:
        print(scenecontrols)
    for x_frame in x_front:
        hide = hide_group(args, int(x_frame[0]), scenecontrols)
        if hide != 'True':
            min_x = 0
            max_x = 0
            min_z = 0
            max_z = 0
            cent_z = 0
            if x_frame[0] < x_tail_start_frames:
                min_x = x_frame[1]
                max_x = args['ground_x'] + args['track_x_upper_limit']
                min_z = get_track_z(args, hold['lane'])-3
                max_z = get_track_z(args, hold['lane'])+3
                cent_z = get_track_z(args, hold['lane'])
            elif x_frame[0]<=x_tail_end_frames:
                min_x = x_frame[1]
                max_x = 0
                for x_tail_frame in x_tail:
                    if x_tail_frame[0] == x_frame[0]:
                        max_x = x_tail_frame[1]
                        break
                min_z = get_track_z(args, hold['lane']) - 3
                max_z = get_track_z(args, hold['lane']) + 3
                cent_z = get_track_z(args, hold['lane'])
            else:
                raise Exception("没有预料到的hold编排")
            y = args['ground_y']
            command_cur_side = "fill "+str(int(min_x))+" "+str(int(y))+" "+str(int(min_z))+" "+str(int(max_x))+" "+str(int(y))+" "+str(int(max_z))+" "+args['hold_side_material']+"\n"
            command_next_side = "fill "+str(int(min_x))+" "+str(int(y))+" "+str(int(min_z))+" "+str(int(max_x))+" "+str(int(y))+" "+str(int(max_z))+" "+args['air_material']+"\n"
            command_cur_centre = "fill "+str(int(min_x))+" "+str(int(y))+" "+str(int(cent_z))+" "+str(int(max_x))+" "+str(int(y))+" "+str(int(cent_z))+" "+args['hold_centre_material']+"\n"
            command_next_centre = "fill "+str(int(min_x))+" "+str(int(y))+" "+str(int(cent_z))+" "+str(int(max_x))+" "+str(int(y))+" "+str(int(cent_z))+" "+args['air_material']+"\n"
            commands.append((x_frame[0], command_cur_side))
            commands.append((x_frame[0], command_cur_centre))
            commands.append((x_frame[0]+1, command_next_side))
            commands.append((x_frame[0]+1, command_next_centre))
    for x_frame in x_tail:
        hide = hide_group(args, x_frame[0], scenecontrols)
        if hide != 'True':
            min_x = 0
            max_x = 0
            min_z = 0
            max_z = 0
            cent_z = 0
            if x_frame[0] <= x_front_end_frames:
                continue
            elif x_frame[0] <= x_tail_end_frames:
                min_x = args['ground_x']
                max_x = x_frame[1]
                min_z = get_track_z(args, hold['lane']) - 3
                max_z = get_track_z(args, hold['lane']) + 3
                cent_z = get_track_z(args, hold['lane'])
            else:
                raise Exception("没有预料到的hold编排")
            y = args['ground_y']
            command_cur_side = "fill " + str(int(min_x)) + " " + str(int(y)) + " " + str(int(min_z)) + " " + str(
                int(max_x)) + " " + str(int(y)) + " " + str(int(max_z)) + " " + args['hold_side_material'] + "\n"
            command_next_side = "fill " + str(int(min_x)) + " " + str(int(y)) + " " + str(int(min_z)) + " " + str(
                int(max_x)) + " " + str(int(y)) + " " + str(int(max_z)) + " " + args['air_material'] + "\n"
            command_cur_centre = "fill " + str(int(min_x)) + " " + str(int(y)) + " " + str(int(cent_z)) + " " + str(
                int(max_x)) + " " + str(int(y)) + " " + str(int(cent_z)) + " " + args['hold_centre_material'] + "\n"
            command_next_centre = "fill " + str(int(min_x)) + " " + str(int(y)) + " " + str(int(cent_z)) + " " + str(
                int(max_x)) + " " + str(int(y)) + " " + str(int(cent_z)) + " " + args['air_material'] + "\n"
            commands.append((x_frame[0], command_cur_side))
            commands.append((x_frame[0], command_cur_centre))
            commands.append((x_frame[0] + 1, command_next_side))
            commands.append((x_frame[0] + 1, command_next_centre))
    if x_front_end_frames < x_tail_start_frames:
        for frame in range(x_front_end_frames, x_tail_start_frames):
            hide = hide_group(args, x_frame[0], scenecontrols)
            if hide != 'True':
                min_x = args['ground_x']
                max_x = args['ground_x'] + args['track_x_upper_limit']
                min_z = get_track_z(args, hold['lane']) - 3
                max_z = get_track_z(args, hold['lane']) + 3
                cent_z = get_track_z(args, hold['lane'])
                y = args['ground_y']
                command_cur_side = "fill " + str(int(min_x)) + " " + str(int(y)) + " " + str(int(min_z)) + " " + str(
                    int(max_x)) + " " + str(int(y)) + " " + str(int(max_z)) + " " + args['hold_side_material'] + "\n"
                command_next_side = "fill " + str(int(min_x)) + " " + str(int(y)) + " " + str(int(min_z)) + " " + str(
                    int(max_x)) + " " + str(int(y)) + " " + str(int(max_z)) + " " + args['air_material'] + "\n"
                command_cur_centre = "fill " + str(int(min_x)) + " " + str(int(y)) + " " + str(int(cent_z)) + " " + str(
                    int(max_x)) + " " + str(int(y)) + " " + str(int(cent_z)) + " " + args['hold_centre_material'] + "\n"
                command_next_centre = "fill " + str(int(min_x)) + " " + str(int(y)) + " " + str(int(cent_z)) + " " + str(
                    int(max_x)) + " " + str(int(y)) + " " + str(int(cent_z)) + " " + args['air_material'] + "\n"
                commands.append((frame, command_cur_side))
                commands.append((frame, command_cur_centre))
                commands.append((frame + 1, command_next_side))
                commands.append((frame + 1, command_next_centre))
    return commands

def arc_support_line_part_render(args, arc, song, timings,material):
    commands = []
    poses = position_infer(args, song, timings, arc['t1'])
    for pose in poses:
        frame = pose[0]
        x = pose[1]
        y = get_y(args, arc['y1'])
        z = get_z(args, arc['x1'])
        low_y = args['ground_y']
        command_cur = "fill "+str(int(x))+" "+ str(int(y))+" "+str(int(z))+" "+str(int(x))+" "+ str(int(low_y))+" "+str(int(z))+" "+ material+ "\n"
        command_next = "fill "+str(int(x))+" "+ str(int(y))+" "+str(int(z))+" "+str(int(x))+" "+ str(int(low_y))+" "+str(int(z))+" air\n"
        commands.append((frame, command_cur))
        commands.append((frame+1, command_next))
    return commands

def arc_support_line_group_render(args, arcs, song, timings,material):
    commands = []
    for i in range(len(arcs)):
        if i > 0 and arcs[i-1]['t2']==arcs[i]['t1'] and arcs[i-1]['x2']==arcs[i]['x1'] and arcs[i-1]['y2']==arcs[i]['y1'] and arcs[i]['y2']-arcs[i]['y1']>0.01:
            print("首尾相接但是有高度差别，需要处理")
            command = arc_support_line_part_render(args, arcs[i], song, timings, material)
            commands = commands + command
            continue
        elif i > 0 and arcs[i-1]['t2']==arcs[i]['t1'] and arcs[i-1]['x2']==arcs[i]['x1'] and arcs[i-1]['y2']==arcs[i]['y1'] and arcs[i]['y2']-arcs[i]['y1']<=0.01:
            print("首尾相接但是没有明显高差，无需处理")
            continue
        else:
            print("其他情况需要渲染")
            command = arc_support_line_part_render(args, arcs[i], song, timings, material)
            commands = commands + command
            continue
    return commands

def arc_support_line_render(args, arcs, song, timings):
    commands = []
    # arcs分类
    arcs.sort(key=lambda x: x['t1'])
    blue_arcs = []
    red_arcs = []
    green_arcs = []
    # 过滤黑线并分类
    for arc in arcs:
        if arc['skylineBoolean'] == False and arc['color'] == 0:
            blue_arcs.append(arc)
        elif arc['skylineBoolean'] == False and arc['color'] == 1:
            red_arcs.append(arc)
        elif arc['skylineBoolean'] == False and arc['color'] == 2:
            green_arcs.append(arc)
        elif arc['skylineBoolean'] == True:
            print("黑线不绘制支撑柱")
        else:
            raise Exception("不支持的arc类型")
    commands = commands + arc_support_line_group_render(args, blue_arcs, song, timings, args['blue_arc_support_material'])
    commands = commands + arc_support_line_group_render(args, red_arcs, song, timings, args['red_arc_support_material'])
    commands = commands + arc_support_line_group_render(args, green_arcs, song, timings, args['green_arc_support_material'])
    return commands



def get_y(args,y):
    return y * args['ground_interval'] * args['y_ratio'] + args['arc_raise']

def get_z(args,x):
    # 这里的x是谱面的x
    return args['ground_z'] + 1.5 * args['ground_interval'] + x * 2 * args['ground_interval'] + 0.5

def get_track_z(args,lane):
    return args['ground_z'] + lane * args['ground_interval']