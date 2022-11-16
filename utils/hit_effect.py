import cv2
import os
import PIL
from PIL import Image,ImageDraw,ImageFont
import numpy as np
import pygame
from utils.arcs import arc_s, arc_b, arc_si, arc_so, arc_siso, arc_sosi, arc_sisi, arc_soso, arc_zero



class generate_hit_effect(object):
    def __init__(self):
        self.note_read_flag = False
        self.note_effect_np_img = 0
        # 素材大小均为1024*1024，note打击用"note_"开头的素材，hold和arc用"particle_arc"，判定文字统一用"hit_"开头的东西
        self.note_type = ['colorless', 'conflict', 'light', 'mirai_conflict', 'mirai_light']

    def generate_note_effect_executor(self, args, frame, x, y):
        commands = []
        if not args['hit_effect_type'] in self.note_type:
            print("仅可使用note打击效果['colorless', 'conflict', 'light', 'mirai_conflict', 'mirai_light']")
            raise Exception("未定义的note渲染效果："+str(args['hit_effect_type']))
        if self.note_read_flag == False:
            # 读取素材
            # print(os.getcwd())
            path = args['hit_effect_path']+"note_"+args['hit_effect_type']+".png"
            # path = args['hit_effect_path']+"hit_pure.png"
            # print(path)
            # note_effect_img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            # note_effect_img = note_effect_img[:,:,[0,1,2,3]]
            note_effect_img = PIL.Image.open(path)
            # print(note_effect_img)
            # note_effect_img.show()
            self.note_effect_np_img = np.asarray(note_effect_img)
            self.note_read_flag = True

        for i in range(0, 4):
            for j in range(0, 4):
                x_min = i*256
                x_max = (i+1)*256-1
                y_min = j*256
                y_max = (j+1)*256-1
                temp_img_part = self.note_effect_np_img[x_min:x_max,y_min:y_max]
                for k in range(0, 255, args['hit_effect_sample_stride']):
                    for l in range(0, 255, args['hit_effect_sample_stride']):
                        if temp_img_part[k,l,0]>args['hit_effect_allow_mistake_per_channel'] and temp_img_part[k,l,1]>args['hit_effect_allow_mistake_per_channel'] and temp_img_part[k,l,2]>args['hit_effect_allow_mistake_per_channel']:
                            continue
                        else:
                            delta_x = (k-128)/args['hit_effect_scale']
                            delta_y = (l-128)/args['hit_effect_scale']
                            final_x = x+delta_x
                            final_y = y+delta_y
                            command_z = self.get_z(args,final_x)
                            command_y = self.get_y(args,final_y)
                            command_x = args['ground_x'] + 0.5
                            color_r = round(temp_img_part[k,l,0] / 255, 5)
                            color_g = round(temp_img_part[k,l,1] / 255, 5)
                            color_b = round(temp_img_part[k,l,2] / 255, 5)
                            command = "particle minecraft:dust "+ str(color_r)[0:6] +" "+ str(color_g)[0:6] + " " + str(color_b)[0:6] +" "+ str(args['hit_effect_particle_size']) +" " + str(command_x)[0:6] + " " + str(command_y)[0:6] + " " + str(command_z)[0:6] + " 0 0 0 100 1 force\n"
                            commands.append((frame,command))
                frame += 1
        return commands

    def note_hit_generate(self, args, note,timing_group_args):
        commands = []
        if timing_group_args == "noinput":
            return commands
        x = args['ground_x'] - 0.5
        y_effect = args['ground_y'] + 1
        y_text = args['ground_y'] + args['hit_effect_text_rise']+1
        z = self.get_track_z(args, note['lane'])
        frame = int(note['t'] * args['tps'] / 1000)
        # commands = self.generate_note_effect_executor(args, frame, z, y_effect)
        command_effect = "particle minecraft:explosion "+str(x)+" "+str(y_effect)+" "+str(z)+" 0 0 0 0 1 force\n"
        command_text = "particle minecraft:sweep_attack "+str(x)+" "+str(y_text)+" "+str(z)+" 0 0 0 0 1 force\n"
        commands.append((frame, command_effect))
        commands.append((frame, command_text))
        return commands

    def hold_hit_generate(self, args, hold, timings,timing_group_args):
        commands = []
        if timing_group_args == "noinput":
            return commands
        x = args['ground_x'] - 0.5
        y_effect = args['ground_y'] + 1
        y_text = args['ground_y'] + args['hit_effect_text_rise'] + 1
        z = self.get_track_z(args, hold['lane'])
        temp_time = hold['t1']
        timing = self.get_start_timing(hold['t1'], timings)
        while temp_time<hold['t2']:
            frame = int(temp_time * args['tps'] / 1000)
            # commands = self.generate_note_effect_executor(args, frame, z, y_effect)
            # command_effect = "particle minecraft:explosion " + str(x) + " " + str(y_effect) + " " + str(
            #     z) + " 0 0 0 0 1 force\n"
            command_text = "particle minecraft:sweep_attack " + str(x) + " " + str(y_text) + " " + str(
                z) + " 0 0 0 0 1 force\n"
            # commands.append((frame, command_effect))
            commands.append((frame, command_text))
            temp_time+=30000/timing['bpm']
        # 常驻的星芒特效：
        temp_t = hold['t1']
        while temp_t < hold['t2']:
            # "particle minecraft:soul ~ ~1 ~ 0 0 0 0 1 force"
            command_effect = "particle minecraft:soul " + str(x) + " " + str(y_effect) + " " + str(
                 z) + " 0 0 0 0 1 force\n"
            frame = int(temp_t * args['tps'] / 1000)
            commands.append((frame, command_effect))
            temp_t += 1000 / args['tps']
        return commands


    def arc_hit_generate(self, args, arc, timings,timing_group_args):
        commands = []
        if timing_group_args == "noinput":
            return commands
        x = args['ground_x']+ 0.5
        temp_time = arc['t1']
        timing = self.get_start_timing(arc['t1'],timings)
        if arc['skylineBoolean'] == False and len(arc['arctaps']) == 0:
            while temp_time<arc['t2']:
                if arc['easing'] == 's':
                    result = arc_s(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_time)
                elif arc['easing'] == 'b':
                    result = arc_b(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_time)
                elif arc['easing'] == 'si':
                    result = arc_si(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_time)
                elif arc['easing'] == 'so':
                    result = arc_so(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_time)
                elif arc['easing'] == 'sisi':
                    result = arc_sisi(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_time)
                elif arc['easing'] == 'siso':
                    result = arc_siso(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_time)
                elif arc['easing'] == 'sosi':
                    result = arc_sosi(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_time)
                elif arc['easing'] == 'soso':
                    result = arc_soso(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_time)
                else:
                    print(arc)
                    raise Exception("不支持的arc种类:" + arc['easing'])
                # for _result in result:
                result = result[0]
                x = args['ground_x'] - 0.5
                y_effect = self.get_y(args, result[1])+1
                y_text = self.get_y(args, result[1]) + args['hit_effect_text_rise']+1
                z = self.get_z(args, result[0])
                command_text = "particle minecraft:sweep_attack " + str(x) + " " + str(y_text) + " " + str(
                    z) + " 0 0 0 0 1 force\n"
                frame = int(temp_time * args['tps'] / 1000)
                # commands.append((frame, command_effect))
                commands.append((frame, command_text))
                temp_time+=30000/timing['bpm']

            # 处理常驻星芒特效
            temp_t = arc['t1']
            while temp_t < arc['t2']:
                # "particle minecraft:soul ~ ~1 ~ 0 0 0 0 1 force"
                if arc['easing'] == 's':
                    result = arc_s(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_t)
                elif arc['easing'] == 'b':
                    result = arc_b(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_t)
                elif arc['easing'] == 'si':
                    result = arc_si(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_t)
                elif arc['easing'] == 'so':
                    result = arc_so(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_t)
                elif arc['easing'] == 'sisi':
                    result = arc_sisi(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_t)
                elif arc['easing'] == 'siso':
                    result = arc_siso(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_t)
                elif arc['easing'] == 'sosi':
                    result = arc_sosi(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_t)
                elif arc['easing'] == 'soso':
                    result = arc_soso(arc['t1'], arc['t2'], arc['x1'], arc['x2'], arc['y1'], arc['y2'], temp_t)
                else:
                    print(arc)
                    raise Exception("不支持的arc种类:" + arc['easing'])
                result = result[0]
                x = args['ground_x'] - 0.5
                y_effect = self.get_y(args, result[1]) + 1
                z = self.get_z(args, result[0])
                command_effect = "particle minecraft:soul " + str(x) + " " + str(y_effect) + " " + str(
                    z) + " 0 0 0 0 1 force\n"
                frame = int(temp_t * args['tps'] / 1000)
                commands.append((frame, command_effect))
                temp_t += 1000 / args['tps']

        # 处理arctap
        for arctap in arc['arctaps']:
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
            result = result[0]
            x = args['ground_x']
            y_effect = self.get_y(args, result[1]) + 1
            y_text = self.get_y(args, result[1]) + args['hit_effect_text_rise'] + 1
            z = self.get_z(args, result[0])
            command_effect = "particle minecraft:explosion " + str(x) + " " + str(y_effect) + " " + str(
                z) + " 0 0 0 0 1 force\n"
            command_text = "particle minecraft:sweep_attack " + str(x) + " " + str(y_text) + " " + str(
                z) + " 0 0 0 0 1 force\n"
            frame = int(arctap * args['tps'] / 1000)
            commands.append((frame, command_effect))
            commands.append((frame, command_text))

        return commands



    def get_y(self, args, y):
        return y * args['ground_interval'] * args['y_ratio'] + args['arc_raise']

    def get_z(self, args, x):
        # 这里的x是谱面的x
        return args['ground_z'] + 1.5 * args['ground_interval'] + x * 2 * args['ground_interval'] + 0.5

    def get_track_z(self, args, lane):
        return args['ground_z'] + lane * args['ground_interval']

    def get_start_timing(self, time,timings):
        for i in range(len(timings)):
            if time<timings[i]['t']:
                if i>0:
                    return timings[i-1]
                else:
                    return timings[0]
        return timings[-1]

    def text_generator(self, args, text, ttf):
        1

if __name__ == "__main__":
    args = {}
    args['hit_effect_path'] = '../hit_effect/'
    args['hit_effect_type'] = 'colorless'
    effect_generator = generate_hit_effect()
    effect_generator.generate_hit_effect(args, 0, 0, 0)