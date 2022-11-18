import os
from utils.file_reader import aff_file_reader, timing_group_parser
from utils.file_writer import write
from utils.render_xp import note_render, hold_render, arc_render, sky_ground_double_key_line_render, \
    scenecontrols_render, sky_input, arc_support_line_render
from utils.hit_effect import generate_hit_effect

tps = 40
effect_controler = generate_hit_effect()

def get_args():
    args = {}

    # 演出全局设置
    args['pi'] = 3.1415926
    args['tps'] = tps
    # 每秒音符移动格子数量
    args['default_speed_per_second'] = 200
    # 轨道基准位置：0轨正中心上面1格坐标
    args['ground_x'] = 1
    args['ground_y'] = 1
    args['ground_z'] = -20
    # 轨道间距，影响地键、长条、天键、4k->6k的宽度
    args['ground_interval'] = 8
    # 向轨道正/负方向推算距离，即渲染范围
    args['track_x_upper_limit'] = 150
    args['track_x_lower_limit'] = -10
    # 0时长arc播放密度，越高越不会断掉
    args['zero_time_arc_play_dense'] = 20
    # 最后一个音符结束后继续播放多久，毫秒，没啥大用
    args['end_time'] = 5000
    # Arc及天键抬高高度（格）
    args['arc_raise'] = 3
    # 黑线粒子密度:每格多少个黑线粒子
    args['particle_dense'] = 0.4
    # 是否开启黑线
    args['enable_blackline'] = 'True'
    # 黑线渲染为方块即'block', 渲染为粒子即'particle'
    args['blackline_mode'] = 'particle'
    # 天键高度相当于多少倍地面轨道
    args['y_ratio'] = 1.2
    args['black_line_material'] = 'light_gray_stained_glass'
    # 材料，填写setblock/fill时所用的方块
    args['note_material'] = 'sea_lantern'
    args['air_material'] = 'air'
    args['arctap_material'] = 'pearlescent_froglight'
    args['red_arc_material'] = 'pink_stained_glass'
    args['red_arc_centre_material'] = 'glowstone'
    args['blue_arc_material'] = 'blue_stained_glass'
    args['blue_arc_centre_material'] = 'sea_lantern'
    args['green_arc_material'] = 'lime_stained_glass'
    args['hold_side_material'] = 'light_blue_concrete'
    args['hold_centre_material'] = 'sea_lantern'
    # 双押线密度，每几格渲染一个双押线粒子
    args['sky_ground_double_key_line_dense'] = 0.5
    # 额外轨道材质，4k转6k时会用得到
    args['extend_track_center_material'] = 'white_stained_glass'
    args['extend_track_slide_material'] = 'light_gray_stained_glass'
    # skyinput升高系数，4k转6k时会用到
    args['enwidencamera_y_increase_ratio'] = 1.61
    # 天线particle指令的长度以及密度
    args['sky_input_particle_length'] = 5
    args['sky_input_particle_dense'] = 40
    # 打击效果，已经弃用
    args['hit_effect_path'] = './hit_effect/'
    args['hit_effect_type'] = 'colorless'
    args['hit_effect_text_rise'] = 1.0 # 文字相对判定点升高多少格
    args['hit_effect_sample_stride'] = 5 # 间隔多少像素采样一个
    args['hit_effect_particle_size'] = 2 # 粒子的大小
    args['hit_effect_scale'] = 128 # 多少像素塞进一格
    args['hit_effect_allow_mistake_per_channel'] = 250 # 颜色容差，三个通道均大于这个数的像素会被忽略
    # 从打击效果到这里的的参数都没有用
    # arc支撑的材料
    args['blue_arc_support_material'] = 'blue_stained_glass_pane'
    args['red_arc_support_material'] = 'pink_stained_glass_pane'
    args['green_arc_support_material'] = 'lime_stained_glass_pane'
    return args

def convert_timing_group(args, song, timing_group, timing_group_args):
    timings, notes, holds, arcs, cameras, scenecontrols, t_max = timing_group_parser(timing_group)
    args['t_max'] = t_max

    commands = []
    print("正在绘制双押线")
    double_key_line_command = sky_ground_double_key_line_render(args, song, timings, notes, arcs, timing_group_args)
    commands = commands + double_key_line_command
    print("生成了" + str(len(double_key_line_command)) + "条双押命令")
    print("双押线绘制完毕")
    print("正在绘制note")
    for note in notes:
        note_commands = note_render(args, note, timings, song, scenecontrols)
        commands = commands + note_commands
    print("note绘制完毕")
    print("正在绘制hold")
    for hold in holds:
        hold_commands = hold_render(args, hold, timings, song, scenecontrols)
        commands = commands + hold_commands
    print("hold绘制完毕")
    print("正在绘制arc")
    for arc in arcs:
        arc_commands = arc_render(args, arc, timings, song, scenecontrols)
        commands = commands + arc_commands
    print("arcs绘制完毕")
    print("正在绘制arc的支撑线")
    arc_support_line_commands = arc_support_line_render(args,arcs,song,timings)
    commands = commands + arc_support_line_commands
    print("arc的支撑线绘制完毕")
    print("正在绘制场景控制")
    scene_commands = scenecontrols_render(args,scenecontrols)
    commands = commands + scene_commands
    print("场景控制绘制完毕")
    print("绘制打击特效")
    for note in notes:
        note_effect_commands = effect_controler.note_hit_generate(args,note,timing_group_args)
        commands = commands + note_effect_commands
    for arc in arcs:
        arc_effect_commands = effect_controler.arc_hit_generate(args, arc, timings,timing_group_args)
        commands = commands + arc_effect_commands
    for hold in holds:
        hold_effect_commands = effect_controler.hold_hit_generate(args, hold, timings, timing_group_args)
        commands = commands + hold_effect_commands
    print("打击特效绘制完毕")

    return commands, t_max


def convert(song, difficulty, path, prefix):
    folder_path = './songs/' + song['id']
    if not os.path.exists(folder_path):
        print("歌曲文件夹不存在")
        raise FileNotFoundError
    aff_path = folder_path + '/' + str(difficulty) + '.aff'
    if not os.path.exists(aff_path):
        print("该难度谱面文件不存在")
        raise FileNotFoundError
    # 通过解析aff文件得到以下参数
    # file_head_dict的最主要参数为file_head_dict['AudioOffset']
    # main_timing_group为默认timing group，类型为List(str)，timing_groups为其他若干timing group，timing_groups_args为对应参数
    file_head_dict, main_timing_group, timing_groups, timing_groups_args = aff_file_reader(aff_path)
    commands = []
    args = get_args()
    t_max = 0

    # 分timinggroup渲染
    for index in range(len(timing_groups)):
        print("正在渲染一个额外timing group")
        one_commands, one_t_max = convert_timing_group(args, song, timing_groups[index], timing_groups_args[index])
        commands = commands + one_commands
        if one_t_max > t_max:
            t_max = one_t_max
        print("该额外timing group渲染完毕")
    print("正在渲染主timing")
    main_commands, t_max_main = convert_timing_group(args, song, main_timing_group, "main")
    print("主timing渲染完毕")
    if t_max_main > t_max:
        t_max = t_max_main
    commands = commands + main_commands

    args['t_max'] = t_max + args['end_time']

    # 全局渲染
    print("正在渲染Sky Input")
    sky_input_scene_ctrls = []
    timings, notes, holds, arcs, cameras, scenecontrols, t_max = timing_group_parser(main_timing_group)
    sky_input_scene_ctrls = sky_input_scene_ctrls + scenecontrols
    for timing_group in timing_groups:
        timings, notes, holds, arcs, cameras, scenecontrols, t_max = timing_group_parser(timing_group)
        sky_input_scene_ctrls = sky_input_scene_ctrls + scenecontrols
    sky_input_command = sky_input(args, sky_input_scene_ctrls)
    commands = commands + sky_input_command
    print("Sky Input渲染完毕")

    print("共计"+str(len(commands))+"条指令")

    write(commands, args, path, prefix)

