def group_by_frame(commands, args):
    groups = []
    # 新建空白帧
    frame_time = 1000 / args['tps']
    cur_time = 0
    while cur_time < args['t_max'] + args['end_time']:
        groups.append([])
        cur_time += frame_time
    # 正式向帧写入语句
    print("正在写入谱面文件")
    for command in commands:
        # print(command)
        groups[command[0]].append(command[1])
    for index in range(len(groups)):
        groups[index] = order_by_operation(groups[index], args)
    return groups


def order_by_operation(commands, args):
    # 整理命令渲染优先级 air<黑线<绿支撑柱<红支撑柱<蓝支撑柱<绿arc<红arc<蓝arc<天键<hold<地键<轨道
    airs = []
    black_lines = []
    red_arcs = []
    red_arc_centres = []
    blue_arcs = []
    blue_arc_centres = []
    sky_notes = []
    notes = []
    holds = []
    green_arcs = []
    tracks = []
    red_arcs_supports = []
    blue_arcs_supports = []
    green_arcs_supports = []
    extend_tracks = []
    for command in commands:
        line = command.strip()
        if line[-len(args['note_material']):] == args['note_material']:
            notes.append(command)
        elif line[-len(args['hold_side_material']):] == args['hold_side_material']:
            holds.append(command)
        elif line[-len(args['hold_centre_material']):] == args['hold_centre_material']:
            holds.append(command)
        elif line[-len(args['air_material']):] == args['air_material']:
            airs.append(command)
        elif line[-len(args['blue_arc_material']):] == args['blue_arc_material']:
            blue_arcs.append(command)
        elif line[-len(args['black_line_materials']):] == args['black_line_materials']:
            black_lines.append(command)
        elif line[-len(args['red_arc_material']):] == args['red_arc_material']:
            red_arcs.append(command)
        elif line[-len(args['green_arc_material']):] == args['green_arc_material']:
            green_arcs.append(command)
        elif line[-len(args['arctap_material']):] == args['arctap_material']:
            sky_notes.append(command)
        elif line[-len(args['red_arc_centre_material']):] == args['red_arc_centre_material']:
            red_arc_centres.append(command)
        elif line[-len(args['blue_arc_centre_material']):] == args['blue_arc_centre_material']:
            blue_arc_centres.append(command)
        elif line[-len(args['extend_track_center_material']):] == args['extend_track_center_material']:
            extend_tracks.append(command)
        elif line[-len(args['extend_track_slide_material']):] == args['extend_track_slide_material']:
            extend_tracks.append(command)
        elif line[-len(args['blue_arc_support_material']):] == args['blue_arc_support_material']:
            blue_arcs_supports.append(command)
        elif line[-len(args['red_arc_support_material']):] == args['red_arc_support_material']:
            red_arcs_supports.append(command)
        elif line[-len(args['green_arc_support_material']):] == args['green_arc_support_material']:
            green_arcs_supports.append(command)
        elif line[0:8] == "particle":
            black_lines.append(command)
        elif line[-4:] == "keep":
            tracks.append(command)
        else:
            print(command)
            raise Exception("未经分类的材质，请检查渲染时用的方块")
    sorted_commands = airs + black_lines + green_arcs_supports + red_arcs_supports + blue_arcs_supports + green_arcs + \
                      red_arcs + blue_arcs + red_arc_centres + blue_arc_centres + sky_notes + holds + notes + tracks + \
                      extend_tracks
    # print("空气填充命令行数："+str(len(airs)))
    # print("黑线命令行数："+str(len(black_lines)))
    # print("绿蛇支撑线填充命令行数："+str(len(green_arcs_supports)))
    # print("红蛇支撑线填充命令行数："+str(len(red_arcs_supports)))
    # print("蓝蛇支撑线填充命令行数："+str(len(blue_arcs_supports)))
    # print("绿蛇边框填充命令行数："+str(len(green_arcs)))
    # print("红蛇边框填充命令行数："+str(len(red_arcs)))
    # print("蓝蛇边框填充命令行数："+str(len(blue_arcs)))
    # print("红蛇夹心填充命令行数："+str(len(red_arc_centres)))
    # print("蓝蛇夹心填充命令行数："+str(len(blue_arc_centres)))
    # print("天键填充命令行数："+str(len(sky_notes)))
    # print("长条填充命令行数："+str(len(holds)))
    # print("Note填充命令行数："+str(len(notes)))
    # print("轨道填充命令行数："+str(len(tracks)))
    # print("外侧轨道填充命令行数："+str(len(extend_tracks)))
    return sorted_commands


def write(commands, args, path, prefix):
    groups = group_by_frame(commands, args)
    # 写入调度器
    scheduler_path = path + "/" + prefix + "_scheduler.mcfunction"
    scheduler = open(scheduler_path, "w")
    for i in range(len(groups)):
        # 写入每帧文件
        final_path = path + "/" + prefix + "_" + str(i) + ".mcfunction"
        f = open(final_path, "w")
        for command in groups[i]:
            f.write(command)
        scheduler.write("schedule function minearcaea:" + prefix + "_" + str(i) + " " + str(i) + "t \n")
        f.close()
    scheduler.close()
