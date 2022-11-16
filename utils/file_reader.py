import json
import os


def aff_file_reader(path):
    # Vars
    file_head_dict = {}
    file_head_flag = True
    main_timing_group_flag = True

    # Process Lines
    file = open(path, "r")
    timing_groups = []
    timing_group = []
    main_timing_group = []
    timing_groups_args = []
    for line in file:
        line = line.strip()
        if file_head_flag:
            if line[0] == '-':
                file_head_flag = False
            else:
                # print(line)
                segments = line.split(':')
                file_head_dict[segments[0]] = int(segments[1])
        else:
            # Not File Head
            if main_timing_group_flag:
                # In Main Timing Group
                if line.startswith('timinggroup'):
                    main_timing_group_flag = False
                    timing_groups_args.append(line[12:-2])
                else:
                    main_timing_group.append(line)
            else:
                # In Branch Timing Group
                if line.startswith('};'):
                    main_timing_group_flag = True
                    timing_groups.append(timing_group)
                    timing_group = []
                else:
                    timing_group.append(line)
    return file_head_dict, main_timing_group, timing_groups, timing_groups_args


def timing_group_parser(lines):
    timings = []
    notes = []
    holds = []
    arcs = []
    cameras = []
    scenecontrols = []
    t_max = 0

    for line in lines:
        line = line.strip()
        # Timings Line Process
        if line.startswith('timing('):
            temp_timings = {}
            segments = line[7:-2].split(',')
            temp_timings['t'] = float(segments[0])
            temp_timings['bpm'] = float(segments[1])
            temp_timings['beats'] = float(segments[2])
            timings.append(temp_timings)
            if t_max < temp_timings['t']:
                t_max = temp_timings['t']


        # Note Line Process
        elif line.startswith('('):
            temp_note = {}
            segments = line[1:-2].split(',')
            temp_note['t'] = int(segments[0])
            temp_note['lane'] = int(segments[1])
            notes.append(temp_note)
            if t_max < temp_note['t']:
                t_max = temp_note['t']

        # Hold Line Process
        elif line.startswith('hold('):
            temp_hold = {}
            segments = line[5:-2].split(',')
            temp_hold['t1'] = int(segments[0])  # 开始时间
            temp_hold['t2'] = int(segments[1])  # 结束时间
            temp_hold['lane'] = int(segments[2])
            holds.append(temp_hold)
            if t_max < temp_hold['t2']:
                t_max = temp_hold['t2']

        # Arc Line Process
        elif line.startswith('arc('):
            temp_arc = {}
            arctap_list = []
            if line[-2] == ']':
                arctaps = line[4:-2].replace('),arctap(', ',').split('[')[1][7:-1].split(',')
                for i in range(len(arctaps)):
                    arctap_list.append(int(arctaps[i]))
            segments = line[4:-2].split(',')
            temp_arc['t1'] = int(segments[0])
            temp_arc['t2'] = int(segments[1])
            temp_arc['x1'] = float(segments[2])
            temp_arc['x2'] = float(segments[3])
            temp_arc['easing'] = str(segments[4])
            temp_arc['y1'] = float(segments[5])
            temp_arc['y2'] = float(segments[6])
            temp_arc['color'] = int(segments[7])  # 0 = Blue,1 = Red,2 = Green
            temp_arc['FX'] = str(segments[8])
            if len(arctap_list)>0: # False = Arc True = BlackLine
                temp_arc['skylineBoolean'] = True
            elif segments[9]=='true':
                temp_arc['skylineBoolean'] = True
            else:
                temp_arc['skylineBoolean'] = False
            temp_arc['arctaps'] = arctap_list
            arcs.append(temp_arc)
            if t_max < temp_arc['t2']:
                t_max = temp_arc['t2']

        # Scene Control Line Process
        elif line.startswith('scenecontrol('):
            temp_scenecontrol = {}
            segments = line[13:-2].split(',')
            temp_scenecontrol['t'] = int(segments[0])
            temp_scenecontrol['type'] = str(segments[1])
            if len(segments) > 2:
                temp_scenecontrol['param1'] = float(segments[2])
                temp_scenecontrol['param2'] = int(segments[3])
            scenecontrols.append(temp_scenecontrol)
            if t_max < temp_scenecontrol['t']:
                t_max = temp_scenecontrol['t']

        # Camera Line Process
        elif line.startswith('camera('):
            temp_camera = {}
            # To Do
            cameras.append(temp_camera)

    return timings, notes, holds, arcs, cameras, scenecontrols, t_max


def json_reader(path: str):
    with open(path, 'r', encoding='utf8') as fp:
        json_data = json.load(fp)
        fp.close()
        return json_data


def process_directory(songlist):
    '''
    预处理文件夹，整理付费与免费曲目
    '''
    for song in songlist['songs']:
        if not os.path.isdir('./songs/' + song['id']):
            # Folder Not Exist
            os.rename('./songs/' + song['id'], './songs/' + song['id'] + 'base.ogg')
            os.mkdir('./songs/' + song['id'])
            os.rename('./songs/' + song['id'] + '_0', './songs/' + song['id'] + '/0.aff')
            os.rename('./songs/' + song['id'] + '_1', './songs/' + song['id'] + '/1.aff')
            os.rename('./songs/' + song['id'] + '_2', './songs/' + song['id'] + '/2.aff')
            os.rename('./songs/' + song['id'] + 'base.ogg', './songs/' + song['id'] + '/base.ogg')
            if os.path.exists('./songs/' + song['id'] + '_3'):
                os.rename('./songs/' + song['id'] + '_3', './songs/' + song['id'] + '/3.aff')
        else:
            # Folder Exist, Like Free Songs
            if os.path.exists('./songs/' + song['id'] + '_3'):
                os.rename('./songs/' + song['id'] + '_3', './songs/' + song['id'] + '/3.aff')
            # Byd Music Differs
            if os.path.exists('./songs/' + song['id'] + '_audio_3'):
                os.rename('./songs/' + song['id'] + '_audio_3', './songs/' + song['id'] + '/byd.ogg')
